from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes.main import main_bp
    from app.routes.knowledge import knowledge_bp
    from app.routes.canvas import canvas_bp
    from app.routes.courseware import courseware_bp
    from app.routes.quiz import quiz_bp
    from app.routes.innovation import innovation_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.chat import chat_bp
    from app.routes.wrong_book import wrong_book_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge')
    app.register_blueprint(canvas_bp, url_prefix='/canvas')
    app.register_blueprint(courseware_bp, url_prefix='/courseware')
    app.register_blueprint(quiz_bp, url_prefix='/quiz')
    app.register_blueprint(innovation_bp, url_prefix='/innovation')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(wrong_book_bp, url_prefix='/wrong-book')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    @app.before_request
    def _inject_current_user():
        """在每个请求前注入 current_user 到 g 对象，供模板使用。"""
        user_id = session.get('user_id')
        if user_id:
            from app.models import User
            g.user = User.query.get(user_id)
        else:
            g.user = None

    @app.context_processor
    def _inject_current_user_to_template():
        """让 current_user 在所有模板中可用。"""
        from app.utils.auth_helpers import get_current_user
        return {'current_user': get_current_user()}

    with app.app_context():
        from app import models
        db.create_all()
        # 为已存在的表补充新增字段（SQLite 不支持 db.create_all 自动加列）
        _migrate_exam_papers(db)
        _migrate_quizzes(db)
        _migrate_users(db)
        _migrate_chat_tables(db)
        _migrate_practice_tables(db)
        _migrate_wrong_book_tables(db)
        _migrate_dashboard_tables(db)
        _migrate_examples(db)
        _migrate_courseware_mode(db)
        _migrate_achievements(db)
        _init_achievements(db)

    return app


def _migrate_exam_papers(db):
    """确保 exam_papers 表存在。db.create_all() 会处理新表创建，此函数作为安全保障。"""
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    if 'exam_papers' not in inspector.get_table_names():
        # db.create_all 应该已经创建了，但以防万一
        pass


def _migrate_quizzes(db):
    """为 quizzes 表补充新增字段（tags），并移除已废弃字段（confidence、match_status）。"""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if 'quizzes' not in inspector.get_table_names():
        return
    existing_cols = {c['name'] for c in inspector.get_columns('quizzes')}
    with db.engine.begin() as conn:
        if 'tags' not in existing_cols:
            conn.execute(text('ALTER TABLE quizzes ADD COLUMN tags VARCHAR(500)'))
        # 移除题库中不再使用的置信度和匹配状态字段
        if 'confidence' in existing_cols:
            conn.execute(text('ALTER TABLE quizzes DROP COLUMN confidence'))
        if 'match_status' in existing_cols:
            conn.execute(text('ALTER TABLE quizzes DROP COLUMN match_status'))


def _migrate_users(db):
    """为 users 表补充新增字段，若已存在则跳过。
    首次运行时 db.create_all() 会自动创建 users 表；此函数用于在表已存在但缺少字段时做安全迁移。
    """
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        return
    existing_cols = {c['name'] for c in inspector.get_columns('users')}
    # 定义 users 表可能需要补充的字段（含类型），用于 ALTER TABLE
    candidate_cols = {
        'username': 'VARCHAR(80)',
        'email': 'VARCHAR(120)',
        'password_hash': 'VARCHAR(256)',
        'is_admin': 'BOOLEAN DEFAULT 0',
        'api_provider': "VARCHAR(50) DEFAULT 'qwen'",
        'api_key': 'VARCHAR(256)',
        'api_model': "VARCHAR(100) DEFAULT 'qwen-plus'",
        'created_at': 'DATETIME',
    }
    with db.engine.begin() as conn:
        for col, col_type in candidate_cols.items():
            if col not in existing_cols:
                conn.execute(text(f'ALTER TABLE users ADD COLUMN {col} {col_type}'))


