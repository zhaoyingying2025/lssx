"""智能助教（对话式 AI 助教）路由蓝图"""
import json

from flask import Blueprint, render_template, request, jsonify, Response, stream_with_context

from app import db
from app.models import Conversation, Message
from app.utils.auth_helpers import login_required, get_current_user, get_user_api_config
from app.utils.ai_assistant import (
    search_knowledge,
    build_system_prompt,
    build_socratic_prompt,
    call_ai_api,
    call_ai_api_stream,
    generate_title,
)
from app.utils.achievement_service import record_chat

chat_bp = Blueprint('chat', __name__)


# ============ 页面 ============

@chat_bp.route('/')
@login_required
def index():
    """助教主页面：左侧对话列表 + 右侧聊天界面"""
    user = get_current_user()
    api_config = get_user_api_config(user)
    return render_template(
        'chat.html',
        api_configured=bool(user and user.api_key),
        provider_label=api_config.get('provider_label', '通义千问'),
        model_name=api_config.get('model', 'qwen-plus'),
    )


# ============ 对话列表 / 详情 ============

@chat_bp.route('/api/check-config')
@login_required
def check_config():
    """检查用户是否已配置 API Key"""
    user = get_current_user()
    api_config = get_user_api_config(user)
    return jsonify({
        'configured': bool(user and user.api_key),
        'provider_label': api_config.get('provider_label'),
        'model': api_config.get('model'),
    })


@chat_bp.route('/api/conversations', methods=['GET'])
@login_required
def list_conversations():
    """获取当前用户的所有对话列表"""
    user = get_current_user()
    convs = Conversation.query.filter_by(user_id=user.id) \
        .order_by(Conversation.updated_at.desc()).all()

    result = []
    for c in convs:
        result.append({
            'id': c.id,
            'title': c.title,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'updated_at': c.updated_at.isoformat() if c.updated_at else None,
        })
    return jsonify({'conversations': result})


@chat_bp.route('/api/conversations', methods=['POST'])
@login_required
def create_conversation():
    """新建对话"""
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '新对话').strip()[:200]

    conv = Conversation(user_id=user.id, title=title)
    db.session.add(conv)
    db.session.commit()
    return jsonify({
        'id': conv.id,
        'title': conv.title,
        'created_at': conv.created_at.isoformat() if conv.created_at else None,
    }), 201


@chat_bp.route('/api/conversations/<int:conv_id>/messages', methods=['GET'])
@login_required
def get_messages(conv_id):
    """获取某对话的所有消息"""
    user = get_current_user()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user.id).first()
    if conv is None:
        return jsonify({'error': '对话不存在'}), 404

    messages = Message.query.filter_by(conversation_id=conv_id) \
        .order_by(Message.created_at.asc()).all()

    result = []
    for m in messages:
        sources = None
        if m.sources:
            try:
                sources = json.loads(m.sources)
            except (ValueError, TypeError):
                sources = None
        result.append({
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'sources': sources,
            'created_at': m.created_at.isoformat() if m.created_at else None,
        })
    return jsonify({
        'conversation': {
            'id': conv.id,
            'title': conv.title,
        },
        'messages': result,
    })


@chat_bp.route('/api/conversations/<int:conv_id>/messages', methods=['POST'])
@login_required
def send_message(conv_id):
    """发送消息（非流式），返回 AI 回复。

    请求体: {"message": "用户输入"}
    """
    user = get_current_user()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user.id).first()
    if conv is None:
        return jsonify({'error': '对话不存在'}), 404

    data = request.get_json(silent=True) or {}
    content = (data.get('message') or '').strip()
    if not content:
        return jsonify({'error': '消息内容不能为空'}), 400

    # 检查 API 配置
    api_config = get_user_api_config(user)
    if not api_config.get('api_key'):
        return jsonify({
            'error': '尚未配置 API Key，请先到「用户设置」页面填写您的 API Key 后再使用助教。',
            'need_config': True,
        }), 403

    # 获取教学模式
    mode = data.get('mode', 'normal')

    # 1) 检索知识库
    knowledge_results = search_knowledge(content, limit=5)

    # 2) 保存用户消息
    user_msg = Message(conversation_id=conv.id, role='user', content=content)
    db.session.add(user_msg)

    # 若是第一条用户消息，自动生成标题
    existing_user_msgs = Message.query.filter_by(
        conversation_id=conv.id, role='user'
    ).count()
    if existing_user_msgs == 0:
        conv.title = generate_title(content)

    db.session.commit()

    # 3) 构建发送给 API 的消息列表（系统提示 + 历史消息 + 当前消息）
    if mode == 'socratic':
        system_prompt = build_socratic_prompt(knowledge_results)
    else:
        system_prompt = build_system_prompt(knowledge_results)
    history_msgs = Message.query.filter_by(conversation_id=conv.id) \
        .order_by(Message.created_at.asc()).all()

    api_messages = [{'role': 'system', 'content': system_prompt}]
    for m in history_msgs:
        api_messages.append({'role': m.role, 'content': m.content})

    # 4) 调用 AI
    reply_text, error = call_ai_api(api_config, api_messages)
    if error:
        return jsonify({'error': error, 'need_config': 'API Key' in error}), 502

    # 5) 保存 AI 回复（附带引用来源）
    sources_data = [
        {
            'id': k['id'],
            'title': k['title'],
            'chapter': k['chapter'],
            'section': k['section'],
        }
        for k in knowledge_results
    ]
    ai_msg = Message(
        conversation_id=conv.id,
        role='assistant',
        content=reply_text,
        sources=json.dumps(sources_data, ensure_ascii=False) if sources_data else None,
    )
    db.session.add(ai_msg)
    conv.updated_at = db.func.now()
    db.session.commit()

    try:
        record_chat(user.id)
    except Exception:
        pass

    return jsonify({
        'message': {
            'id': ai_msg.id,
            'role': 'assistant',
            'content': ai_msg.content,
            'sources': sources_data,
            'created_at': ai_msg.created_at.isoformat() if ai_msg.created_at else None,
        },
        'title': conv.title,
    })


