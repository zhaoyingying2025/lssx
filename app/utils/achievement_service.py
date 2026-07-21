from datetime import datetime
from app import db
from app.models import Achievement, UserAchievement, QuizAnswer, QuizAttempt, WrongQuestion


def get_or_create_user_achievement(user_id, achievement_id):
    """获取或创建用户成就记录"""
    ua = UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement_id).first()
    if not ua:
        ua = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            progress=0,
            is_unlocked=False
        )
        db.session.add(ua)
    return ua


def unlock_achievement(user_id, achievement_id):
    """解锁成就"""
    ua = get_or_create_user_achievement(user_id, achievement_id)
    if not ua.is_unlocked:
        ua.is_unlocked = True
        ua.unlocked_at = datetime.utcnow()
        db.session.commit()
        return True
    return False


def update_progress(user_id, achievement_id, progress):
    """更新成就进度"""
    ua = get_or_create_user_achievement(user_id, achievement_id)
    ua.progress = progress
    db.session.commit()


def check_and_update_achievements(user_id):
    """检查并更新所有成就进度"""
    updated_achievements = []
    achievements = Achievement.query.all()

    for ach in achievements:
        if ach.condition_type == 'quiz_count':
            count = QuizAnswer.query.filter(QuizAnswer.attempt_id.in_(
                db.session.query(QuizAttempt.id).filter(QuizAttempt.user_id == user_id).subquery()
            )).count()
            update_progress(user_id, ach.id, count)
            if count >= ach.condition_value:
                if unlock_achievement(user_id, ach.id):
                    updated_achievements.append(ach.name)

        elif ach.condition_type == 'correct_rate':
            attempt_ids = [r[0] for r in db.session.query(QuizAttempt.id).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.finished_at != None
            ).all()]
            if attempt_ids:
                total = QuizAnswer.query.filter(QuizAnswer.attempt_id.in_(attempt_ids)).count()
                correct = QuizAnswer.query.filter(
                    QuizAnswer.attempt_id.in_(attempt_ids),
                    QuizAnswer.is_correct == True
                ).count()
                rate = round(correct / total * 100, 1) if total > 0 else 0
                update_progress(user_id, ach.id, int(rate))
                if rate >= ach.condition_value:
                    if unlock_achievement(user_id, ach.id):
                        updated_achievements.append(ach.name)

        elif ach.condition_type == 'knowledge_complete':
            count = 0
            updated_achievements.append(ach.name)

        elif ach.condition_type == 'proof_complete':
            count = 0
            update_progress(user_id, ach.id, count)
            if count >= ach.condition_value:
                if unlock_achievement(user_id, ach.id):
                    updated_achievements.append(ach.name)

        elif ach.condition_type == 'graph_algorithm':
            count = 0
            update_progress(user_id, ach.id, count)
            if count >= ach.condition_value:
                if unlock_achievement(user_id, ach.id):
                    updated_achievements.append(ach.name)

        elif ach.condition_type == 'chat_count':
            count = 0
            update_progress(user_id, ach.id, count)
            if count >= ach.condition_value:
                if unlock_achievement(user_id, ach.id):
                    updated_achievements.append(ach.name)

        elif ach.condition_type == 'wrong_mastered':
            count = WrongQuestion.query.filter_by(user_id=user_id, is_mastered=True).count()
            update_progress(user_id, ach.id, count)
            if count >= ach.condition_value:
                if unlock_achievement(user_id, ach.id):
                    updated_achievements.append(ach.name)

        elif ach.condition_type == 'achievements_unlocked':
            unlocked_count = UserAchievement.query.filter_by(user_id=user_id, is_unlocked=True).count()
            update_progress(user_id, ach.id, unlocked_count)
            if unlocked_count >= ach.condition_value:
                if unlock_achievement(user_id, ach.id):
                    updated_achievements.append(ach.name)

    if updated_achievements:
        db.session.commit()

    return updated_achievements