def _migrate_chat_tables(db):
    """确保对话相关表（conversations / messages）存在。

    db.create_all() 会自动创建新表，此函数作为安全保障：
    当数据库已存在但缺少对话表时显式建表，避免历史库未触发 create_all。
    """
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    with db.engine.begin() as conn:
        if 'conversations' not in existing_tables:
            conn.execute(text(
                'CREATE TABLE conversations ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'user_id INTEGER NOT NULL REFERENCES users(id), '
                'title VARCHAR(200), '
                'created_at DATETIME, '
                'updated_at DATETIME)'
            ))
        if 'messages' not in existing_tables:
            conn.execute(text(
                'CREATE TABLE messages ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'conversation_id INTEGER NOT NULL REFERENCES conversations(id), '
                'role VARCHAR(20) NOT NULL, '
                'content TEXT NOT NULL, '
                'sources TEXT, '
                'created_at DATETIME)'
            ))


def _migrate_practice_tables(db):
    """确保在线刷题相关表（quiz_attempts / quiz_answers）存在。

    db.create_all() 会自动创建新表，此函数作为安全保障：
    当数据库已存在但缺少刷题表时显式建表，避免历史库未触发 create_all。
    """
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    with db.engine.begin() as conn:
        if 'quiz_attempts' not in existing_tables:
            conn.execute(text(
                'CREATE TABLE quiz_attempts ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'user_id INTEGER NOT NULL REFERENCES users(id), '
                "mode VARCHAR(20) DEFAULT 'practice', "
                'total_count INTEGER DEFAULT 0, '
                'correct_count INTEGER DEFAULT 0, '
                'score FLOAT DEFAULT 0, '
                'duration INTEGER DEFAULT 0, '
                'chapters_json TEXT, '
                'started_at DATETIME, '
                'finished_at DATETIME)'
            ))
        if 'quiz_answers' not in existing_tables:
            conn.execute(text(
                'CREATE TABLE quiz_answers ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'attempt_id INTEGER NOT NULL REFERENCES quiz_attempts(id), '
                'quiz_id INTEGER NOT NULL REFERENCES quizzes(id), '
                'user_answer TEXT, '
                'is_correct BOOLEAN, '
                'question_type VARCHAR(20), '
                'difficulty VARCHAR(10), '
                'chapter VARCHAR(100), '
                'tags VARCHAR(500), '
                'created_at DATETIME)'
            ))


def _migrate_wrong_book_tables(db):
    """确保错题本表（wrong_questions）存在，并补全新增字段。

    db.create_all() 会自动创建新表，此函数作为安全保障：
    当数据库已存在但缺少错题本表时显式建表；若表已存在但缺少字段则 ALTER TABLE 补列。
    """
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    with db.engine.begin() as conn:
        if 'wrong_questions' not in existing_tables:
            conn.execute(text(
                'CREATE TABLE wrong_questions ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'user_id INTEGER NOT NULL REFERENCES users(id), '
                'quiz_id INTEGER NOT NULL REFERENCES quizzes(id), '
                'user_answer TEXT, '
                'correct_answer TEXT, '
                'wrong_count INTEGER DEFAULT 1, '
                'is_mastered BOOLEAN DEFAULT 0, '
                'note TEXT, '
                'tags VARCHAR(500), '
                'chapter VARCHAR(100), '
                'added_at DATETIME, '
                'last_reviewed DATETIME, '
                'next_review DATETIME)'
            ))
            return

        # 表已存在：补全可能缺失的字段
        existing_cols = {c['name'] for c in inspector.get_columns('wrong_questions')}
        candidate_cols = {
            'user_id': 'INTEGER NOT NULL REFERENCES users(id)',
            'quiz_id': 'INTEGER NOT NULL REFERENCES quizzes(id)',
            'user_answer': 'TEXT',
            'correct_answer': 'TEXT',
            'wrong_count': 'INTEGER DEFAULT 1',
            'is_mastered': 'BOOLEAN DEFAULT 0',
            'note': 'TEXT',
            'tags': 'VARCHAR(500)',
            'chapter': 'VARCHAR(100)',
            'added_at': 'DATETIME',
            'last_reviewed': 'DATETIME',
            'next_review': 'DATETIME',
        }
        for col, col_type in candidate_cols.items():
            if col not in existing_cols:
                conn.execute(text(f'ALTER TABLE wrong_questions ADD COLUMN {col} {col_type}'))


