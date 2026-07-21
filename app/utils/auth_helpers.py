"""认证相关辅助函数与装饰器"""
from functools import wraps
from flask import session, g, redirect, url_for, flash, current_app


def get_current_user():
    """获取当前登录用户对象，未登录返回 None。
    优先从 g 对象读取（before_request 已注入），避免重复查询。
    """
    if getattr(g, 'user', None) is not None:
        return g.user

    user_id = session.get('user_id')
    if not user_id:
        return None

    from app.models import User
    user = User.query.get(user_id)
    g.user = user
    return user


def login_required(f):
    """登录验证装饰器：未登录跳转到登录页"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            flash('请先登录后再访问该页面。', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员验证装饰器：非管理员返回 403"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            flash('请先登录后再访问该页面。', 'warning')
            return redirect(url_for('auth.login'))
        if not user.is_admin:
            flash('无权访问该页面，仅管理员可访问。', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def get_user_api_config(user=None):
    """获取用户的 API 配置，返回字典。
    若用户未配置，回退到应用默认配置。

    返回字段：
        - provider: API提供商标识
        - provider_label: 中文名
        - api_key: 用户的API Key
        - model: 选择的模型
        - api_url: 对应的接口地址
    """
    if user is None:
        user = get_current_user()

    config = current_app.config
    provider_models = config.get('API_PROVIDER_DEFAULT_MODELS', {})
    provider_labels = config.get('API_PROVIDER_LABELS', {})

    provider = (user.api_provider if user and user.api_provider
                else config.get('DEFAULT_API_PROVIDER', 'qwen'))
    model = (user.api_model if user and user.api_model
             else provider_models.get(provider, config.get('DEFAULT_API_MODEL', 'qwen-plus')))
    api_key = user.api_key if user else None

    # 根据Provider取对应的接口URL
    url_map = {
        'qwen': config.get('QWEN_API_URL'),
        'deepseek': config.get('DEEPSEEK_API_URL'),
        'openai': config.get('OPENAI_API_URL'),
    }
    api_url = url_map.get(provider, config.get('QWEN_API_URL'))

    return {
        'provider': provider,
        'provider_label': provider_labels.get(provider, provider),
        'api_key': api_key,
        'model': model,
        'api_url': api_url,
    }
