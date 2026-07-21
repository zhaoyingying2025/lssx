import os
import json
import re
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app.models import Quiz, ExamPaper, QuizAttempt, QuizAnswer
from app.utils.auth_helpers import login_required, get_current_user
from app.utils.achievement_service import record_quiz_submit, record_quiz_finish
from app import db

quiz_bp = Blueprint('quiz', __name__)

QUESTION_TYPE_CN = {
    'choice': '选择题',
    'true_false': '判断题',
    'fill': '填空题',
    'calc': '计算题',
    'proof': '证明题',
    'short_answer': '简答题',
}

DIFFICULTY_CN = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难',
}

# 不自动判分的题型
MANUAL_GRADE_TYPES = {'calc', 'proof', 'short_answer'}

TRUE_VALUES = {'t', 'true', '正确', '对', 'yes', 'y', '1', '√'}
FALSE_VALUES = {'f', 'false', '错误', '错', 'no', 'n', '0', '×'}


def _normalize_bool(val):
    """将各种布尔值表示统一为 True/False/None"""
    if val is None:
        return None
    v = val.strip().lower()
    if v in TRUE_VALUES:
        return True
    if v in FALSE_VALUES:
        return False
    return None


def _parse_options(options_str):
    """将选项字符串解析为列表
    支持格式：
    1. JSON 数组/对象
    2. "A. xxx\nB. xxx" 格式
    3. "A.xxx|B.xxx" 格式
    """
    if not options_str:
        return None
    try:
        parsed = json.loads(options_str)
        if isinstance(parsed, (list, dict)):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    # 解析 "A. xxx\nB. xxx" 格式
    lines = [line.strip() for line in options_str.replace('\r\n', '\n').split('\n') if line.strip()]
    if len(lines) >= 2:
        result = []
        for line in lines:
            m = re.match(r'^([A-Ha-h])[\.\、\)]\s*(.*)', line)
            if m:
                result.append(m.group(2).strip())
            else:
                result.append(line.strip())
        if len(result) >= 2:
            return result
    # 解析 "A.xxx|B.xxx" 格式
    if '|' in options_str:
        parts = [p.strip() for p in options_str.split('|') if p.strip()]
        if len(parts) >= 2:
            result = []
            for p in parts:
                m = re.match(r'^([A-Ha-h])[\.\、\)]\s*(.*)', p)
                if m:
                    result.append(m.group(2).strip())
                else:
                    result.append(p)
            return result
    return options_str


def _check_answer(question_type, user_answer, correct_answer):
    """判分函数
    返回值：
        True/False - 自动判分结果
        None - 不自动判分（calc/proof/short_answer）
    """
    if user_answer is None:
        user_answer = ''
    if correct_answer is None:
        correct_answer = ''
    user = user_answer.strip().lower()
    correct = correct_answer.strip().lower()

    if question_type == 'true_false':
        # 判断题：支持 T/F、正确/错误、True/False 等多种格式
        user_bool = _normalize_bool(user_answer)
        correct_bool = _normalize_bool(correct_answer)
        if user_bool is not None and correct_bool is not None:
            return user_bool == correct_bool
        # 回退到精确匹配
        return user.replace(' ', '') == correct.replace(' ', '')

    if question_type == 'choice':
        # 选择题：完全匹配（忽略大小写、空格）
        return user.replace(' ', '') == correct.replace(' ', '')

    elif question_type == 'fill':
        # 支持多个正确答案（| 分隔）
        correct_options = [c.strip().lower() for c in correct.split('|') if c.strip()]
        # 去除空格和中英文标点（含中英文引号、括号等）
        punct_pattern = re.compile(r"""[\s,.;:!?'"，。；：！？、（）()【】\[\]]+""")
        user_clean = punct_pattern.sub('', user)
        for opt in correct_options:
            opt_clean = punct_pattern.sub('', opt)
            if user_clean == opt_clean:
                return True
        return False

    else:
        # calc/proof/short_answer 不自动判分
        return None


