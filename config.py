import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'discrete-math-teaching-secret-key-2024')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PDF教材路径
    PDF_BOOK_PATH = os.path.join(
        basedir,
        '附件一.离散数学及其应用 本科教学版 (（美）肯尼思·H.罗森（Kenneth H. Rosen）著 etc.)-电子书.pdf'
    )

    # PDF答案路径
    PDF_ANSWER_PATH = os.path.join(
        basedir,
        'Rosen_8e_Answers_to_Odd_Numbered_Exercises（奇数练习的答案）.pdf'
    )

    # AI助手默认配置
    DEFAULT_API_PROVIDER = 'qwen'
    DEFAULT_API_MODEL = 'qwen-plus'

    # 通义千问API配置
    QWEN_API_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
    QWEN_DEFAULT_MODEL = 'qwen-plus'

    # DeepSeek API配置
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
    DEEPSEEK_DEFAULT_MODEL = 'deepseek-chat'

    # OpenAI API配置
    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
    OPENAI_DEFAULT_MODEL = 'gpt-4o-mini'

    # 各Provider对应的默认模型映射，便于前端选择时自动填充
    API_PROVIDER_DEFAULT_MODELS = {
        'qwen': 'qwen-plus',
        'deepseek': 'deepseek-chat',
        'openai': 'gpt-4o-mini',
    }

    # 各Provider对应的中文显示名
    API_PROVIDER_LABELS = {
        'qwen': '通义千问',
        'deepseek': 'DeepSeek',
        'openai': 'OpenAI',
    }
