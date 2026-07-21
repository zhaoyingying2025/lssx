"""AI 助教工具模块

提供知识库检索（RAG/GraphRAG）、系统提示词构建、AI API 调用（非流式 / 流式）以及
对话标题生成等能力。支持通义千问、DeepSeek、OpenAI 三种 OpenAI 兼容格式。
"""
import json

import requests
from sqlalchemy import or_

from app.models import KnowledgeItem


# ============ 知识库检索（RAG） ============

def search_knowledge(query, limit=5):
    """从知识库检索相关知识，用于 RAG。

    使用简单的关键词匹配：将查询按空白拆分为多个关键词，在标题 / 内容 /
    标签中匹配。命中关键词越多、且命中标题的条目排序越靠前。
    返回形如 [{id, title, content, chapter, section, tags}] 的列表。
    """
    if not query or not query.strip():
        return []

    query = query.strip()
    # 拆分关键词（中文按字符也作为兜底）
    keywords = [w for w in query.replace('，', ' ').replace('、', ' ').split() if w]
    if not keywords:
        keywords = [query]

    # 先用 LIKE 做粗筛，命中任一关键词（在标题/内容/标签中）即纳入候选
    conditions = []
    for kw in keywords:
        like = f'%{kw}%'
        conditions.append(or_(
            KnowledgeItem.title.like(like),
            KnowledgeItem.content.like(like),
            KnowledgeItem.tags.like(like),
        ))

    base_query = KnowledgeItem.query
    if len(conditions) == 1:
        base_query = base_query.filter(conditions[0])
    elif len(conditions) > 1:
        base_query = base_query.filter(or_(*conditions))

    candidates = base_query.all()

    # 计算相关性分数：标题命中权重最高，内容次之，标签最低
    def score(item):
        s = 0
        title = (item.title or '').lower()
        content = (item.content or '').lower()
        tags = (item.tags or '').lower()
        for kw in keywords:
            klc = kw.lower()
            if klc in title:
                s += 5
            if klc in content:
                s += 2
            if klc in tags:
                s += 3
        return s

    scored = [(it, score(it)) for it in candidates]
    # 过滤掉得分为 0 的（理论上 LIKE 已保证 >=1，这里做二次保险）
    scored = [pair for pair in scored if pair[1] > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for it, _ in scored[:limit]:
        results.append({
            'id': it.id,
            'title': it.title,
            'content': it.content or '',
            'chapter': it.chapter or '',
            'section': it.section or '',
            'tags': it.tags or '',
        })
    return results


# ============ 系统提示词 ============

def build_system_prompt(knowledge_results):
    """构建系统提示词，包含检索到的知识。

    告诉 AI 它是离散数学助教，并附上检索到的知识条目作为参考。
    """
    base_prompt = (
        '你是一位专业的离散数学助教，精通 Kenneth H. Rosen《离散数学及其应用》的全部内容，'
        '包括逻辑与证明、集合与函数、算法、数论与密码学、归纳与递归、计数、离散概率、'
        '高级计数技术、关系、图、树、布尔代数以及建模计算等主题。\n\n'
        '请遵循以下原则回答学生的问题：\n'
        '1. 使用中文回答，语言清晰、准确、易懂。\n'
        '2. 概念解释要严谨，必要时给出形式化定义，并辅以直观说明与示例。\n'
        '3. 涉及数学公式时，使用 LaTeX 语法书写：行内公式用 $...$，独立公式用 $$...$$。\n'
        '4. 适当使用 Markdown 排版（标题、列表、表格、代码块等），让回答结构清晰。\n'
        '5. 如果问题超出离散数学范畴，可以简要说明并尽量给出有帮助的引导。\n'
        '6. 不要编造不存在的知识；若不确定，请如实说明。'
    )

    if not knowledge_results:
        return base_prompt + '\n\n（本次未检索到直接相关的知识库条目，请依据你的离散数学专业知识回答。）'

    knowledge_text = '\n\n'.join(
        f'【知识条目 {idx}】\n标题：{item["title"]}\n'
        f'章节：{item["chapter"] or "未分类"}'
        f'{("  小节：" + item["section"]) if item["section"] else ""}\n'
        f'内容：{item["content"]}'
        for idx, item in enumerate(knowledge_results, 1)
    )

    return (
        base_prompt
        + '\n\n以下是知识库中检索到的相关参考资料，请优先依据这些内容作答，'
        '并可在其基础上进一步解释和拓展：\n\n'
        + knowledge_text
    )


def build_socratic_prompt(knowledge_results):
    """构建苏格拉底式教学系统提示词。

    采用引导性提问方式，帮助学生深入思考，而不是直接给出答案。
    """
    base_prompt = (
        '你是一位采用苏格拉底式教学法的离散数学导师。你的目标不是直接给出答案，'
        '而是通过引导性提问帮助学生自己思考、发现和理解概念。\n\n'
        '请遵循以下教学原则：\n'
        '1. 当学生提问时，不要直接回答，而是提出启发性问题引导他们思考。\n'
        '2. 从学生已有的知识出发，逐步引导到新知识。\n'
        '3. 鼓励学生反思自己的理解，发现潜在的误解。\n'
        '4. 当学生卡住时，提供适当的提示但不给出完整答案。\n'
        '5. 使用简单易懂的语言，避免过于复杂的术语。\n'
        '6. 保持耐心，让学生有时间思考和回答。\n'
        '7. 当学生表达正确理解时，给予肯定并进一步挑战。\n\n'
        '你的回答应该以提问为主，引导学生一步步深入理解离散数学概念。'
    )

    if not knowledge_results:
        return base_prompt + '\n\n（本次未检索到直接相关的知识库条目，请依据你的离散数学专业知识引导。）'

    knowledge_text = '\n\n'.join(
        f'【相关知识 {idx}】\n标题：{item["title"]}\n内容要点：{item["content"][:300]}...'
        for idx, item in enumerate(knowledge_results, 1)
    )

    return (
        base_prompt
        + '\n\n以下是相关的知识背景，请据此设计引导性问题：\n\n'
        + knowledge_text
    )


# ============ AI API 调用 ============

def _build_headers(api_config):
    return {
        'Authorization': f'Bearer {api_config.get("api_key", "")}',
        'Content-Type': 'application/json',
    }


def call_ai_api(api_config, messages, temperature=0.7):
    """调用 AI API（通义千问 / DeepSeek / OpenAI 兼容格式），非流式。

    api_config: get_user_api_config() 的返回值
    messages: [{role, content}]
    返回: (response_text, error) —— 成功时 error 为 None，失败时 response_text 为 None。
    """
    api_key = api_config.get('api_key')
    if not api_key:
        return None, '尚未配置 API Key，请先到「用户设置」页面填写您的 API Key。'

    api_url = api_config.get('api_url')
    model = api_config.get('model')
    if not api_url or not model:
        return None, 'API 配置不完整（缺少接口地址或模型名称）。'

    payload = {
        'model': model,
        'messages': messages,
        'stream': False,
        'temperature': temperature,
    }

    try:
        resp = requests.post(
            api_url,
            headers=_build_headers(api_config),
            json=payload,
            timeout=60,
        )
    except requests.exceptions.Timeout:
        return None, 'AI 接口请求超时，请稍后重试。'
    except requests.exceptions.ConnectionError:
        return None, '无法连接 AI 接口，请检查网络后重试。'
    except requests.exceptions.RequestException as e:
        return None, f'AI 接口请求失败：{e}'

    if resp.status_code != 200:
        # 尝试解析错误信息
        try:
            err_data = resp.json()
            err_msg = (err_data.get('error') or {}).get('message') \
                or err_data.get('message') \
                or resp.text[:200]
        except (ValueError, KeyError):
            err_msg = resp.text[:200] if resp.text else f'HTTP {resp.status_code}'
        return None, f'AI 接口返回错误（{resp.status_code}）：{err_msg}'

    try:
        data = resp.json()
        text = data['choices'][0]['message']['content']
        return text, None
    except (ValueError, KeyError, IndexError) as e:
        return None, f'解析 AI 接口响应失败：{e}'


def call_ai_api_stream(api_config, messages, temperature=0.7):
    """流式调用 AI API，生成器函数，逐块 yield 文本。

    遇到错误时 yield 一个以 '__ERROR__:' 开头的字符串，前端据此展示错误。
    """
    api_key = api_config.get('api_key')
    if not api_key:
        yield '__ERROR__:尚未配置 API Key，请先到「用户设置」页面填写您的 API Key。'
        return

    api_url = api_config.get('api_url')
    model = api_config.get('model')
    if not api_url or not model:
        yield '__ERROR__:API 配置不完整（缺少接口地址或模型名称）。'
        return

    payload = {
        'model': model,
        'messages': messages,
        'stream': True,
        'temperature': temperature,
    }

    try:
        resp = requests.post(
            api_url,
            headers=_build_headers(api_config),
            json=payload,
            timeout=90,
            stream=True,
        )
    except requests.exceptions.Timeout:
        yield '__ERROR__:AI 接口请求超时，请稍后重试。'
        return
    except requests.exceptions.ConnectionError:
        yield '__ERROR__:无法连接 AI 接口，请检查网络后重试。'
        return
    except requests.exceptions.RequestException as e:
        yield '__ERROR__:AI 接口请求失败：' + str(e)
        return

    if resp.status_code != 200:
        try:
            err_data = resp.json()
            err_msg = (err_data.get('error') or {}).get('message') \
                or err_data.get('message') \
                or resp.text[:200]
        except (ValueError, KeyError):
            err_msg = resp.text[:200] if resp.text else f'HTTP {resp.status_code}'
        yield '__ERROR__:AI 接口返回错误（%s）：%s' % (resp.status_code, err_msg)
        return

    # 解析 SSE 流：每行形如 "data: {json}"，流结束为 "data: [DONE]"
    try:
        for raw_line in resp.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            if not line.startswith('data:'):
                continue
            data_str = line[5:].strip()
            if data_str == '[DONE]':
                break
            try:
                chunk = json.loads(data_str)
            except (ValueError, json.JSONDecodeError):
                continue
            try:
                delta = chunk['choices'][0]['delta']
            except (KeyError, IndexError):
                continue
            piece = delta.get('content')
            if piece:
                yield piece
    except requests.exceptions.RequestException as e:
        yield '__ERROR__:读取 AI 响应流失败：' + str(e)


# ============ 对话标题生成 ============

def generate_title(first_message):
    """根据用户第一条消息生成对话标题：截取前 20 个字符。"""
    if not first_message:
        return '新对话'
    text = first_message.strip().replace('\n', ' ')
    if len(text) <= 20:
        return text
    return text[:20] + '…'
