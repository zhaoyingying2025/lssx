"""错题本蓝图

提供错题本的浏览、筛选、手动添加、标记掌握、笔记、删除、
PDF导出、从刷题记录自动收录、复习列表等功能。

所有路由均需登录（@login_required）。
"""
import io
import os
import json
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, send_file, current_app

from app import db
from app.models import WrongQuestion, Quiz, QuizAnswer, QuizAttempt
from app.utils.auth_helpers import login_required, get_current_user
from app.utils.achievement_service import record_wrong_mastered

wrong_book_bp = Blueprint('wrong_book', __name__)


# 题型 / 难度中文名映射（与 quiz.py 保持一致）
QUESTION_TYPE_CN = {
    'choice': '选择题',
    'fill': '填空题',
    'calc': '计算题',
    'proof': '证明题',
    'true_false': '判断题',
    'short_answer': '简答题',
}

DIFFICULTY_CN = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难',
}

# 艾宾浩斯遗忘曲线复习间隔（天）
# 第1次：1天 / 第2次：3天 / 第3次：7天 / 第4次：15天 / 第5次：30天
REVIEW_INTERVALS_DAYS = [1, 3, 7, 15, 30]


def compute_next_review(wrong_count):
    """根据累计答错次数计算下次复习时间。

    wrong_count 为当前已答错次数（含本次）。第 n 次复习间隔取 REVIEW_INTERVALS_DAYS[n-1]，
    超出列表则取最后一个间隔（30天）。
    """
    if wrong_count <= 0:
        idx = 0
    elif wrong_count > len(REVIEW_INTERVALS_DAYS):
        idx = len(REVIEW_INTERVALS_DAYS) - 1
    else:
        idx = wrong_count - 1
    days = REVIEW_INTERVALS_DAYS[idx]
    return datetime.utcnow() + timedelta(days=days)


def add_or_update_wrong_question(user_id, quiz_id, user_answer, correct_answer=None):
    """收录一道错题到错题本。

    若该用户该题已存在错题记录：wrong_count +1，更新 user_answer，
    并根据新的 wrong_count 重新计算 next_review（重置复习节奏）。
    若不存在：新建记录，wrong_count=1，next_review=今天+1天。

    若该题此前被标记为已掌握，再次答错则取消已掌握状态，重新纳入复习。
    返回 (WrongQuestion, created) 元组，created 表示是否新建。
    """
    wq = WrongQuestion.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()

    if wq is not None:
        wq.wrong_count = (wq.wrong_count or 0) + 1
        wq.user_answer = user_answer
        if correct_answer:
            wq.correct_answer = correct_answer
        # 再次答错，重新纳入复习节奏
        wq.is_mastered = False
        wq.last_reviewed = datetime.utcnow()
        wq.next_review = compute_next_review(wq.wrong_count)
        db.session.add(wq)
        return wq, False

    # 取题目信息补充章节/标签
    quiz = Quiz.query.get(quiz_id) if quiz_id else None
    if correct_answer is None and quiz is not None:
        correct_answer = quiz.answer

    wq = WrongQuestion(
        user_id=user_id,
        quiz_id=quiz_id,
        user_answer=user_answer,
        correct_answer=correct_answer,
        wrong_count=1,
        is_mastered=False,
        tags=(quiz.tags if quiz else None),
        chapter=(quiz.chapter if quiz else None),
        added_at=datetime.utcnow(),
        last_reviewed=datetime.utcnow(),
        next_review=compute_next_review(1),
    )
    db.session.add(wq)
    return wq, True


def _serialize_wrong_question(wq, quiz=None):
    """序列化错题记录为前端可用的字典。"""
    if quiz is None:
        quiz = Quiz.query.get(wq.quiz_id)
    now = datetime.utcnow()
    need_review = (not wq.is_mastered) and (wq.next_review is None or wq.next_review <= now)
    return {
        'id': wq.id,
        'quiz_id': wq.quiz_id,
        'user_answer': wq.user_answer or '',
        'correct_answer': wq.correct_answer or (quiz.answer if quiz else ''),
        'answer_cn': quiz.answer_cn if quiz else '',
        'wrong_count': wq.wrong_count or 1,
        'is_mastered': bool(wq.is_mastered),
        'note': wq.note or '',
        'tags': wq.tags or '',
        'chapter': wq.chapter or '',
        'added_at': wq.added_at.isoformat() if wq.added_at else None,
        'last_reviewed': wq.last_reviewed.isoformat() if wq.last_reviewed else None,
        'next_review': wq.next_review.isoformat() if wq.next_review else None,
        'need_review': need_review,
        # 关联题目信息
        'question_text': quiz.question_text if quiz else '(题目已删除)',
        'question_type': quiz.question_type if quiz else '',
        'question_type_cn': QUESTION_TYPE_CN.get(quiz.question_type, quiz.question_type) if quiz else '',
        'difficulty': quiz.difficulty if quiz else '',
        'difficulty_cn': DIFFICULTY_CN.get(quiz.difficulty, quiz.difficulty) if quiz else '',
        'section': quiz.section if quiz else '',
        'options': quiz.options if quiz else '',
    }