def record_quiz_submit(user_id, is_correct):
    """记录答题提交，更新相关成就"""
    achievements = Achievement.query.filter(Achievement.condition_type.in_(['quiz_count', 'correct_rate'])).all()

    for ach in achievements:
        ua = get_or_create_user_achievement(user_id, ach.id)

        if ach.condition_type == 'quiz_count':
            ua.progress += 1
            if ua.progress >= ach.condition_value and not ua.is_unlocked:
                ua.is_unlocked = True
                ua.unlocked_at = datetime.utcnow()

        elif ach.condition_type == 'correct_rate':
            attempt_ids = [r[0] for r in db.session.query(QuizAttempt.id).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.finished_at != None
            ).all()]
            if attempt_ids:
                total = QuizAnswer.query.filter(QuizAnswer.attempt_id.in_(attempt_ids)).count()
                correct = QuizAnswer.query.filter(
                    QuizAnswer.attempt_id.in_(attempt_ids),
                    QuizAnswer.is_correct == True
                ).count()
                rate = round(correct / total * 100, 1) if total > 0 else 0
                ua.progress = int(rate)
                if rate >= ach.condition_value and not ua.is_unlocked:
                    ua.is_unlocked = True
                    ua.unlocked_at = datetime.utcnow()

    db.session.commit()


def record_quiz_finish(user_id, score):
    """记录刷题完成，更新正确率相关成就"""
    achievements = Achievement.query.filter_by(condition_type='correct_rate').all()

    for ach in achievements:
        ua = get_or_create_user_achievement(user_id, ach.id)

        attempt_ids = [r[0] for r in db.session.query(QuizAttempt.id).filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.finished_at != None
        ).all()]

        if attempt_ids:
            total = QuizAnswer.query.filter(QuizAnswer.attempt_id.in_(attempt_ids)).count()
            correct = QuizAnswer.query.filter(
                QuizAnswer.attempt_id.in_(attempt_ids),
                QuizAnswer.is_correct == True
            ).count()
            rate = round(correct / total * 100, 1) if total > 0 else 0
            ua.progress = int(rate)
            if rate >= ach.condition_value and not ua.is_unlocked:
                ua.is_unlocked = True
                ua.unlocked_at = datetime.utcnow()

    db.session.commit()


def record_knowledge_read(user_id, knowledge_id):
    """记录知识阅读，更新知识探索相关成就"""
    achievements = Achievement.query.filter_by(condition_type='knowledge_complete').all()

    for ach in achievements:
        ua = get_or_create_user_achievement(user_id, ach.id)
        ua.progress += 1
        if ua.progress >= ach.condition_value and not ua.is_unlocked:
            ua.is_unlocked = True
            ua.unlocked_at = datetime.utcnow()

    db.session.commit()


def record_proof_complete(user_id, proof_id):
    """记录证明完成，更新证明相关成就"""
    achievements = Achievement.query.filter_by(condition_type='proof_complete').all()

    for ach in achievements:
        ua = get_or_create_user_achievement(user_id, ach.id)
        ua.progress += 1
        if ua.progress >= ach.condition_value and not ua.is_unlocked:
            ua.is_unlocked = True
            ua.unlocked_at = datetime.utcnow()

    db.session.commit()


def record_graph_algorithm(user_id, algorithm_name):
    """记录图论算法使用，更新图论相关成就"""
    achievements = Achievement.query.filter_by(condition_type='graph_algorithm').all()

    for ach in achievements:
        ua = get_or_create_user_achievement(user_id, ach.id)
        ua.progress += 1
        if ua.progress >= ach.condition_value and not ua.is_unlocked:
            ua.is_unlocked = True
            ua.unlocked_at = datetime.utcnow()

    db.session.commit()


def record_chat(user_id):
    """记录聊天次数，更新AI对话相关成就"""
    achievements = Achievement.query.filter_by(condition_type='chat_count').all()

    for ach in achievements:
        ua = get_or_create_user_achievement(user_id, ach.id)
        ua.progress += 1
        if ua.progress >= ach.condition_value and not ua.is_unlocked:
            ua.is_unlocked = True
            ua.unlocked_at = datetime.utcnow()

    db.session.commit()