@quiz_bp.route('/')
def index():
    chapter = request.args.get('chapter', '')
    difficulty = request.args.get('difficulty', '')
    question_type = request.args.get('question_type', '')
    tag = request.args.get('tag', '')
    query = Quiz.query
    if chapter:
        query = query.filter_by(chapter=chapter)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if question_type:
        query = query.filter_by(question_type=question_type)
    if tag:
        query = query.filter(Quiz.tags.like(f'%{tag}%'))
    quizzes = query.order_by(Quiz.created_at.desc()).all()

    chapters = sorted(set(q.chapter for q in Quiz.query.with_entities(Quiz.chapter).distinct() if q.chapter))

    try:
        from app.utils.quiz_data import get_all_tags as _builtin_tags
        builtin_tags = _builtin_tags()
    except Exception:
        builtin_tags = []
    db_tags = set()
    for row in Quiz.query.with_entities(Quiz.tags).distinct():
        if row and row[0]:
            for t in row[0].split(','):
                t = t.strip()
                if t:
                    db_tags.add(t)
    all_tags = sorted(set(builtin_tags) | db_tags)

    return render_template('quiz.html', quizzes=quizzes, chapter=chapter,
                           difficulty=difficulty, question_type=question_type,
                           tag=tag, chapters=chapters, all_tags=all_tags)


@quiz_bp.route('/api/list')
def api_list():
    """题目列表API，支持筛选参数"""
    chapter = request.args.get('chapter', '')
    question_type = request.args.get('question_type', '')
    difficulty = request.args.get('difficulty', '')
    tag = request.args.get('tag', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = Quiz.query
    if chapter:
        query = query.filter_by(chapter=chapter)
    if question_type:
        query = query.filter_by(question_type=question_type)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if tag:
        query = query.filter(Quiz.tags.like(f'%{tag}%'))

    total = query.count()
    quizzes = query.order_by(Quiz.chapter, Quiz.section, Quiz.question_number).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'items': [{
            'id': q.id,
            'chapter': q.chapter,
            'section': q.section,
            'question_number': q.question_number,
            'question_text': q.question_text,
            'question_type': q.question_type,
            'options': q.options,
            'answer': q.answer,
            'difficulty': q.difficulty,
            'source_page': q.source_page,
            'tags': q.tags,
            'created_at': q.created_at.isoformat() if q.created_at else None
        } for q in quizzes]
    })


@quiz_bp.route('/api/random')
def api_random():
    count = request.args.get('count', 5, type=int)
    chapter = request.args.get('chapter', '')
    query = Quiz.query
    if chapter:
        query = query.filter_by(chapter=chapter)
    quizzes = query.order_by(db.func.random()).limit(count).all()
    return jsonify([{
        'id': q.id,
        'chapter': q.chapter,
        'section': q.section,
        'question_text': q.question_text,
        'question_type': q.question_type,
        'options': _parse_options(q.options),
        'answer': q.answer,
        'difficulty': q.difficulty
    } for q in quizzes])


@quiz_bp.route('/api/tags')
def api_tags():
    """获取所有不重复标签列表（合并内置题库与数据库已存题目）"""
    try:
        from app.utils.quiz_data import get_all_tags as _builtin_tags
        builtin_tags = _builtin_tags()
    except Exception:
        builtin_tags = []
    db_tags = set()
    for row in Quiz.query.with_entities(Quiz.tags).distinct():
        if row and row[0]:
            for t in row[0].split(','):
                t = t.strip()
                if t:
                    db_tags.add(t)
    all_tags = sorted(set(builtin_tags) | db_tags)
    return jsonify({'tags': all_tags, 'count': len(all_tags)})


@quiz_bp.route('/api/detail/<int:quiz_id>')
def api_detail(quiz_id):
    """获取单道题目详情"""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'success': False, 'message': '题目不存在'}), 404
    return jsonify({
        'success': True,
        'item': {
            'id': quiz.id,
            'chapter': quiz.chapter,
            'section': quiz.section,
            'question_number': quiz.question_number,
            'question_text': quiz.question_text,
            'question_type': quiz.question_type,
            'options': quiz.options,
            'answer': quiz.answer,
            'difficulty': quiz.difficulty,
            'source_page': quiz.source_page,
            'tags': quiz.tags,
            'created_at': quiz.created_at.isoformat() if quiz.created_at else None,
        }
    })


