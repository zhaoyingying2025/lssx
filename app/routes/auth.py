"""认证路由：注册、登录、退出、用户设置"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

from app import db
from app.models import User
from app.utils.auth_helpers import login_required, get_current_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    # 若已登录，直接跳转首页
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm_password') or ''
        email = (request.form.get('email') or '').strip()

        # 基础校验
        if not username or not password:
            flash('用户名和密码不能为空。', 'danger')
            return redirect(url_for('auth.register'))
        if len(username) < 3 or len(username) > 80:
            flash('用户名长度需为 3-80 个字符。', 'danger')
            return redirect(url_for('auth.register'))
        if len(password) < 6:
            flash('密码长度至少 6 位。', 'danger')
            return redirect(url_for('auth.register'))
        if password != confirm:
            flash('两次输入的密码不一致。', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('该用户名已被注册，请更换。', 'danger')
            return redirect(url_for('auth.register'))

        # 邮箱可选，但若填写则简单校验格式
        if email and '@' not in email:
            flash('邮箱格式不正确。', 'danger')
            return redirect(url_for('auth.register'))

        # 创建用户
        user = User(username=username, email=email or None)
        user.set_password(password)

        # 第一个注册的用户自动成为管理员
        if User.query.count() == 0:
            user.is_admin = True
            user.api_provider = current_app.config.get('DEFAULT_API_PROVIDER', 'qwen')
            user.api_model = current_app.config.get('DEFAULT_API_MODEL', 'qwen-plus')

        db.session.add(user)
        db.session.commit()

        # 注册成功后自动登录
        session.clear()
        session['user_id'] = user.id
        flash(f'注册成功，欢迎加入，{user.username}！', 'success')
        if user.is_admin:
            flash('您是首位注册用户，已自动成为管理员。', 'info')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    # 若已登录，直接跳转首页
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        if not username or not password:
            flash('请输入用户名和密码。', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('用户名或密码错误。', 'danger')
            return redirect(url_for('auth.login'))

        session.clear()
        session['user_id'] = user.id
        flash(f'欢迎回来，{user.username}！', 'success')

        # 跳转到 next 或首页
        next_url = request.args.get('next') or request.form.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('您已安全退出登录。', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """用户设置：修改密码、配置 API Key、选择模型"""
    user = get_current_user()

    if request.method == 'POST':
        action = request.form.get('action', 'api')

        if action == 'password':
            # 修改密码
            old_password = request.form.get('old_password') or ''
            new_password = request.form.get('new_password') or ''
            confirm = request.form.get('confirm_password') or ''

            if not user.check_password(old_password):
                flash('原密码不正确。', 'danger')
                return redirect(url_for('auth.settings'))
            if len(new_password) < 6:
                flash('新密码长度至少 6 位。', 'danger')
                return redirect(url_for('auth.settings'))
            if new_password != confirm:
                flash('两次输入的新密码不一致。', 'danger')
                return redirect(url_for('auth.settings'))

            user.set_password(new_password)
            db.session.commit()
            flash('密码修改成功。', 'success')
            return redirect(url_for('auth.settings'))

        elif action == 'profile':
            # 修改基本资料（邮箱）
            email = (request.form.get('email') or '').strip()
            if email and '@' not in email:
                flash('邮箱格式不正确。', 'danger')
                return redirect(url_for('auth.settings'))
            user.email = email or None
            db.session.commit()
            flash('个人资料已更新。', 'success')
            return redirect(url_for('auth.settings'))

        else:
            # 默认：保存 API 配置
            provider = request.form.get('api_provider') or 'qwen'
            api_key = (request.form.get('api_key') or '').strip()
            api_model = (request.form.get('api_model') or '').strip()

            if provider not in ('qwen', 'deepseek', 'openai'):
                flash('不支持的 API 服务商。', 'danger')
                return redirect(url_for('auth.settings'))

            # 若用户未填写模型名，则使用该Provider的默认模型
            if not api_model:
                api_model = current_app.config.get(
                    'API_PROVIDER_DEFAULT_MODELS', {}
                ).get(provider, current_app.config.get('DEFAULT_API_MODEL', 'qwen-plus'))

            user.api_provider = provider
            # 若 API Key 留空则不覆盖（保留原值）
            if api_key:
                user.api_key = api_key
            user.api_model = api_model
            db.session.commit()
            flash('API 配置已保存。', 'success')
            return redirect(url_for('auth.settings'))

    # GET：渲染设置页
    provider_models = current_app.config.get('API_PROVIDER_DEFAULT_MODELS', {})
    provider_labels = current_app.config.get('API_PROVIDER_LABELS', {})
    return render_template(
        'auth/settings.html',
        user=user,
        provider_models=provider_models,
        provider_labels=provider_labels,
    )