def record_wrong_mastered(user_id):
    """记录掌握错题，更新错题克星成就"""
    achievements = Achievement.query.filter_by(condition_type='wrong_mastered').all()

    for ach in achievements:
        ua = get_or_create_user_achievement(user_id, ach.id)
        ua.progress = WrongQuestion.query.filter_by(user_id=user_id, is_mastered=True).count()
        if ua.progress >= ach.condition_value and not ua.is_unlocked:
            ua.is_unlocked = True
            ua.unlocked_at = datetime.utcnow()

    db.session.commit()


def get_user_achievements(user_id):
    """获取用户的所有成就记录（包含成就详情）"""
    user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
    achievement_ids = [ua.achievement_id for ua in user_achievements]
    achievements = Achievement.query.filter(Achievement.id.in_(achievement_ids)).all()
    achievement_map = {a.id: a for a in achievements}

    result = []
    for ua in user_achievements:
        ach = achievement_map.get(ua.achievement_id)
        if ach:
            result.append({
                'id': ach.id,
                'name': ach.name,
                'description': ach.description,
                'icon': ach.icon,
                'type': ach.type,
                'rarity': ach.rarity,
                'condition_type': ach.condition_type,
                'condition_value': ach.condition_value,
                'points': ach.points,
                'progress': ua.progress,
                'is_unlocked': ua.is_unlocked,
                'unlocked_at': ua.unlocked_at.isoformat() if ua.unlocked_at else None,
            })

    all_achievements = Achievement.query.all()
    for ach in all_achievements:
        if ach.id not in achievement_map:
            result.append({
                'id': ach.id,
                'name': ach.name,
                'description': ach.description,
                'icon': ach.icon,
                'type': ach.type,
                'rarity': ach.rarity,
                'condition_type': ach.condition_type,
                'condition_value': ach.condition_value,
                'points': ach.points,
                'progress': 0,
                'is_unlocked': False,
                'unlocked_at': None,
            })

    result.sort(key=lambda x: x['is_unlocked'], reverse=True)
    return result


def get_user_achievement_stats(user_id):
    """获取用户成就统计"""
    total = Achievement.query.count()
    unlocked = UserAchievement.query.filter_by(user_id=user_id, is_unlocked=True).count()
    points = 0
    user_achievements = UserAchievement.query.filter_by(user_id=user_id, is_unlocked=True).all()
    for ua in user_achievements:
        ach = Achievement.query.get(ua.achievement_id)
        if ach:
            points += ach.points

    return {
        'total': total,
        'unlocked': unlocked,
        'locked': total - unlocked,
        'points': points,
        'progress': round(unlocked / total * 100, 1) if total > 0 else 0,
    }


def get_achievement_leaderboard(limit=10):
    """获取成就排行榜（按积分排名）"""
    from app.models import User
    user_stats = []
    
    users = User.query.all()
    for user in users:
        stats = get_user_achievement_stats(user.id)
        user_stats.append({
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
            'points': stats['points'],
            'unlocked': stats['unlocked'],
            'total': stats['total'],
            'progress': stats['progress'],
        })
    
    user_stats.sort(key=lambda x: x['points'], reverse=True)
    return user_stats[:limit]


def share_achievement(user_id, achievement_id):
    """生成成就分享内容"""
    ua = UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement_id).first()
    if not ua or not ua.is_unlocked:
        return None
    
    achievement = Achievement.query.get(achievement_id)
    if not achievement:
        return None
    
    return {
        'user_id': user_id,
        'achievement_id': achievement_id,
        'achievement_name': achievement.name,
        'achievement_icon': achievement.icon,
        'achievement_rarity': achievement.rarity,
        'achievement_points': achievement.points,
        'unlocked_at': ua.unlocked_at.isoformat() if ua.unlocked_at else None,
        'share_text': f'我解锁了「{achievement.name}」成就！获得{achievement.points}积分，快来挑战吧！',
    }