@quiz_bp.route('/api/create', methods=['POST'])
def api_create():
    """手动创建一道新题目。

    必填字段：question_text、answer
    可选字段：chapter、section、question_type、difficulty、options、tags
    """
    data = request.get_json(silent=True) or {}

    question_text = (data.get('question_text') or '').strip()
    answer = (data.get('answer') or '').strip()
    if not question_text:
        return jsonify({'success': False, 'message': '题目内容不能为空'}), 400
    if not answer:
        return jsonify({'success': False, 'message': '答案不能为空'}), 400

    valid_types = {'choice', 'fill', 'calc', 'proof', 'true_false', 'short_answer'}
    question_type = data.get('question_type', 'choice')
    if question_type not in valid_types:
        question_type = 'choice'

    valid_diff = {'easy', 'medium', 'hard'}
    difficulty = data.get('difficulty', 'medium')
    if difficulty not in valid_diff:
        difficulty = 'medium'

    chapter = (data.get('chapter') or '').strip()
    section = (data.get('section') or '').strip()
    max_num = db.session.query(db.func.max(Quiz.question_number)).filter_by(chapter=chapter).scalar() or 0

    quiz = Quiz(
        chapter=chapter,
        section=section,
        question_number=max_num + 1,
        question_text=question_text,
        question_type=question_type,
        options=data.get('options') or '',
        answer=answer,
        difficulty=difficulty,
        tags=data.get('tags') or '',
    )
    db.session.add(quiz)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': '题目创建成功',
        'id': quiz.id,
        'question_number': quiz.question_number,
    })


@quiz_bp.route('/api/update/<int:quiz_id>', methods=['PUT'])
def api_update(quiz_id):
    """更新一道题目的内容。

    支持部分更新：仅更新请求中提供的字段。
    可更新字段：chapter、section、question_text、question_type、difficulty、
              options、answer、tags
    """
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'success': False, 'message': '题目不存在'}), 404

    data = request.get_json(silent=True) or {}
    valid_types = {'choice', 'fill', 'calc', 'proof', 'true_false', 'short_answer'}
    valid_diff = {'easy', 'medium', 'hard'}

    if 'chapter' in data:
        quiz.chapter = (data.get('chapter') or '').strip()
    if 'section' in data:
        quiz.section = (data.get('section') or '').strip()
    if 'question_text' in data:
        if not (data.get('question_text') or '').strip():
            return jsonify({'success': False, 'message': '题目内容不能为空'}), 400
        quiz.question_text = data.get('question_text')
    if 'question_type' in data and data['question_type'] in valid_types:
        quiz.question_type = data['question_type']
    if 'difficulty' in data and data['difficulty'] in valid_diff:
        quiz.difficulty = data['difficulty']
    if 'options' in data:
        quiz.options = data.get('options') or ''
    if 'answer' in data:
        if not (data.get('answer') or '').strip():
            return jsonify({'success': False, 'message': '答案不能为空'}), 400
        quiz.answer = data['answer']
    if 'tags' in data:
        quiz.tags = data.get('tags') or ''

    db.session.commit()
    return jsonify({
        'success': True,
        'message': '题目已更新',
        'id': quiz.id,
    })


@quiz_bp.route('/api/delete/<int:quiz_id>', methods=['DELETE'])
def api_delete(quiz_id):
    """删除一道题目"""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'success': False, 'message': '题目不存在'}), 404
    try:
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'success': True, 'message': '题目已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@quiz_bp.route('/api/reset', methods=['POST'])
def api_reset():
    """重置题库：清空所有现有题目并导入内置的 200 道离散数学题目。

    警告：该操作不可恢复，会删除数据库中所有现有题目（包括手动添加的题目）。
    """
    try:
        from app.utils.quiz_data import import_quiz_data
        count = import_quiz_data()
        return jsonify({
            'success': True,
            'message': f'题库已重置，共导入 {count} 道题目',
            'count': count,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'重置题库失败: {str(e)}',
        }), 500


@quiz_bp.route('/api/import-builtin', methods=['POST'])
def api_import_builtin():
    """重置题库的别名端点，便于前端调用。"""
    return api_reset()


# ===== 组卷 API =====