@wrong_book_bp.route('/')
@login_required
def index():
    """错题本主页面"""
    user = get_current_user()

    # 章节下拉数据
    chapters = sorted({wq.chapter for wq in
                       WrongQuestion.query.filter_by(user_id=user.id)
                       .filter(WrongQuestion.chapter != None)
                       .filter(WrongQuestion.chapter != '').all()
                       if wq.chapter})

    # 标签下拉数据
    tag_set = set()
    for row in WrongQuestion.query.filter_by(user_id=user.id).with_entities(WrongQuestion.tags).distinct():
        if row and row[0]:
            for t in row[0].split(','):
                t = t.strip()
                if t:
                    tag_set.add(t)
    all_tags = sorted(tag_set)

    return render_template('wrong_book.html', chapters=chapters, all_tags=all_tags)


@wrong_book_bp.route('/api/list')
@login_required
def api_list():
    """获取错题列表，支持筛选：chapter, tags, is_mastered, need_review"""
    user = get_current_user()
    chapter = request.args.get('chapter', '').strip()
    tag = request.args.get('tags', '').strip()
    is_mastered = request.args.get('is_mastered', '').strip()
    need_review = request.args.get('need_review', '').strip()

    query = WrongQuestion.query.filter_by(user_id=user.id)
    if chapter:
        query = query.filter(WrongQuestion.chapter == chapter)
    if tag:
        query = query.filter(WrongQuestion.tags.like(f'%{tag}%'))
    if is_mastered == 'true':
        query = query.filter(WrongQuestion.is_mastered == True)
    elif is_mastered == 'false':
        query = query.filter(WrongQuestion.is_mastered == False)
    if need_review == 'true':
        now = datetime.utcnow()
        query = query.filter(
            WrongQuestion.is_mastered == False,
            db.or_(WrongQuestion.next_review == None, WrongQuestion.next_review <= now)
        )

    items = query.order_by(WrongQuestion.added_at.desc()).all()

    # 批量获取关联题目
    quiz_ids = [wq.quiz_id for wq in items]
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all() if quiz_ids else []
    quiz_map = {q.id: q for q in quizzes}

    return jsonify({
        'success': True,
        'total': len(items),
        'items': [_serialize_wrong_question(wq, quiz_map.get(wq.quiz_id)) for wq in items],
    })


