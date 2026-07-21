from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """用户"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    api_provider = db.Column(db.String(50), default='qwen')  # qwen/deepseek/openai
    api_key = db.Column(db.String(256))  # 用户自己的API Key
    api_model = db.Column(db.String(100), default='qwen-plus')  # 用户选择的模型
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """设置密码（自动生成哈希）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """校验密码"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class KnowledgeItem(db.Model):
    """知识条目"""
    __tablename__ = 'knowledge_items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    chapter = db.Column(db.String(100))
    section = db.Column(db.String(100))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(500))
    source = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<KnowledgeItem {self.title}>'


class Quiz(db.Model):
    """试题"""
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.String(100))
    section = db.Column(db.String(100))
    question_number = db.Column(db.Integer)  # 题号（如 1, 3, 5 等奇数编号）
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='choice')  # choice/fill/proof/calc/true_false/short_answer
    options = db.Column(db.Text)  # JSON格式存储选项
    answer = db.Column(db.Text, nullable=False)
    answer_cn = db.Column(db.Text)  # 中文答案翻译
    difficulty = db.Column(db.String(10), default='medium')  # easy/medium/hard
    source_page = db.Column(db.Integer)
    tags = db.Column(db.String(500))  # 知识点标签，多个用逗号分隔
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Quiz {self.id}: {self.question_text[:30]}>'


class Courseware(db.Model):
    """课件"""
    __tablename__ = 'coursewares'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    mode = db.Column(db.String(10), default='html')  # html 或 ppt
    content_json = db.Column(db.Text)  # JSON格式存储课件内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Courseware {self.title}>'


class Graph(db.Model):
    """图形画板数据"""
    __tablename__ = 'graphs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), default='graph')  # graph 或 tree
    data_json = db.Column(db.Text)  # JSON格式存储图形数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Graph {self.name}>'


class ExamPaper(db.Model):
    """试卷"""
    __tablename__ = 'exam_papers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    chapters_json = db.Column(db.Text)  # JSON格式存储章节列表
    question_types_json = db.Column(db.Text)  # JSON格式存储题型列表
    difficulty_json = db.Column(db.Text)  # JSON格式存储难度分布
    total_count = db.Column(db.Integer, default=0)
    include_answers = db.Column(db.Boolean, default=True)
    answer_language = db.Column(db.String(10), default='cn')  # cn/en/both
    questions_json = db.Column(db.Text)  # JSON格式存储试卷题目数据
    pdf_path = db.Column(db.String(500))  # PDF文件路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExamPaper {self.title}>'


class Conversation(db.Model):
    """对话"""
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), default='新对话')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(db.Model):
    """对话消息"""
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user/assistant
    content = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text)  # JSON格式，引用的知识条目
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class QuizAttempt(db.Model):
    """做题记录"""
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mode = db.Column(db.String(20), default='practice')  # practice/random/exam
    total_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0)  # 百分制得分
    duration = db.Column(db.Integer, default=0)  # 用时(秒)
    chapters_json = db.Column(db.Text)  # 练习范围
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<QuizAttempt {self.id} user={self.user_id} mode={self.mode}>'


class QuizAnswer(db.Model):
    """每道题的作答记录"""
    __tablename__ = 'quiz_answers'
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    question_type = db.Column(db.String(20))
    difficulty = db.Column(db.String(10))
    chapter = db.Column(db.String(100))
    tags = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<QuizAnswer {self.id} attempt={self.attempt_id} quiz={self.quiz_id}>'


class WrongQuestion(db.Model):
    """错题本"""
    __tablename__ = 'wrong_questions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_answer = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    wrong_count = db.Column(db.Integer, default=1)  # 答错次数
    is_mastered = db.Column(db.Boolean, default=False)  # 是否已掌握（移出错题本）
    note = db.Column(db.Text)  # 用户笔记
    tags = db.Column(db.String(500))
    chapter = db.Column(db.String(100))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime)  # 最后复习时间
    next_review = db.Column(db.DateTime)  # 下次复习时间（艾宾浩斯曲线）

    def __repr__(self):
        return f'<WrongQuestion {self.id} user={self.user_id} quiz={self.quiz_id}>'


class Example(db.Model):
    """例题"""
    __tablename__ = 'examples'
    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.String(100))
    knowledge_item_id = db.Column(db.Integer, db.ForeignKey('knowledge_items.id'))
    title = db.Column(db.String(200), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='calc')  # choice/fill/calc/proof
    difficulty = db.Column(db.String(10), default='medium')  # easy/medium/hard
    steps_json = db.Column(db.Text)  # JSON格式存储分步解析
    answer = db.Column(db.Text)
    summary = db.Column(db.Text)  # 方法总结
    graph_data = db.Column(db.Text)  # JSON格式存储关联图形数据（可选，用于画板联动）
    tags = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Example {self.id}: {self.title[:30]}>'


class Achievement(db.Model):
    """成就/徽章"""
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # FontAwesome图标类名
    type = db.Column(db.String(50), default='badge')  # badge/trophy/medal
    rarity = db.Column(db.String(20), default='common')  # common/rare/epic/legendary
    condition_type = db.Column(db.String(50))  # quiz_count/correct_rate/knowledge_complete/proof_complete/graph_algorithm
    condition_value = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Achievement {self.name}>'


class UserAchievement(db.Model):
    """用户成就记录"""
    __tablename__ = 'user_achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)
    is_unlocked = db.Column(db.Boolean, default=False)
    unlocked_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserAchievement user={self.user_id} achievement={self.achievement_id}>'