@quiz_bp.route('/api/exam-form')
def api_exam_form():
    """获取组卷表单数据（可用章节、题型等）"""
    from app.utils.exam_generator import (
        get_available_chapters, get_available_question_types,
        get_question_counts_by_chapter_and_type,
        QUESTION_TYPE_NAMES, DIFFICULTY_NAMES, DEFAULT_SCORES
    )

    chapters = get_available_chapters()
    question_types = get_available_question_types()
    counts = get_question_counts_by_chapter_and_type()

    # 总可用题数
    total_available = Quiz.query.count()

    return jsonify({
        'chapters': chapters,
        'question_types': [
            {'value': qt, 'label': QUESTION_TYPE_NAMES.get(qt, qt)}
            for qt in question_types
        ],
        'difficulties': [
            {'value': 'easy', 'label': DIFFICULTY_NAMES['easy']},
            {'value': 'medium', 'label': DIFFICULTY_NAMES['medium']},
            {'value': 'hard', 'label': DIFFICULTY_NAMES['hard']},
        ],
        'default_scores': DEFAULT_SCORES,
        'counts_by_chapter_type': counts,
        'total_available': total_available,
    })


@quiz_bp.route('/api/generate-exam', methods=['POST'])
def api_generate_exam():
    """生成试卷"""
    from app.utils.exam_generator import generate_exam, QUESTION_TYPE_NAMES
    from app.utils.exam_pdf import generate_exam_pdf, generate_exam_html

    data = request.get_json(silent=True) or {}

    title = data.get('title', '离散数学试卷')
    chapters = data.get('chapters', [])
    question_types = data.get('question_types', [])
    difficulty = data.get('difficulty', {'easy': 3, 'medium': 5, 'hard': 2})
    total_count = data.get('total_count', 20)
    include_answers = data.get('include_answers', True)
    answer_language = data.get('answer_language', 'cn')

    if not question_types:
        return jsonify({'success': False, 'message': '请至少选择一种题型'}), 400

    if total_count < 1 or total_count > 200:
        return jsonify({'success': False, 'message': '题数应在1-200之间'}), 400

    try:
        # 生成试卷
        exam_data = generate_exam(
            title=title,
            chapters=chapters,
            question_types=question_types,
            difficulty_distribution=difficulty,
            total_count=total_count,
            include_answers=include_answers,
            answer_language=answer_language,
        )

        if not exam_data['questions']:
            return jsonify({
                'success': False,
                'message': '没有找到符合条件的题目，请调整筛选条件',
            }), 400

        # 序列化题目数据
        questions_serialized = []
        for group in exam_data['questions']:
            group_data = {
                'type': group['type'],
                'type_name': group['type_name'],
                'score_per': group['score_per'],
                'questions': [],
            }
            for q in group['questions']:
                group_data['questions'].append({
                    'id': q.id,
                    'chapter': q.chapter,
                    'section': q.section,
                    'question_text': q.question_text,
                    'question_type': q.question_type,
                    'options': q.options,
                    'answer': q.answer,
                    'difficulty': q.difficulty,
                })
            questions_serialized.append(group_data)

        # 生成PDF
        pdf_dir = os.path.join(current_app.root_path, '..', 'exam_pdfs')
        os.makedirs(pdf_dir, exist_ok=True)

        import time
        timestamp = int(time.time())
        safe_title = ''.join(c for c in title if c.isalnum() or c in '_ -') or 'exam'
        pdf_filename = f'{safe_title}_{timestamp}.pdf'
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        generate_exam_pdf(exam_data, pdf_path, include_answers=include_answers,
                          answer_language=answer_language)

        # 生成HTML预览
        html_preview = generate_exam_html(exam_data, include_answers=include_answers,
                                           answer_language=answer_language)

        # 保存到数据库
        paper = ExamPaper(
            title=title,
            chapters_json=json.dumps(chapters, ensure_ascii=False),
            question_types_json=json.dumps(question_types, ensure_ascii=False),
            difficulty_json=json.dumps(difficulty, ensure_ascii=False),
            total_count=exam_data['stats']['total'],
            include_answers=include_answers,
            answer_language=answer_language,
            questions_json=json.dumps(questions_serialized, ensure_ascii=False),
            pdf_path=pdf_path,
        )
        db.session.add(paper)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'试卷生成成功！共{exam_data["stats"]["total"]}题',
            'paper_id': paper.id,
            'html_preview': html_preview,
            'warnings': exam_data.get('warnings', []),
            'stats': exam_data['stats'],
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'生成试卷失败: {str(e)}',
        }), 500


