"""管理后台路由：首页统计、用户管理"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func, or_

from app import db
from app.models import User, KnowledgeItem, Quiz, Courseware, Graph, ExamPaper
from app.utils.auth_helpers import admin_required, get_current_user

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@admin_required
def index():
    """管理后台首页：统计数据"""
    stats = {
        'users': User.query.count(),
        'admins': User.query.filter_by(is_admin=True).count(),
        'knowledge': KnowledgeItem.query.count(),
        'quizzes': Quiz.query.count(),
        'coursewares': Courseware.query.count(),
        'graphs': Graph.query.count(),
        'exam_papers': ExamPaper.query.count(),
    }

    # 最近注册的 5 位用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    # 各章节知识条目分布（用于柱状图）
    chapter_rows = (
        db.session.query(KnowledgeItem.chapter, func.count(KnowledgeItem.id))
        .filter(KnowledgeItem.chapter.isnot(None))
        .group_by(KnowledgeItem.chapter)
        .order_by(func.count(KnowledgeItem.id).desc())
        .limit(8)
        .all()
    )
    chart_chapters = [row[0] or '未分类' for row in chapter_rows]
    chart_counts = [row[1] for row in chapter_rows]

    # 各题型数量（用于饼图）
    quiz_type_rows = (
        db.session.query(Quiz.question_type, func.count(Quiz.id))
        .group_by(Quiz.question_type)
        .all()
    )
    quiz_type_labels = [row[0] or '未分类' for row in quiz_type_rows]
    quiz_type_counts = [row[1] for row in quiz_type_rows]

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        chart_chapters=chart_chapters,
        chart_counts=chart_counts,
        quiz_type_labels=quiz_type_labels,
        quiz_type_counts=quiz_type_counts,
    )


@admin_bp.route('/users')
@admin_required
def users():
    """用户列表"""
    keyword = (request.args.get('keyword') or '').strip()
    query = User.query
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            or_(User.username.like(like), User.email.like(like))
        )
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users, keyword=keyword)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        is_admin = request.form.get('is_admin') == 'on'
        api_provider = request.form.get('api_provider') or user.api_provider
        api_model = (request.form.get('api_model') or '').strip()
        api_key = (request.form.get('api_key') or '').strip()

        if email and '@' not in email:
            flash('邮箱格式不正确。', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user.id))

        user.email = email or None
        user.is_admin = is_admin
        if api_provider in ('qwen', 'deepseek', 'openai'):
            user.api_provider = api_provider
        if api_model:
            user.api_model = api_model
        if api_key:
            user.api_key = api_key

        # 可选：重置密码（管理员设置新密码）
        new_password = request.form.get('new_password') or ''
        if new_password:
            if len(new_password) < 6:
                flash('新密码长度至少 6 位。', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user.id))
            user.set_password(new_password)

        db.session.commit()
        flash(f'用户 {user.username} 信息已更新。', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/edit_user.html', edit_user=user)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """切换用户管理员状态"""
    user = User.query.get_or_404(user_id)
    current = get_current_user()
    if current is not None and current.id == user.id:
        flash('不能修改自己的管理员状态。', 'warning')
        return redirect(url_for('admin.users'))

    user.is_admin = not user.is_admin
    db.session.commit()
    status = '授予' if user.is_admin else '撤销'
    flash(f'已{status}用户 {user.username} 的管理员权限。', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    current = get_current_user()
    if current is not None and current.id == user.id:
        flash('不能删除当前登录的账号。', 'warning')
        return redirect(url_for('admin.users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'用户 {username} 已删除。', 'success')
    return redirect(url_for('admin.users'))