@wrong_book_bp.route('/api/add', methods=['POST'])
@login_required
def api_add():
    """手动添加错题。

    支持两种方式：
    1. 从题库选择：提供 quiz_id + user_answer
    2. 直接输入：提供 question_text + correct_answer (+ user_answer, chapter, tags)
       直接输入会在 Quiz 表中创建一道新题目，再收录到错题本。
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    quiz_id = data.get('quiz_id')
    user_answer = (data.get('user_answer') or '').strip()
    correct_answer = (data.get('correct_answer') or '').strip()

    if quiz_id:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'success': False, 'message': '题目不存在'}), 404
        wq, created = add_or_update_wrong_question(
            user.id, quiz.id, user_answer, correct_answer=correct_answer or quiz.answer
        )
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '错题已添加' if created else '错题已存在，答错次数已更新',
            'created': created,
            'id': wq.id,
        })

    # 直接输入新题目
    question_text = (data.get('question_text') or '').strip()
    if not question_text:
        return jsonify({'success': False, 'message': '题目内容不能为空'}), 400
    if not correct_answer:
        return jsonify({'success': False, 'message': '正确答案不能为空'}), 400

    chapter = (data.get('chapter') or '').strip()
    tags = (data.get('tags') or '').strip()
    question_type = data.get('question_type', 'short_answer')
    difficulty = data.get('difficulty', 'medium')

    max_num = db.session.query(db.func.max(Quiz.question_number)).filter_by(chapter=chapter).scalar() or 0
    quiz = Quiz(
        chapter=chapter,
        question_number=max_num + 1,
        question_text=question_text,
        question_type=question_type,
        answer=correct_answer,
        difficulty=difficulty,
        tags=tags,
    )
    db.session.add(quiz)
    db.session.flush()  # 取得 quiz.id

    wq, created = add_or_update_wrong_question(
        user.id, quiz.id, user_answer, correct_answer=correct_answer
    )
    db.session.commit()
    return jsonify({
        'success': True,
        'message': '错题已添加',
        'created': True,
        'id': wq.id,
    })


@wrong_book_bp.route('/api/<int:wq_id>/mastered', methods=['POST'])
@login_required
def api_mark_mastered(wq_id):
    """标记为已掌握（移出错题本复习队列）"""
    user = get_current_user()
    wq = WrongQuestion.query.get(wq_id)
    if not wq or wq.user_id != user.id:
        return jsonify({'success': False, 'message': '错题不存在'}), 404

    wq.is_mastered = True
    wq.last_reviewed = datetime.utcnow()
    db.session.commit()

    try:
        record_wrong_mastered(user.id)
    except Exception:
        pass

    return jsonify({'success': True, 'message': '已标记为已掌握'})


@wrong_book_bp.route('/api/<int:wq_id>/unmastered', methods=['POST'])
@login_required
def api_mark_unmastered(wq_id):
    """取消已掌握，重新纳入复习队列"""
    user = get_current_user()
    wq = WrongQuestion.query.get(wq_id)
    if not wq or wq.user_id != user.id:
        return jsonify({'success': False, 'message': '错题不存在'}), 404

    wq.is_mastered = False
    wq.last_reviewed = datetime.utcnow()
    # 取消掌握后，从当前 wrong_count 重新安排下次复习
    wq.next_review = compute_next_review(wq.wrong_count or 1)
    db.session.commit()
    return jsonify({'success': True, 'message': '已重新纳入复习'})


@wrong_book_bp.route('/api/<int:wq_id>/note', methods=['POST'])
@login_required
def api_update_note(wq_id):
    """更新错题笔记"""
    user = get_current_user()
    wq = WrongQuestion.query.get(wq_id)
    if not wq or wq.user_id != user.id:
        return jsonify({'success': False, 'message': '错题不存在'}), 404

    data = request.get_json(silent=True) or {}
    note = (data.get('note') or '').strip()
    wq.note = note
    db.session.commit()
    return jsonify({'success': True, 'message': '笔记已保存'})


@wrong_book_bp.route('/api/<int:wq_id>/review', methods=['POST'])
@login_required
def api_mark_reviewed(wq_id):
    """标记本次已复习，更新 last_reviewed 并按艾宾浩斯曲线安排下次复习。"""
    user = get_current_user()
    wq = WrongQuestion.query.get(wq_id)
    if not wq or wq.user_id != user.id:
        return jsonify({'success': False, 'message': '错题不存在'}), 404

    wq.last_reviewed = datetime.utcnow()
    wq.next_review = compute_next_review(wq.wrong_count or 1)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': '已记录本次复习',
        'next_review': wq.next_review.isoformat() if wq.next_review else None,
    })


@wrong_book_bp.route('/api/<int:wq_id>/delete', methods=['DELETE'])
@login_required
def api_delete(wq_id):
    """删除错题"""
    user = get_current_user()
    wq = WrongQuestion.query.get(wq_id)
    if not wq or wq.user_id != user.id:
        return jsonify({'success': False, 'message': '错题不存在'}), 404

    try:
        db.session.delete(wq)
        db.session.commit()
        return jsonify({'success': True, 'message': '错题已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@wrong_book_bp.route('/api/auto-add', methods=['POST'])
@login_required
def api_auto_add():
    """从刷题记录自动收录错题。

    扫描当前用户所有 QuizAnswer 中 is_correct=False 的记录，
    将其加入错题本（已存在则 wrong_count +1）。
    可选参数 attempt_id：仅收录某次刷题的错题。
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    attempt_id = data.get('attempt_id')

    query = QuizAnswer.query.filter(
        QuizAnswer.is_correct == False
    ).join(QuizAttempt, QuizAnswer.attempt_id == QuizAttempt.id).filter(
        QuizAttempt.user_id == user.id
    )
    if attempt_id:
        query = query.filter(QuizAnswer.attempt_id == attempt_id)

    answers = query.all()
    if not answers:
        return jsonify({'success': True, 'message': '没有可收录的错题', 'added': 0, 'updated': 0})

    added = 0
    updated = 0
    quiz_ids = [a.quiz_id for a in answers]
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all() if quiz_ids else []
    quiz_map = {q.id: q for q in quizzes}

    for a in answers:
        quiz = quiz_map.get(a.quiz_id)
        if not quiz:
            continue
        _, created = add_or_update_wrong_question(
            user.id, quiz.id, a.user_answer or '', correct_answer=quiz.answer
        )
        if created:
            added += 1
        else:
            updated += 1

    db.session.commit()
    return jsonify({
        'success': True,
        'message': f'收录完成：新增 {added} 题，更新 {updated} 题',
        'added': added,
        'updated': updated,
    })