@quiz_bp.route('/api/exam-list')
def api_exam_list():
    """获取已生成试卷列表"""
    papers = ExamPaper.query.order_by(ExamPaper.created_at.desc()).all()

    return jsonify({
        'items': [{
            'id': p.id,
            'title': p.title,
            'chapters': json.loads(p.chapters_json) if p.chapters_json else [],
            'question_types': json.loads(p.question_types_json) if p.question_types_json else [],
            'total_count': p.total_count,
            'include_answers': p.include_answers,
            'answer_language': p.answer_language,
            'created_at': p.created_at.isoformat() if p.created_at else None,
        } for p in papers]
    })


@quiz_bp.route('/api/exam-pdf/<int:paper_id>')
def api_exam_pdf(paper_id):
    """下载PDF试卷"""
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({'success': False, 'message': '试卷不存在'}), 404

    if not paper.pdf_path or not os.path.exists(paper.pdf_path):
        return jsonify({'success': False, 'message': 'PDF文件不存在'}), 404

    return send_file(
        paper.pdf_path,
        as_attachment=True,
        download_name=f'{paper.title}.pdf',
        mimetype='application/pdf',
    )


@quiz_bp.route('/api/exam-preview/<int:paper_id>')
def api_exam_preview(paper_id):
    """预览试卷内容（HTML）"""
    from app.utils.exam_pdf import generate_exam_html

    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({'success': False, 'message': '试卷不存在'}), 404

    try:
        # 从存储的题目数据重建exam_data格式
        questions_data = json.loads(paper.questions_json) if paper.questions_json else []

        # 需要重新获取Quiz对象来生成HTML
        quiz_ids = []
        for group in questions_data:
            for q in group.get('questions', []):
                quiz_ids.append(q['id'])

        quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all() if quiz_ids else []
        quiz_map = {q.id: q for q in quizzes}

        # 重建exam_data
        exam_data = {
            'title': paper.title,
            'questions': [],
        }
        for group in questions_data:
            group_questions = []
            for q_data in group.get('questions', []):
                q = quiz_map.get(q_data['id'])
                if q:
                    group_questions.append(q)
            if group_questions:
                exam_data['questions'].append({
                    'type': group['type'],
                    'type_name': group['type_name'],
                    'score_per': group['score_per'],
                    'questions': group_questions,
                })

        html_preview = generate_exam_html(
            exam_data,
            include_answers=paper.include_answers,
            answer_language=paper.answer_language,
        )

        return jsonify({
            'success': True,
            'html_preview': html_preview,
            'title': paper.title,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'预览失败: {str(e)}',
        }), 500


@quiz_bp.route('/api/exam-delete/<int:paper_id>', methods=['DELETE'])
def api_exam_delete(paper_id):
    """删除试卷"""
    paper = ExamPaper.query.get(paper_id)
    if not paper:
        return jsonify({'success': False, 'message': '试卷不存在'}), 404

    try:
        # 删除PDF文件
        if paper.pdf_path and os.path.exists(paper.pdf_path):
            os.remove(paper.pdf_path)

        db.session.delete(paper)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '试卷已删除',
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}',
        }), 500


# ===== 在线刷题 API =====

def _serialize_quiz_for_practice(quiz):
    """将题目序列化为前端需要的格式（不含答案）"""
    options = _parse_options(quiz.options)

    return {
        'id': quiz.id,
        'chapter': quiz.chapter,
        'section': quiz.section,
        'question_number': quiz.question_number,
        'question_text': quiz.question_text,
        'question_type': quiz.question_type,
        'question_type_cn': QUESTION_TYPE_CN.get(quiz.question_type, quiz.question_type),
        'options': options,
        'difficulty': quiz.difficulty,
        'difficulty_cn': DIFFICULTY_CN.get(quiz.difficulty, quiz.difficulty),
        'tags': quiz.tags,
    }


