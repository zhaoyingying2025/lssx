"""学习仪表盘蓝图

提供学习数据概览、各章节正确率、学习趋势、题型分布、
推荐学习内容等接口，以及仪表盘主页面。

所有路由均需登录（@login_required）。
"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify

from app import db
from app.models import (
    QuizAttempt, QuizAnswer, Quiz, KnowledgeItem, WrongQuestion
)
from app.utils.auth_helpers import login_required, get_current_user
from app.utils.achievement_service import get_user_achievements, get_user_achievement_stats, get_achievement_leaderboard, share_achievement

dashboard_bp = Blueprint('dashboard', __name__)


# 题型中文名映射
QUESTION_TYPE_CN = {
    'choice': '选择题',
    'fill': '填空题',
    'calc': '计算题',
    'proof': '证明题',
    'true_false': '判断题',
    'short_answer': '简答题',
}


def _user_answer_ids(user_id):
    """返回当前用户的所有 attempt_id 列表"""
    rows = db.session.query(QuizAttempt.id).filter(QuizAttempt.user_id == user_id).all()
    return [r[0] for r in rows]


@dashboard_bp.route('/')
@login_required
def index():
    """仪表盘主页面"""
    return render_template('dashboard.html')


@dashboard_bp.route('/api/overview')
@login_required
def api_overview():
    """数据概览：累计学习天数、做题数量、总正确率、已掌握知识点、总刷题次数、今日做题数"""
    user = get_current_user()
    now = datetime.utcnow()

    attempt_ids = _user_answer_ids(user.id)

    # 累计做题数量（仅统计有作答记录的）
    total_answered = 0
    total_correct = 0
    if attempt_ids:
        total_answered = QuizAnswer.query.filter(QuizAnswer.attempt_id.in_(attempt_ids)).count()
        total_correct = QuizAnswer.query.filter(
            QuizAnswer.attempt_id.in_(attempt_ids),
            QuizAnswer.is_correct == True
        ).count()

    # 总正确率（仅基于可判分题目）
    accuracy = round(total_correct / total_answered * 100, 1) if total_answered > 0 else 0.0

    # 累计学习天数：第一次做题到最后一次做题的天数差
    study_days = 0
    if attempt_ids:
        first = db.session.query(db.func.min(QuizAnswer.created_at)).filter(
            QuizAnswer.attempt_id.in_(attempt_ids)
        ).scalar()
        last = db.session.query(db.func.max(QuizAnswer.created_at)).filter(
            QuizAnswer.attempt_id.in_(attempt_ids)
        ).scalar()
        if first and last:
            first_d = first.date() if hasattr(first, 'date') else first
            last_d = last.date() if hasattr(last, 'date') else last
            # 兼容 datetime / date
            try:
                study_days = (last_d - first_d).days + 1
            except TypeError:
                study_days = 0
            if study_days < 0:
                study_days = 0

    # 已掌握知识点数量（从 KnowledgeItem 关联：统计有内容的知识条目数）
    mastered_knowledge = KnowledgeItem.query.count()

    # 总刷题次数
    total_attempts = QuizAttempt.query.filter_by(user_id=user.id).count()

    # 今日做题数（按 UTC 当天，作答记录 created_at）
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
    today_answered = 0
    if attempt_ids:
        today_answered = QuizAnswer.query.filter(
            QuizAnswer.attempt_id.in_(attempt_ids),
            QuizAnswer.created_at >= today_start,
            QuizAnswer.created_at <= today_end
        ).count()

    # 错题本统计
    wrong_total = WrongQuestion.query.filter_by(user_id=user.id).count()
    wrong_need_review = WrongQuestion.query.filter(
        WrongQuestion.user_id == user.id,
        WrongQuestion.is_mastered == False,
        db.or_(WrongQuestion.next_review == None, WrongQuestion.next_review <= now)
    ).count()

    return jsonify({
        'success': True,
        'study_days': study_days,
        'total_answered': total_answered,
        'total_correct': total_correct,
        'accuracy': accuracy,
        'mastered_knowledge': mastered_knowledge,
        'total_attempts': total_attempts,
        'today_answered': today_answered,
        'wrong_total': wrong_total,
        'wrong_need_review': wrong_need_review,
    })


@dashboard_bp.route('/api/chapter-stats')
@login_required
def api_chapter_stats():
    """各章节正确率：从 QuizAnswer 按 chapter 分组统计"""
    user = get_current_user()
    attempt_ids = _user_answer_ids(user.id)
    if not attempt_ids:
        return jsonify({'success': True, 'items': []})

    rows = db.session.query(
        QuizAnswer.chapter,
        db.func.count(QuizAnswer.id).label('total'),
        db.func.sum(db.case((QuizAnswer.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        QuizAnswer.attempt_id.in_(attempt_ids),
        QuizAnswer.chapter != None,
        QuizAnswer.chapter != ''
    ).group_by(QuizAnswer.chapter).all()

    items = []
    for chapter, total, correct in rows:
        total = int(total or 0)
        correct = int(correct or 0)
        accuracy = round(correct / total * 100, 1) if total > 0 else 0.0
        items.append({
            'chapter': chapter,
            'total': total,
            'correct': correct,
            'accuracy': accuracy,
        })
    # 按正确率升序，便于前端识别薄弱章节
    items.sort(key=lambda x: x['accuracy'])
    return jsonify({'success': True, 'items': items})


@dashboard_bp.route('/api/trend')
@login_required
def api_trend():
    """学习趋势：近30天每天做题数量和正确数"""
    user = get_current_user()
    attempt_ids = _user_answer_ids(user.id)
    if not attempt_ids:
        return jsonify({'success': True, 'days': [], 'items': []})

    now = datetime.utcnow()
    start = datetime(now.year, now.month, now.day) - timedelta(days=29)

    rows = db.session.query(
        db.func.date(QuizAnswer.created_at).label('d'),
        db.func.count(QuizAnswer.id).label('total'),
        db.func.sum(db.case((QuizAnswer.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        QuizAnswer.attempt_id.in_(attempt_ids),
        QuizAnswer.created_at >= start
    ).group_by(db.func.date(QuizAnswer.created_at)).all()

    # 构建按日期的映射
    stat_map = {}
    for d, total, correct in rows:
        # d 可能是字符串或 date 对象
        key = str(d)
        stat_map[key] = {'total': int(total or 0), 'correct': int(correct or 0)}

    days = []
    items = []
    for i in range(30):
        day = (start + timedelta(days=i))
        key = day.strftime('%Y-%m-%d')
        stat = stat_map.get(key, {'total': 0, 'correct': 0})
        days.append(key[5:])  # MM-DD
        items.append({
            'date': key,
            'total': stat['total'],
            'correct': stat['correct'],
            'accuracy': round(stat['correct'] / stat['total'] * 100, 1) if stat['total'] > 0 else 0.0,
        })

    return jsonify({'success': True, 'days': days, 'items': items})


@dashboard_bp.route('/api/type-distribution')
@login_required
def api_type_distribution():
    """题型分布：从 QuizAnswer 按 question_type 分组"""
    user = get_current_user()
    attempt_ids = _user_answer_ids(user.id)
    if not attempt_ids:
        return jsonify({'success': True, 'items': []})

    rows = db.session.query(
        QuizAnswer.question_type,
        db.func.count(QuizAnswer.id).label('total'),
        db.func.sum(db.case((QuizAnswer.is_correct == True, 1), else_=0)).label('correct')
    ).filter(
        QuizAnswer.attempt_id.in_(attempt_ids)
    ).group_by(QuizAnswer.question_type).all()

    items = []
    for qtype, total, correct in rows:
        total = int(total or 0)
        correct = int(correct or 0)
        accuracy = round(correct / total * 100, 1) if total > 0 else 0.0
        label = QUESTION_TYPE_CN.get(qtype, qtype or '未知')
        items.append({
            'type': qtype or 'unknown',
            'type_cn': label,
            'count': total,
            'correct': correct,
            'accuracy': accuracy,
        })
    # 按数量降序
    items.sort(key=lambda x: x['count'], reverse=True)
    return jsonify({'success': True, 'items': items})


@dashboard_bp.route('/api/recommendations')
@login_required
def api_recommendations():
    """推荐学习内容：
    - 正确率低于60%的章节 → 推荐复习该章节知识
    - 待复习的错题 → 推荐复习错题
    - 未学习过的章节 → 推荐开始学习
    """
    user = get_current_user()
    now = datetime.utcnow()
    attempt_ids = _user_answer_ids(user.id)

    recommendations = []

    # 1) 待复习错题
    wrong_review_count = WrongQuestion.query.filter(
        WrongQuestion.user_id == user.id,
        WrongQuestion.is_mastered == False,
        db.or_(WrongQuestion.next_review == None, WrongQuestion.next_review <= now)
    ).count()
    if wrong_review_count > 0:
        recommendations.append({
            'type': 'wrong_review',
            'icon': 'bi-journal-x',
            'title': f'复习错题本',
            'desc': f'你有 {wrong_review_count} 道错题已到复习时间，趁热打铁巩固一下',
            'link': '/wrong-book/',
            'link_text': '去复习',
            'priority': 1,
        })

    # 2) 正确率低于60%的章节
    practiced_chapters = set()
    if attempt_ids:
        rows = db.session.query(
            QuizAnswer.chapter,
            db.func.count(QuizAnswer.id).label('total'),
            db.func.sum(db.case((QuizAnswer.is_correct == True, 1), else_=0)).label('correct')
        ).filter(
            QuizAnswer.attempt_id.in_(attempt_ids),
            QuizAnswer.chapter != None,
            QuizAnswer.chapter != ''
        ).group_by(QuizAnswer.chapter).all()

        weak_chapters = []
        for chapter, total, correct in rows:
            total = int(total or 0)
            correct = int(correct or 0)
            practiced_chapters.add(chapter)
            if total >= 3:  # 至少做过3题才评估
                acc = correct / total * 100 if total > 0 else 0
                if acc < 60:
                    weak_chapters.append((chapter, acc, total, correct))

        # 取正确率最低的3个章节
        weak_chapters.sort(key=lambda x: x[1])
        for chapter, acc, total, correct in weak_chapters[:3]:
            recommendations.append({
                'type': 'weak_chapter',
                'icon': 'bi-exclamation-triangle',
                'title': f'加强「{chapter}」',
                'desc': f'该章节正确率仅 {acc:.1f}%（{correct}/{total}），建议复习相关知识点',
                'link': f'/knowledge/?chapter={chapter}',
                'link_text': '复习知识',
                'priority': 2,
            })

    # 3) 未学习过的章节（题库中存在但用户从未做过）
    all_quiz_chapters = db.session.query(Quiz.chapter).filter(
        Quiz.chapter != None, Quiz.chapter != ''
    ).distinct().all()
    all_quiz_chapters = {r[0] for r in all_quiz_chapters}
    unlearned = sorted(all_quiz_chapters - practiced_chapters)
    for chapter in unlearned[:3]:
        recommendations.append({
            'type': 'new_chapter',
            'icon': 'bi-stars',
            'title': f'开始学习「{chapter}」',
            'desc': '你还未在该章节做过练习，开启新的学习之旅吧',
            'link': f'/quiz/practice',
            'link_text': '去练习',
            'priority': 3,
        })

    # 4) 若推荐为空，给一个默认鼓励
    if not recommendations:
        recommendations.append({
            'type': 'empty',
            'icon': 'bi-emoji-smile',
            'title': '继续保持',
            'desc': '暂无薄弱环节，继续保持良好的学习节奏！',
            'link': '/quiz/practice',
            'link_text': '继续刷题',
            'priority': 9,
        })

    recommendations.sort(key=lambda x: x['priority'])
    return jsonify({'success': True, 'items': recommendations})


@dashboard_bp.route('/api/recent-attempts')
@login_required
def api_recent_attempts():
    """最近5次刷题历史"""
    user = get_current_user()
    attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(
        QuizAttempt.started_at.desc()
    ).limit(5).all()

    mode_cn = {'practice': '章节练习', 'random': '随机刷题', 'exam': '模拟考试'}
    items = []
    for a in attempts:
        items.append({
            'id': a.id,
            'mode': a.mode,
            'mode_cn': mode_cn.get(a.mode, a.mode),
            'total_count': a.total_count,
            'correct_count': a.correct_count,
            'score': a.score,
            'duration': a.duration,
            'started_at': a.started_at.isoformat() if a.started_at else None,
            'finished_at': a.finished_at.isoformat() if a.finished_at else None,
            'is_finished': a.finished_at is not None,
        })

    return jsonify({'success': True, 'items': items})


@dashboard_bp.route('/api/achievements/stats')
@login_required
def api_achievements_stats():
    """获取用户成就统计"""
    user = get_current_user()
    stats = get_user_achievement_stats(user.id)
    return jsonify({'success': True, **stats})


@dashboard_bp.route('/api/achievements/list')
@login_required
def api_achievements_list():
    """获取用户的所有成就记录"""
    user = get_current_user()
    achievements = get_user_achievements(user.id)
    return jsonify({'success': True, 'items': achievements})


@dashboard_bp.route('/api/achievements/leaderboard')
@login_required
def api_achievements_leaderboard():
    """获取成就排行榜"""
    user = get_current_user()
    leaderboard = get_achievement_leaderboard(10)
    current_rank = None
    for i, item in enumerate(leaderboard):
        if item['user_id'] == user.id:
            current_rank = i + 1
            break
    
    return jsonify({
        'success': True,
        'items': leaderboard,
        'current_user_rank': current_rank,
        'current_user_points': get_user_achievement_stats(user.id)['points']
    })


@dashboard_bp.route('/api/achievements/share/<int:achievement_id>')
@login_required
def api_achievements_share(achievement_id):
    """生成成就分享内容"""
    user = get_current_user()
    share_data = share_achievement(user.id, achievement_id)
    if share_data:
        return jsonify({'success': True, **share_data})
    return jsonify({'success': False, 'message': '成就未解锁或不存在'})