@wrong_book_bp.route('/api/review-list')
@login_required
def api_review_list():
    """获取需要复习的错题（next_review <= now 且未掌握）"""
    user = get_current_user()
    now = datetime.utcnow()
    query = WrongQuestion.query.filter(
        WrongQuestion.user_id == user.id,
        WrongQuestion.is_mastered == False,
        db.or_(WrongQuestion.next_review == None, WrongQuestion.next_review <= now)
    ).order_by(WrongQuestion.next_review.asc())

    items = query.all()
    quiz_ids = [wq.quiz_id for wq in items]
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all() if quiz_ids else []
    quiz_map = {q.id: q for q in quizzes}

    return jsonify({
        'success': True,
        'total': len(items),
        'items': [_serialize_wrong_question(wq, quiz_map.get(wq.quiz_id)) for wq in items],
    })


@wrong_book_bp.route('/api/stats')
@login_required
def api_stats():
    """错题本统计：总错题数、待复习数、已掌握数、今日需复习数"""
    user = get_current_user()
    base = WrongQuestion.query.filter_by(user_id=user.id)
    total = base.count()
    mastered = base.filter(WrongQuestion.is_mastered == True).count()
    now = datetime.utcnow()
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
    need_review = base.filter(
        WrongQuestion.is_mastered == False,
        db.or_(WrongQuestion.next_review == None, WrongQuestion.next_review <= now)
    ).count()
    today_review = base.filter(
        WrongQuestion.is_mastered == False,
        WrongQuestion.next_review != None,
        WrongQuestion.next_review <= today_end
    ).count()

    return jsonify({
        'success': True,
        'total': total,
        'mastered': mastered,
        'need_review': need_review,
        'today_review': today_review,
        'pending': total - mastered - need_review,
    })


@wrong_book_bp.route('/api/export-pdf')
@login_required
def api_export_pdf():
    """导出错题本为 PDF（使用 reportlab）。

    支持与列表相同的筛选参数：chapter, tags, is_mastered。
    """
    user = get_current_user()
    chapter = request.args.get('chapter', '').strip()
    tag = request.args.get('tags', '').strip()
    is_mastered = request.args.get('is_mastered', '').strip()

    query = WrongQuestion.query.filter_by(user_id=user.id)
    if chapter:
        query = query.filter(WrongQuestion.chapter == chapter)
    if tag:
        query = query.filter(WrongQuestion.tags.like(f'%{tag}%'))
    if is_mastered == 'true':
        query = query.filter(WrongQuestion.is_mastered == True)
    elif is_mastered == 'false':
        query = query.filter(WrongQuestion.is_mastered == False)

    items = query.order_by(WrongQuestion.added_at.desc()).all()
    quiz_ids = [wq.quiz_id for wq in items]
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all() if quiz_ids else []
    quiz_map = {q.id: q for q in quizzes}

    pdf_bytes = _build_wrong_book_pdf(user, items, quiz_map, chapter=chapter, tag=tag, is_mastered=is_mastered)

    filename = f'错题本_{user.username}_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf',
    )