@quiz_bp.route('/practice')
@login_required
def practice():
    """刷题主页面"""
    # 获取所有章节供前端选择
    chapters = sorted(set(
        q.chapter for q in Quiz.query.with_entities(Quiz.chapter).distinct()
        if q.chapter
    ))
    # 获取所有标签
    try:
        from app.utils.quiz_data import get_all_tags as _builtin_tags
        builtin_tags = _builtin_tags()
    except Exception:
        builtin_tags = []
    db_tags = set()
    for row in Quiz.query.with_entities(Quiz.tags).distinct():
        if row and row[0]:
            for t in row[0].split(','):
                t = t.strip()
                if t:
                    db_tags.add(t)
    all_tags = sorted(set(builtin_tags) | db_tags)

    # 题型统计（按可用题型）
    question_types = []
    for qt, cn in QUESTION_TYPE_CN.items():
        count = Quiz.query.filter_by(question_type=qt).count()
        if count > 0:
            question_types.append({'value': qt, 'label': cn, 'count': count})

    return render_template(
        'quiz_practice.html',
        chapters=chapters,
        all_tags=all_tags,
        question_types=question_types,
    )


@quiz_bp.route('/api/practice/start', methods=['POST'])
@login_required
def api_practice_start():
    """开始一次刷题
    请求体: {
        mode: 'practice'|'random'|'exam',
        chapters: [],  # 空表示全部
        question_types: [],  # 空表示全部
        difficulty: [],  # 空表示全部
        count: 10,  # 题目数量
        tags: [],  # 标签筛选
    }
    返回: {
        attempt_id: 123,
        questions: [{id, question_text, question_type, options, difficulty, chapter, tags}],
    }
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    mode = data.get('mode', 'practice')
    if mode not in ('practice', 'random', 'exam'):
        mode = 'practice'

    chapters = data.get('chapters', []) or []
    question_types = data.get('question_types', []) or []
    difficulty = data.get('difficulty', []) or []
    tags = data.get('tags', []) or []
    count = int(data.get('count', 10))
    if count < 1:
        count = 10
    if count > 200:
        count = 200

    # 构建查询
    query = Quiz.query
    if chapters:
        query = query.filter(Quiz.chapter.in_(chapters))
    if question_types:
        query = query.filter(Quiz.question_type.in_(question_types))
    if difficulty:
        query = query.filter(Quiz.difficulty.in_(difficulty))
    if tags:
        # 标签采用 OR 匹配（任一标签命中即可）
        tag_filters = []
        for t in tags:
            tag_filters.append(Quiz.tags.like(f'%{t}%'))
        query = query.filter(db.or_(*tag_filters))

    # 随机排序并限制数量
    quizzes = query.order_by(db.func.random()).limit(count).all()

    if not quizzes:
        return jsonify({
            'success': False,
            'message': '没有找到符合条件的题目，请调整筛选条件',
        }), 400

    # 创建 QuizAttempt 记录
    attempt = QuizAttempt(
        user_id=user.id,
        mode=mode,
        total_count=len(quizzes),
        correct_count=0,
        score=0,
        duration=0,
        chapters_json=json.dumps(chapters, ensure_ascii=False) if chapters else None,
        started_at=datetime.utcnow(),
    )
    db.session.add(attempt)
    db.session.commit()

    # 序列化题目（不含答案）
    questions = [_serialize_quiz_for_practice(q) for q in quizzes]

    return jsonify({
        'success': True,
        'attempt_id': attempt.id,
        'mode': mode,
        'questions': questions,
        'total': len(questions),
    })


@quiz_bp.route('/api/practice/submit', methods=['POST'])
@login_required
def api_practice_submit():
    """提交单题答案（即时判分）
    请求体: {
        attempt_id: 123,
        quiz_id: 456,
        user_answer: 'A',
    }
    返回: {
        is_correct: true/false/null,
        correct_answer: '...',
        explanation: '...'  # 如果有的话
    }
    """
    data = request.get_json(silent=True) or {}
    attempt_id = data.get('attempt_id')
    quiz_id = data.get('quiz_id')
    user_answer = data.get('user_answer', '')

    if not attempt_id or not quiz_id:
        return jsonify({'success': False, 'message': '缺少 attempt_id 或 quiz_id'}), 400

    attempt = QuizAttempt.query.get(attempt_id)
    if not attempt:
        return jsonify({'success': False, 'message': '刷题记录不存在'}), 404

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'success': False, 'message': '题目不存在'}), 404

    # 模拟考试模式不即时判分，仅记录答案
    if attempt.mode == 'exam':
        # 记录答案（如已存在则更新）
        answer_record = QuizAnswer.query.filter_by(
            attempt_id=attempt_id, quiz_id=quiz_id
        ).first()
        if answer_record:
            answer_record.user_answer = user_answer
        else:
            answer_record = QuizAnswer(
                attempt_id=attempt_id,
                quiz_id=quiz_id,
                user_answer=user_answer,
                is_correct=None,
                question_type=quiz.question_type,
                difficulty=quiz.difficulty,
                chapter=quiz.chapter,
                tags=quiz.tags,
            )
            db.session.add(answer_record)
        db.session.commit()

        # 更新成就进度（答题数量）
        try:
            record_quiz_submit(attempt.user_id, None)
        except Exception:
            pass

        return jsonify({
            'success': True,
            'is_correct': None,
            'message': '答案已保存，将在考试结束后统一判分',
        })

    # 即时判分（practice/random 模式）
    is_correct = _check_answer(quiz.question_type, user_answer, quiz.answer)

    # 记录或更新作答
    answer_record = QuizAnswer.query.filter_by(
        attempt_id=attempt_id, quiz_id=quiz_id
    ).first()
    if answer_record:
        answer_record.user_answer = user_answer
        answer_record.is_correct = is_correct
    else:
        answer_record = QuizAnswer(
            attempt_id=attempt_id,
            quiz_id=quiz_id,
            user_answer=user_answer,
            is_correct=is_correct,
            question_type=quiz.question_type,
            difficulty=quiz.difficulty,
            chapter=quiz.chapter,
            tags=quiz.tags,
        )
        db.session.add(answer_record)
    db.session.commit()

    # 更新成就进度
    try:
        record_quiz_submit(user.id, is_correct)
    except Exception:
        pass

    # 返回判分结果与参考答案
    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': quiz.answer,
        'explanation': '',
        'question_type': quiz.question_type,
        'auto_graded': quiz.question_type not in MANUAL_GRADE_TYPES,
    })


@quiz_bp.route('/api/practice/finish', methods=['POST'])
@login_required
def api_practice_finish():
    """结束刷题，生成成绩单
    请求体: {
        attempt_id: 123,
        duration: 300,  # 用时秒
    }
    返回: {
        total: 10,
        correct: 7,
        wrong: 3,
        score: 70,
        details: [{quiz_id, question_text, user_answer, correct_answer, is_correct, chapter, tags}],
        wrong_questions: [...]  # 错题列表
    }
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    attempt_id = data.get('attempt_id')
    duration = int(data.get('duration', 0))

    if not attempt_id:
        return jsonify({'success': False, 'message': '缺少 attempt_id'}), 400

    attempt = QuizAttempt.query.get(attempt_id)
    if not attempt:
        return jsonify({'success': False, 'message': '刷题记录不存在'}), 404

    # 安全检查：仅本人可查看自己的记录
    if attempt.user_id != user.id:
        return jsonify({'success': False, 'message': '无权访问该刷题记录'}), 403

    # 获取所有作答记录
    answer_records = QuizAnswer.query.filter_by(attempt_id=attempt_id).all()
    quiz_ids = [ar.quiz_id for ar in answer_records]
    quizzes = Quiz.query.filter(Quiz.id.in_(quiz_ids)).all() if quiz_ids else []
    quiz_map = {q.id: q for q in quizzes}

    # 模拟考试模式：统一判分
    if attempt.mode == 'exam':
        for ar in answer_records:
            q = quiz_map.get(ar.quiz_id)
            if q and ar.is_correct is None:
                ar.is_correct = _check_answer(q.question_type, ar.user_answer, q.answer)
        db.session.commit()

    # 统计
    total = attempt.total_count
    correct_count = sum(1 for ar in answer_records if ar.is_correct is True)
    wrong_count = sum(1 for ar in answer_records if ar.is_correct is False)
    ungraded_count = sum(1 for ar in answer_records if ar.is_correct is None)
    answered_count = len(answer_records)

    # 百分制得分：只计算可判分的题目（choice/true_false/fill）
    gradable = correct_count + wrong_count
    if gradable > 0:
        score = round(correct_count / gradable * 100, 1)
    else:
        score = 0

    # 更新 attempt
    attempt.correct_count = correct_count
    attempt.score = score
    attempt.duration = duration
    attempt.finished_at = datetime.utcnow()
    db.session.commit()

    # 更新成就进度（正确率）
    try:
        record_quiz_finish(user.id, score)
    except Exception:
        pass

    # 自动收录错题到错题本（仅自动判分为错的）
    # 延迟导入避免循环依赖；错题收录失败不影响成绩返回
    try:
        from app.routes.wrong_book import add_or_update_wrong_question
        for ar in answer_records:
            if ar.is_correct is False:
                q = quiz_map.get(ar.quiz_id)
                if q is None:
                    continue
                add_or_update_wrong_question(
                    user.id, q.id, ar.user_answer or '', correct_answer=q.answer
                )
        db.session.commit()
    except Exception:
        db.session.rollback()

    # 构建详情列表
    details = []
    wrong_questions = []
    for ar in answer_records:
        q = quiz_map.get(ar.quiz_id)
        if not q:
            continue
        detail = {
            'quiz_id': q.id,
            'question_text': q.question_text,
            'question_type': q.question_type,
            'question_type_cn': QUESTION_TYPE_CN.get(q.question_type, q.question_type),
            'user_answer': ar.user_answer or '',
            'correct_answer': q.answer,
            'is_correct': ar.is_correct,
            'chapter': q.chapter,
            'tags': q.tags,
            'difficulty': q.difficulty,
            'difficulty_cn': DIFFICULTY_CN.get(q.difficulty, q.difficulty),
            'auto_graded': q.question_type not in MANUAL_GRADE_TYPES,
        }
        details.append(detail)
        # 错题（仅自动判分为错的）
        if ar.is_correct is False:
            wrong_questions.append(detail)

    return jsonify({
        'success': True,
        'attempt_id': attempt.id,
        'mode': attempt.mode,
        'total': total,
        'answered': answered_count,
        'correct': correct_count,
        'wrong': wrong_count,
        'ungraded': ungraded_count,
        'score': score,
        'duration': duration,
        'details': details,
        'wrong_questions': wrong_questions,
    })