def _migrate_dashboard_tables(db):
    """仪表盘所需表的迁移保障。

    仪表盘本身不引入新表，仅依赖 quiz_attempts / quiz_answers / wrong_questions /
    knowledge_items / quizzes。这些表的迁移由各自函数负责，此处仅作为占位与
    未来扩展的钩子，确保创建顺序正确（在 wrong_questions 之后调用）。
    """
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())
    # 仪表盘依赖的表应由前置迁移函数创建；此处仅做存在性校验，缺失则跳过
    # （db.create_all 已处理新库创建，历史库由各自迁移函数兜底）
    _ = existing_tables


def _migrate_examples(db):
    """确保 examples 表（典型例题）存在。

    db.create_all() 会为新库自动创建表，此函数作为安全保障：
    当数据库已存在但缺少 examples 表时显式建表，避免历史库未触发 create_all。
    """
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    if 'examples' not in existing_tables:
        with db.engine.begin() as conn:
            conn.execute(text(
                'CREATE TABLE examples ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'chapter VARCHAR(100), '
                'knowledge_item_id INTEGER REFERENCES knowledge_items(id), '
                'title VARCHAR(200) NOT NULL, '
                'question TEXT NOT NULL, '
                "question_type VARCHAR(20) DEFAULT 'calc', "
                "difficulty VARCHAR(10) DEFAULT 'medium', "
                'steps_json TEXT, '
                'answer TEXT, '
                'summary TEXT, '
                'graph_data TEXT, '
                'tags VARCHAR(500), '
                'sort_order INTEGER DEFAULT 0, '
                'created_at DATETIME)'
            ))
        return

    # 表已存在：补全可能缺失的字段
    existing_cols = {c['name'] for c in inspector.get_columns('examples')}
    candidate_cols = {
        'chapter': 'VARCHAR(100)',
        'knowledge_item_id': 'INTEGER REFERENCES knowledge_items(id)',
        'title': 'VARCHAR(200)',
        'question': 'TEXT',
        'question_type': "VARCHAR(20) DEFAULT 'calc'",
        'difficulty': "VARCHAR(10) DEFAULT 'medium'",
        'steps_json': 'TEXT',
        'answer': 'TEXT',
        'summary': 'TEXT',
        'graph_data': 'TEXT',
        'tags': 'VARCHAR(500)',
        'sort_order': 'INTEGER DEFAULT 0',
        'created_at': 'DATETIME',
    }
    with db.engine.begin() as conn:
        for col, col_type in candidate_cols.items():
            if col not in existing_cols:
                conn.execute(text(f'ALTER TABLE examples ADD COLUMN {col} {col_type}'))


def _migrate_courseware_mode(db):
    """为 coursewares 表补充 mode 字段，若已存在则跳过。"""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if 'coursewares' not in inspector.get_table_names():
        return
    existing_cols = {c['name'] for c in inspector.get_columns('coursewares')}
    with db.engine.begin() as conn:
        if 'mode' not in existing_cols:
            conn.execute(text("ALTER TABLE coursewares ADD COLUMN mode VARCHAR(10) DEFAULT 'html'"))


def _migrate_achievements(db):
    """确保成就相关表（achievements / user_achievements）存在。"""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    if 'achievements' not in existing_tables:
        with db.engine.begin() as conn:
            conn.execute(text(
                'CREATE TABLE achievements ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name VARCHAR(100) NOT NULL, '
                'description TEXT, '
                'icon VARCHAR(100), '
                "type VARCHAR(50) DEFAULT 'badge', "
                "rarity VARCHAR(20) DEFAULT 'common', "
                'condition_type VARCHAR(50), '
                'condition_value INTEGER DEFAULT 0, '
                'points INTEGER DEFAULT 0, '
                'created_at DATETIME)'
            ))

    if 'user_achievements' not in existing_tables:
        with db.engine.begin() as conn:
            conn.execute(text(
                'CREATE TABLE user_achievements ('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'user_id INTEGER NOT NULL REFERENCES users(id), '
                'achievement_id INTEGER NOT NULL REFERENCES achievements(id), '
                'progress INTEGER DEFAULT 0, '
                'is_unlocked BOOLEAN DEFAULT 0, '
                'unlocked_at DATETIME, '
                'created_at DATETIME)'
            ))