def _escape_pdf_text(text):
    """转义 XML 特殊字符，供 Paragraph 使用。"""
    if text is None:
        return ''
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def _build_wrong_book_pdf(user, items, quiz_map, chapter='', tag='', is_mastered=''):
    """生成错题本 PDF 的二进制内容。"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont

    # 注册中文字体（与 exam_pdf 同样的回退策略，但独立实现避免耦合）
    font_name = 'Helvetica'
    font_bold = 'Helvetica-Bold'
    try:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            font_name = 'STSong-Light'
            font_bold = 'STSong-Light'
        except Exception:
            fonts_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
            for fname, ffile in (('MSYaHei', 'msyh.ttc'), ('SimSun', 'simsun.ttc'), ('SimHei', 'simhei.ttf')):
                fpath = os.path.join(fonts_dir, ffile)
                if os.path.exists(fpath):
                    try:
                        pdfmetrics.registerFont(TTFont(fname, fpath))
                        font_name = fname
                        font_bold = fname
                        break
                    except Exception:
                        continue
    except Exception:
        pass

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle('WBTitle', parent=styles['Normal'], fontName=font_bold,
                                 fontSize=20, leading=28, alignment=TA_CENTER, spaceAfter=6)
    style_subtitle = ParagraphStyle('WBSub', parent=styles['Normal'], fontName=font_name,
                                    fontSize=11, leading=16, alignment=TA_CENTER, spaceAfter=4,
                                    textColor=colors.HexColor('#555555'))
    style_section = ParagraphStyle('WBSection', parent=styles['Normal'], fontName=font_bold,
                                   fontSize=13, leading=20, spaceBefore=10, spaceAfter=6,
                                   textColor=colors.HexColor('#1B5E20'))
    style_q = ParagraphStyle('WBQ', parent=styles['Normal'], fontName=font_bold,
                             fontSize=11, leading=18, spaceBefore=8, spaceAfter=4)
    style_body = ParagraphStyle('WBBody', parent=styles['Normal'], fontName=font_name,
                                fontSize=10.5, leading=17, spaceAfter=2)
    style_note = ParagraphStyle('WBNote', parent=styles['Normal'], fontName=font_name,
                                fontSize=10, leading=16, spaceAfter=2,
                                textColor=colors.HexColor('#666666'))

    buffer = io.BytesIO()
    page_width, page_height = A4
    content_width = page_width - 4 * cm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    story = []

    # 标题
    story.append(Paragraph('错题本', style_title))
    meta_lines = [f'用户：{_escape_pdf_text(user.username)}',
                  f'导出时间：{datetime.utcnow().strftime("%Y-%m-%d %H:%M")}',
                  f'错题总数：{len(items)} 题']
    if chapter:
        meta_lines.append(f'章节筛选：{_escape_pdf_text(chapter)}')
    if tag:
        meta_lines.append(f'标签筛选：{_escape_pdf_text(tag)}')
    if is_mastered == 'true':
        meta_lines.append('状态：已掌握')
    elif is_mastered == 'false':
        meta_lines.append('状态：未掌握')
    story.append(Paragraph('　|　'.join(meta_lines), style_subtitle))
    story.append(Spacer(1, 8))

    if not items:
        story.append(Paragraph('暂无错题记录。', style_body))
    else:
        for idx, wq in enumerate(items, 1):
            quiz = quiz_map.get(wq.quiz_id)
            qtype = QUESTION_TYPE_CN.get(quiz.question_type, quiz.question_type) if quiz else ''
            diff = DIFFICULTY_CN.get(quiz.difficulty, quiz.difficulty) if quiz else ''
            chapter_str = wq.chapter or (quiz.chapter if quiz else '')

            header = f'第 {idx} 题'
            if qtype:
                header += f'　[{_escape_pdf_text(qtype)}]'
            if diff:
                header += f'　[{_escape_pdf_text(diff)}]'
            if chapter_str:
                header += f'　[{_escape_pdf_text(chapter_str)}]'
            if wq.is_mastered:
                header += '　[已掌握]'
            header += f'　答错 {wq.wrong_count or 1} 次'
            story.append(Paragraph(header, style_q))

            if quiz:
                story.append(Paragraph(
                    '<b>题目：</b>' + _escape_pdf_text(quiz.question_text), style_body))
            else:
                story.append(Paragraph('<b>题目：</b>(题目已删除)', style_body))

            story.append(Paragraph(
                '<font color="#C0392B"><b>你的答案：</b></font>' + _escape_pdf_text(wq.user_answer or '（未作答）'),
                style_body))
            correct = wq.correct_answer or (quiz.answer if quiz else '')
            story.append(Paragraph(
                '<font color="#1E8449"><b>正确答案：</b></font>' + _escape_pdf_text(correct or ''),
                style_body))
            if quiz and quiz.answer_cn:
                story.append(Paragraph(
                    '<b>中文答案：</b>' + _escape_pdf_text(quiz.answer_cn), style_body))

            review_info = []
            if wq.last_reviewed:
                review_info.append(f'最后复习：{wq.last_reviewed.strftime("%Y-%m-%d")}')
            if wq.next_review:
                review_info.append(f'下次复习：{wq.next_review.strftime("%Y-%m-%d")}')
            if review_info:
                story.append(Paragraph('　'.join(review_info), style_note))

            if wq.note:
                story.append(Paragraph(
                    '<b>笔记：</b>' + _escape_pdf_text(wq.note), style_note))

            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