@chat_bp.route('/api/conversations/<int:conv_id>/stream', methods=['POST'])
@login_required
def stream_message(conv_id):
    """流式发送消息（SSE）。

    请求体: {"message": "用户输入"}
    返回：text/event-stream，事件：
        - data: {"type":"sources","sources":[...]}  引用来源
        - data: {"type":"delta","content":"..."}      文本块
        - data: {"type":"title","title":"..."}        标题更新
        - data: {"type":"done","messageId":..}        结束
        - data: {"type":"error","message":"..."}      错误
    """
    user = get_current_user()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user.id).first()
    if conv is None:
        return jsonify({'error': '对话不存在'}), 404

    data = request.get_json(silent=True) or {}
    content = (data.get('message') or '').strip()
    if not content:
        return jsonify({'error': '消息内容不能为空'}), 400

    api_config = get_user_api_config(user)
    if not api_config.get('api_key'):
        return jsonify({
            'error': '尚未配置 API Key，请先到「用户设置」页面填写您的 API Key 后再使用助教。',
            'need_config': True,
        }), 403

    def sse(data_dict):
        """格式化为 SSE 事件"""
        return 'data: ' + json.dumps(data_dict, ensure_ascii=False) + '\n\n'

    @stream_with_context
    def generate():
        # 获取教学模式
        mode = data.get('mode', 'normal')

        # 1) 检索知识库
        knowledge_results = search_knowledge(content, limit=5)

        # 2) 保存用户消息
        user_msg = Message(conversation_id=conv.id, role='user', content=content)
        db.session.add(user_msg)

        existing_user_msgs = Message.query.filter_by(
            conversation_id=conv.id, role='user'
        ).count()
        is_first = (existing_user_msgs == 0)
        if is_first:
            new_title = generate_title(content)
            conv.title = new_title
        db.session.commit()

        # 推送引用来源（供前端展示）
        sources_data = [
            {
                'id': k['id'],
                'title': k['title'],
                'chapter': k['chapter'],
                'section': k['section'],
            }
            for k in knowledge_results
        ]
        yield sse({'type': 'sources', 'sources': sources_data})

        # 推送标题更新
        if is_first:
            yield sse({'type': 'title', 'title': conv.title})

        # 3) 构建消息列表（支持苏格拉底式教学模式）
        if mode == 'socratic':
            system_prompt = build_socratic_prompt(knowledge_results)
        else:
            system_prompt = build_system_prompt(knowledge_results)
        history_msgs = Message.query.filter_by(conversation_id=conv.id) \
            .order_by(Message.created_at.asc()).all()
        api_messages = [{'role': 'system', 'content': system_prompt}]
        for m in history_msgs:
            api_messages.append({'role': m.role, 'content': m.content})

        # 4) 流式调用 AI，逐块转发
        full_reply = []
        had_error = False
        for piece in call_ai_api_stream(api_config, api_messages):
            if piece.startswith('__ERROR__:'):
                had_error = True
                yield sse({'type': 'error', 'message': piece[len('__ERROR__:'):],
                           'need_config': 'API Key' in piece})
                break
            full_reply.append(piece)
            yield sse({'type': 'delta', 'content': piece})

        if had_error:
            return

        # 5) 保存 AI 回复
        reply_text = ''.join(full_reply)
        ai_msg = Message(
            conversation_id=conv.id,
            role='assistant',
            content=reply_text,
            sources=json.dumps(sources_data, ensure_ascii=False) if sources_data else None,
        )
        db.session.add(ai_msg)
        conv.updated_at = db.func.now()
        db.session.commit()

        try:
            record_chat(user.id)
        except Exception:
            pass

        yield sse({'type': 'done', 'messageId': ai_msg.id})

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache',
                             'X-Accel-Buffering': 'no',
                             'Connection': 'keep-alive'})


@chat_bp.route('/api/conversations/<int:conv_id>', methods=['DELETE'])
@login_required
def delete_conversation(conv_id):
    """删除对话及其所有消息"""
    user = get_current_user()
    conv = Conversation.query.filter_by(id=conv_id, user_id=user.id).first()
    if conv is None:
        return jsonify({'error': '对话不存在'}), 404

    Message.query.filter_by(conversation_id=conv.id).delete()
    db.session.delete(conv)
    db.session.commit()
    return jsonify({'success': True, 'message': '对话已删除'})