def _init_achievements(db):
    """初始化成就数据。"""
    from app.models import Achievement
    existing = Achievement.query.first()
    if existing:
        return

    achievements = [
        {'name': '初学者', 'description': '完成第一次答题', 'icon': 'fas fa-graduation-cap', 'type': 'badge', 'rarity': 'common', 'condition_type': 'quiz_count', 'condition_value': 1, 'points': 10},
        {'name': '勤奋学习者', 'description': '累计答题达到10道', 'icon': 'fas fa-book-open', 'type': 'badge', 'rarity': 'common', 'condition_type': 'quiz_count', 'condition_value': 10, 'points': 20},
        {'name': '学霸之路', 'description': '累计答题达到50道', 'icon': 'fas fa-award', 'type': 'medal', 'rarity': 'rare', 'condition_type': 'quiz_count', 'condition_value': 50, 'points': 50},
        {'name': '答题大师', 'description': '累计答题达到100道', 'icon': 'fas fa-trophy', 'type': 'trophy', 'rarity': 'epic', 'condition_type': 'quiz_count', 'condition_value': 100, 'points': 100},
        {'name': '精准射手', 'description': '单次答题正确率达到80%', 'icon': 'fas fa-bullseye', 'type': 'badge', 'rarity': 'common', 'condition_type': 'correct_rate', 'condition_value': 80, 'points': 30},
        {'name': '完美表现', 'description': '单次答题正确率达到100%', 'icon': 'fas fa-star', 'type': 'medal', 'rarity': 'rare', 'condition_type': 'correct_rate', 'condition_value': 100, 'points': 50},
        {'name': '知识探索者', 'description': '阅读10个知识条目', 'icon': 'fas fa-search', 'type': 'badge', 'rarity': 'common', 'condition_type': 'knowledge_complete', 'condition_value': 10, 'points': 20},
        {'name': '知识达人', 'description': '阅读50个知识条目', 'icon': 'fas fa-lightbulb', 'type': 'medal', 'rarity': 'rare', 'condition_type': 'knowledge_complete', 'condition_value': 50, 'points': 50},
        {'name': '证明新手', 'description': '完成第一道证明题', 'icon': 'fas fa-pencil-alt', 'type': 'badge', 'rarity': 'common', 'condition_type': 'proof_complete', 'condition_value': 1, 'points': 30},
        {'name': '证明高手', 'description': '完成5道证明题', 'icon': 'fas fa-scroll', 'type': 'medal', 'rarity': 'rare', 'condition_type': 'proof_complete', 'condition_value': 5, 'points': 80},
        {'name': '证明大师', 'description': '完成所有证明题', 'icon': 'fas fa-crown', 'type': 'trophy', 'rarity': 'legendary', 'condition_type': 'proof_complete', 'condition_value': 10, 'points': 200},
        {'name': '图论新手', 'description': '使用图论算法动画功能', 'icon': 'fas fa-network-wired', 'type': 'badge', 'rarity': 'common', 'condition_type': 'graph_algorithm', 'condition_value': 1, 'points': 20},
        {'name': '图论专家', 'description': '使用5种不同的图论算法', 'icon': 'fas fa-project-diagram', 'type': 'medal', 'rarity': 'rare', 'condition_type': 'graph_algorithm', 'condition_value': 5, 'points': 60},
        {'name': 'AI探索者', 'description': '与AI助教进行第一次对话', 'icon': 'fas fa-robot', 'type': 'badge', 'rarity': 'common', 'condition_type': 'chat_count', 'condition_value': 1, 'points': 15},
        {'name': 'AI对话达人', 'description': '与AI助教进行10次对话', 'icon': 'fas fa-comments', 'type': 'medal', 'rarity': 'rare', 'condition_type': 'chat_count', 'condition_value': 10, 'points': 40},
        {'name': '错题克星', 'description': '掌握5道错题', 'icon': 'fas fa-check-circle', 'type': 'badge', 'rarity': 'common', 'condition_type': 'wrong_mastered', 'condition_value': 5, 'points': 30},
        {'name': '全图鉴收集者', 'description': '解锁所有成就', 'icon': 'fas fa-globe', 'type': 'trophy', 'rarity': 'legendary', 'condition_type': 'achievements_unlocked', 'condition_value': 15, 'points': 500},
    ]

    for ach in achievements:
        achievement = Achievement(**ach)
        db.session.add(achievement)
    db.session.commit()