@quiz_bp.route('/api/practice/history')
@login_required
def api_practice_history():
    """获取刷题历史记录"""
    user = get_current_user()
    limit = request.args.get('limit', 50, type=int)
    if limit < 1:
        limit = 50
    if limit > 500:
        limit = 500

    attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(
        QuizAttempt.started_at.desc()
    ).limit(limit).all()

    items = []
    for a in attempts:
        items.append({
            'id': a.id,
            'mode': a.mode,
            'mode_cn': {'practice': '章节练习', 'random': '随机刷题', 'exam': '模拟考试'}.get(a.mode, a.mode),
            'total_count': a.total_count,
            'correct_count': a.correct_count,
            'score': a.score,
            'duration': a.duration,
            'chapters': json.loads(a.chapters_json) if a.chapters_json else [],
            'started_at': a.started_at.isoformat() if a.started_at else None,
            'finished_at': a.finished_at.isoformat() if a.finished_at else None,
            'is_finished': a.finished_at is not None,
        })

    # 统计
    total_attempts = QuizAttempt.query.filter_by(user_id=user.id).count()
    finished_attempts = QuizAttempt.query.filter_by(user_id=user.id).filter(
        QuizAttempt.finished_at != None
    ).count()
    avg_score = 0
    if finished_attempts > 0:
        scores = QuizAttempt.query.filter_by(user_id=user.id).filter(
            QuizAttempt.finished_at != None,
            QuizAttempt.score != None
        ).with_entities(QuizAttempt.score).all()
        valid_scores = [s[0] for s in scores if s[0] is not None]
        if valid_scores:
            avg_score = round(sum(valid_scores) / len(valid_scores), 1)

    return jsonify({
        'success': True,
        'items': items,
        'stats': {
            'total_attempts': total_attempts,
            'finished_attempts': finished_attempts,
            'avg_score': avg_score,
        },
    })
