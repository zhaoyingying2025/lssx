import json
from flask import Blueprint, render_template, request, jsonify, flash, g
from app.models import KnowledgeItem, Example, QuizAnswer, WrongQuestion
from app.utils.achievement_service import record_knowledge_read, record_proof_complete
from app import db
from sqlalchemy import or_, func, desc

knowledge_bp = Blueprint('knowledge', __name__)

PER_PAGE = 20


@knowledge_bp.route('/')
def index():
    """知识库首页，展示所有知识条目"""
    chapter = request.args.get('chapter', '')
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    query = KnowledgeItem.query
    if chapter:
        query = query.filter_by(chapter=chapter)
    if category:
        query = query.filter_by(category=category)
    if search:
        keyword = f'%{search}%'
        query = query.filter(or_(KnowledgeItem.title.like(keyword), KnowledgeItem.content.like(keyword)))

    pagination = query.order_by(KnowledgeItem.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    items = pagination.items

    # 获取各章节的条目数量
    chapter_counts = {}
    all_chapters = db.session.query(KnowledgeItem.chapter).distinct().all()
    for (ch,) in all_chapters:
        if ch:
            chapter_counts[ch] = KnowledgeItem.query.filter_by(chapter=ch).count()

    return render_template('knowledge.html', items=items, pagination=pagination,
                           chapter=chapter, category=category, search=search,
                           chapter_counts=chapter_counts)


@knowledge_bp.route('/api/list')
def api_list():
    """返回JSON格式的知识条目列表，支持筛选和分页"""
    chapter = request.args.get('chapter', '')
    section = request.args.get('section', '')
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    query = KnowledgeItem.query
    if chapter:
        query = query.filter_by(chapter=chapter)
    if section:
        query = query.filter_by(section=section)
    if category:
        query = query.filter_by(category=category)
    if search:
        keyword = f'%{search}%'
        query = query.filter(or_(KnowledgeItem.title.like(keyword), KnowledgeItem.content.like(keyword)))

    pagination = query.order_by(KnowledgeItem.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)

    items_data = [{
        'id': item.id,
        'title': item.title,
        'content': item.content,
        'content_summary': (item.content[:200] + '...') if item.content and len(item.content) > 200 else (item.content or ''),
        'chapter': item.chapter,
        'section': item.section,
        'category': item.category,
        'tags': item.tags,
        'source': item.source,
        'is_custom': item.source == 'custom' if item.source else False,
        'created_at': item.created_at.isoformat() if item.created_at else None
    } for item in pagination.items]

    return jsonify({
        'items': items_data,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@knowledge_bp.route('/api/detail/<int:item_id>')
def api_detail(item_id):
    """返回单个知识条目详情JSON"""
    item = KnowledgeItem.query.get_or_404(item_id)

    if g.user:
        try:
            record_knowledge_read(g.user.id, item.id)
        except Exception:
            pass

    return jsonify({
        'id': item.id,
        'title': item.title,
        'content': item.content,
        'chapter': item.chapter,
        'section': item.section,
        'category': item.category,
        'tags': item.tags,
        'source': item.source,
        'is_custom': item.source == 'custom' if item.source else False,
        'created_at': item.created_at.isoformat() if item.created_at else None
    })


@knowledge_bp.route('/api/create', methods=['POST'])
def api_create():
    """创建新的自定义知识条目"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

    item = KnowledgeItem(
        title=title,
        content=content,
        chapter=data.get('chapter', ''),
        section=data.get('section', ''),
        category=data.get('category', 'detail'),
        tags=data.get('tags', ''),
        source='custom'
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '知识条目创建成功',
        'item': {
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'chapter': item.chapter,
            'section': item.section,
            'category': item.category,
            'tags': item.tags,
            'source': item.source,
            'created_at': item.created_at.isoformat() if item.created_at else None
        }
    }), 201


@knowledge_bp.route('/api/update/<int:item_id>', methods=['PUT'])
def api_update(item_id):
    """更新知识条目"""
    item = KnowledgeItem.query.get_or_404(item_id)

    # 只有自定义条目可以编辑
    if item.source != 'custom':
        return jsonify({'success': False, 'message': '内置知识条目不可编辑'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

    item.title = title
    item.content = content
    if 'chapter' in data:
        item.chapter = data['chapter']
    if 'section' in data:
        item.section = data['section']
    if 'category' in data:
        item.category = data['category']
    if 'tags' in data:
        item.tags = data['tags']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': '知识条目更新成功',
        'item': {
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'chapter': item.chapter,
            'section': item.section,
            'category': item.category,
            'tags': item.tags,
            'source': item.source,
            'created_at': item.created_at.isoformat() if item.created_at else None
        }
    })


@knowledge_bp.route('/api/delete/<int:item_id>', methods=['DELETE'])
def api_delete(item_id):
    """删除知识条目"""
    item = KnowledgeItem.query.get_or_404(item_id)

    # 只有自定义条目可以删除
    if item.source != 'custom':
        return jsonify({'success': False, 'message': '内置知识条目不可删除'}), 403

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '知识条目删除成功'
    })


@knowledge_bp.route('/api/chapters')
def api_chapters():
    """获取所有章节及其条目数量"""
    from app.utils.example_data import EXAMPLE_CHAPTER_TITLES

    chapters = db.session.query(
        KnowledgeItem.chapter,
        db.func.count(KnowledgeItem.id)
    ).group_by(KnowledgeItem.chapter).all()

    chapter_data = {}
    for ch, count in chapters:
        if ch:
            chapter_data[ch] = {
                'count': count,
                'title': EXAMPLE_CHAPTER_TITLES.get(ch, '')
            }

    # 获取各章节的小节
    sections = db.session.query(
        KnowledgeItem.chapter,
        KnowledgeItem.section,
        db.func.count(KnowledgeItem.id)
    ).filter(KnowledgeItem.section != '').group_by(
        KnowledgeItem.chapter, KnowledgeItem.section
    ).all()

    section_data = {}
    for ch, sec, count in sections:
        if ch and sec:
            if ch not in section_data:
                section_data[ch] = []
            section_data[ch].append({'name': sec, 'count': count})

    return jsonify({
        'chapters': chapter_data,
        'sections': section_data
    })


@knowledge_bp.route('/import', methods=['POST'])
def import_data():
    """重建知识库：清空现有条目并导入内置中文知识库数据。"""
    from app.utils.knowledge_data import import_knowledge_data
    try:
        count = import_knowledge_data()
        return jsonify({
            'success': True,
            'message': f'知识库重建完成！共导入 {count} 个中文知识条目',
            'count': count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'知识库重建失败: {str(e)}'
        }), 500


@knowledge_bp.route('/api/rebuild', methods=['POST'])
def api_rebuild():
    """重建知识库 API：清空并重新导入内置中文知识库（供前端"重建知识库"按钮调用）。"""
    from app.utils.knowledge_data import import_knowledge_data
    try:
        count = import_knowledge_data()
        return jsonify({
            'success': True,
            'message': f'知识库重建完成！共导入 {count} 个中文知识条目',
            'count': count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'知识库重建失败: {str(e)}'
        }), 500


# ===================== 例题（典型例题动画讲解） =====================

@knowledge_bp.route('/examples')
def examples_list():
    """例题列表页：展示所有例题，支持章节筛选和搜索"""
    chapter = request.args.get('chapter', '')
    search = request.args.get('search', '')

    query = Example.query
    if chapter:
        query = query.filter_by(chapter=chapter)
    if search:
        keyword = f'%{search}%'
        query = query.filter(or_(Example.title.like(keyword),
                                 Example.question.like(keyword),
                                 Example.tags.like(keyword)))

    examples = query.order_by(Example.sort_order.asc()).all()

    # 统计各章例题数量
    chapter_counts = {}
    rows = db.session.query(Example.chapter, db.func.count(Example.id)).group_by(Example.chapter).all()
    for ch, cnt in rows:
        if ch:
            chapter_counts[ch] = cnt

    # 章节标题对照（来自内置数据，避免表为空时无章节信息）
    from app.utils.example_data import EXAMPLE_CHAPTER_TITLES
    chapter_titles = EXAMPLE_CHAPTER_TITLES

    return render_template('knowledge_examples.html',
                           examples=examples,
                           current_chapter=chapter,
                           search=search,
                           chapter_counts=chapter_counts,
                           chapter_titles=chapter_titles)


@knowledge_bp.route('/examples/<int:example_id>')
def example_detail(example_id):
    """例题详情页：分步讲解带动画效果"""
    example = Example.query.get_or_404(example_id)

    # 解析 steps_json
    try:
        steps = json.loads(example.steps_json) if example.steps_json else []
    except (ValueError, TypeError):
        steps = []

    # 解析 graph_data（用于画板联动）
    graph_data = None
    if example.graph_data:
        try:
            graph_data = example.graph_data  # 保持字符串，前端解析
        except Exception:
            graph_data = None

    # 获取相邻例题（用于"上一题/下一题"）
    prev_example = Example.query.filter(Example.id < example_id).order_by(Example.id.desc()).first()
    next_example = Example.query.filter(Example.id > example_id).order_by(Example.id.asc()).first()

    return render_template('knowledge_example_detail.html',
                           example=example,
                           steps=steps,
                           graph_data=graph_data,
                           prev_example=prev_example,
                           next_example=next_example)


@knowledge_bp.route('/api/examples')
def api_examples_list():
    """例题列表 API：返回 JSON 格式的例题列表"""
    chapter = request.args.get('chapter', '')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Example.query
    if chapter:
        query = query.filter_by(chapter=chapter)
    if search:
        keyword = f'%{search}%'
        query = query.filter(or_(Example.title.like(keyword),
                                 Example.question.like(keyword),
                                 Example.tags.like(keyword)))

    pagination = query.order_by(Example.sort_order.asc()).paginate(
        page=page, per_page=min(per_page, 100), error_out=False)

    items_data = [{
        'id': ex.id,
        'title': ex.title,
        'question': ex.question,
        'chapter': ex.chapter,
        'question_type': ex.question_type,
        'difficulty': ex.difficulty,
        'tags': ex.tags,
        'has_graph': bool(ex.graph_data),
        'summary': ex.summary or '',
        'answer': ex.answer or ''
    } for ex in pagination.items]

    return jsonify({
        'items': items_data,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@knowledge_bp.route('/api/examples/<int:example_id>')
def api_examples_detail(example_id):
    """单个例题详情 API"""
    ex = Example.query.get_or_404(example_id)
    try:
        steps = json.loads(ex.steps_json) if ex.steps_json else []
    except (ValueError, TypeError):
        steps = []

    try:
        graph_data = json.loads(ex.graph_data) if ex.graph_data else None
    except (ValueError, TypeError):
        graph_data = None

    return jsonify({
        'id': ex.id,
        'title': ex.title,
        'question': ex.question,
        'chapter': ex.chapter,
        'question_type': ex.question_type,
        'difficulty': ex.difficulty,
        'steps': steps,
        'answer': ex.answer,
        'summary': ex.summary,
        'graph_data': graph_data,
        'tags': ex.tags,
        'sort_order': ex.sort_order,
        'created_at': ex.created_at.isoformat() if ex.created_at else None
    })


@knowledge_bp.route('/api/examples/import', methods=['POST'])
def api_examples_import():
    """导入预置例题数据 API"""
    from app.utils.example_data import import_example_data
    try:
        count = import_example_data()
        return jsonify({
            'success': True,
            'message': f'例题导入完成！共导入 {count} 道典型例题',
            'count': count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'例题导入失败: {str(e)}'
        }), 500


# ===================== 知识库可视化：思维导图 / 概念对比 / 公式速查 =====================

def _chapter_sort_key(ch):
    """从章节字符串中提取数字排序键，例如 "第3章 基础：逻辑与证明" -> 3。"""
    if not ch:
        return 9999
    import re
    m = re.search(r'(\d+)', ch)
    return int(m.group(1)) if m else 9999


def _section_sort_key(sec):
    """从小节字符串中提取形如 '1.2' 的数字排序键。"""
    if not sec:
        return (9999, 0)
    import re
    m = re.match(r'\s*(\d+)\.(\d+)', sec)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m2 = re.search(r'(\d+)', sec)
    return (int(m2.group(1)) if m2 else 9999, 0)


@knowledge_bp.route('/mindmap')
def mindmap():
    """思维导图浏览页面"""
    return render_template('knowledge_mindmap.html')


@knowledge_bp.route('/api/mindmap')
def api_mindmap():
    """获取思维导图树形数据：章 → 节 → 知识点。"""
    items = KnowledgeItem.query.order_by(KnowledgeItem.chapter.asc()).all()

    # 三层结构: chapter -> section -> items
    chapters = {}  # {chapter: {section: [item, ...]}}
    for it in items:
        ch = it.chapter or '未分类'
        sec = it.section or '未分小节'
        chapters.setdefault(ch, {}).setdefault(sec, []).append(it)

    def build_leaf(item):
        return {
            'name': item.title,
            'id': item.id,
            'is_leaf': True
        }

    children = []
    for ch in sorted(chapters.keys(), key=_chapter_sort_key):
        sec_dict = chapters[ch]
        sec_nodes = []
        for sec in sorted(sec_dict.keys(), key=_section_sort_key):
            leaf_nodes = [build_leaf(it) for it in sec_dict[sec]]
            sec_nodes.append({
                'name': sec,
                'children': leaf_nodes
            })
        children.append({
            'name': ch,
            'children': sec_nodes
        })

    return jsonify({
        'name': '离散数学',
        'children': children
    })


@knowledge_bp.route('/api/mindmap_save', methods=['POST'])
def api_mindmap_save():
    """保存思维导图数据"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    try:
        import os
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'mindmap_backup.json')
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': '思维导图保存成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'保存失败: {str(e)}'
        }), 500


@knowledge_bp.route('/comparison')
def comparison():
    """概念对比页面"""
    return render_template('knowledge_comparison.html')


@knowledge_bp.route('/api/comparisons')
def api_comparisons():
    """获取所有对比主题（仅返回索引与标题，避免一次返回全部数据）。"""
    from app.utils.comparison_data import COMPARISONS
    return jsonify({
        'total': len(COMPARISONS),
        'items': [
            {'index': i, 'title': c['title'], 'item_count': len(c.get('items', []))}
            for i, c in enumerate(COMPARISONS)
        ]
    })


@knowledge_bp.route('/api/comparisons/<int:index>')
def api_comparison_detail(index):
    """获取单个对比详情。"""
    from app.utils.comparison_data import COMPARISONS
    if index < 0 or index >= len(COMPARISONS):
        return jsonify({'success': False, 'message': '对比主题不存在'}), 404
    return jsonify({
        'index': index,
        'data': COMPARISONS[index]
    })


@knowledge_bp.route('/formulas')
def formulas():
    """公式速查表页面"""
    return render_template('knowledge_formulas.html')


@knowledge_bp.route('/api/formulas')
def api_formulas():
    """获取公式列表，支持按 chapter 筛选与关键字搜索。"""
    from app.utils.formula_data import FORMULAS
    chapter = request.args.get('chapter', '').strip()
    search = request.args.get('search', '').strip().lower()

    result = FORMULAS
    if chapter:
        result = [f for f in result if f['chapter'] == chapter]
    if search:
        result = [
            f for f in result
            if search in f['name'].lower()
            or search in f['description'].lower()
            or search in f['formula'].lower()
            or search in (f.get('tags') or '').lower()
            or search in f['category'].lower()
        ]

    # 顺便返回章节列表供前端筛选
    chapters = []
    seen = set()
    for f in FORMULAS:
        if f['chapter'] not in seen:
            seen.add(f['chapter'])
            chapters.append(f['chapter'])
    chapters.sort(key=_chapter_sort_key)

    return jsonify({
        'total': len(result),
        'chapters': chapters,
        'items': result
    })


@knowledge_bp.route('/api/recommendations')
def api_recommendations():
    """基于用户学习数据的智能推荐"""
    user_id = g.user.id if g.user else None

    recommendations = []

    if user_id:
        weak_tags = []
        wrong_answers = WrongQuestion.query.filter_by(user_id=user_id, is_mastered=False).all()
        for wa in wrong_answers:
            if wa.tags:
                weak_tags.extend(wa.tags.split(','))

        if weak_tags:
            weak_tag_set = set([t.strip() for t in weak_tags if t.strip()])
            for tag in weak_tag_set:
                related_items = KnowledgeItem.query.filter(
                    KnowledgeItem.tags.like(f'%{tag}%')
                ).limit(3).all()
                for item in related_items:
                    if item.id not in [r['id'] for r in recommendations]:
                        recommendations.append({
                            'id': item.id,
                            'title': item.title,
                            'chapter': item.chapter,
                            'category': item.category,
                            'reason': f'薄弱知识点：{tag}',
                            'type': 'weak_spot'
                        })

        completed_tags = []
        quiz_answers = QuizAnswer.query.filter_by(user_id=user_id, is_correct=True).all()
        for qa in quiz_answers:
            if qa.tags:
                completed_tags.extend(qa.tags.split(','))
        completed_tag_set = set([t.strip() for t in completed_tags if t.strip()])

        for tag in completed_tag_set:
            related_items = KnowledgeItem.query.filter(
                KnowledgeItem.tags.like(f'%{tag}%')
            ).filter(
                KnowledgeItem.category.in_(['theorem', 'algorithm', 'advanced'])
            ).limit(2).all()
            for item in related_items:
                if item.id not in [r['id'] for r in recommendations]:
                    recommendations.append({
                        'id': item.id,
                        'title': item.title,
                        'chapter': item.chapter,
                        'category': item.category,
                        'reason': f'已掌握：{tag}，推荐进阶内容',
                        'type': 'advanced'
                    })

    if not recommendations:
        trending_items = KnowledgeItem.query.filter(
            KnowledgeItem.category.in_(['theorem', 'algorithm'])
        ).limit(5).all()
        for item in trending_items:
            recommendations.append({
                'id': item.id,
                'title': item.title,
                'chapter': item.chapter,
                'category': item.category,
                'reason': '热门知识点',
                'type': 'trending'
            })

    return jsonify({
        'recommendations': recommendations[:10]
    })


@knowledge_bp.route('/api/learning-path')
def api_learning_path():
    """获取个性化学习路径"""
    user_id = g.user.id if g.user else None
    target = request.args.get('target', 'basic')

    paths = []

    if target == 'basic':
        paths = [
            {'step': 1, 'title': '图的基本概念', 'chapter': '第6章 图', 'type': 'concept'},
            {'step': 2, 'title': '图的表示方法', 'chapter': '第6章 图', 'type': 'concept'},
            {'step': 3, 'title': '图的分类', 'chapter': '第6章 图', 'type': 'concept'},
            {'step': 4, 'title': '图的遍历', 'chapter': '第6章 图', 'type': 'algorithm'},
            {'step': 5, 'title': '最短路径', 'chapter': '第6章 图', 'type': 'algorithm'},
            {'step': 6, 'title': '最小生成树', 'chapter': '第6章 图', 'type': 'algorithm'},
        ]
    elif target == 'advanced':
        paths = [
            {'step': 1, 'title': '拓扑排序', 'chapter': '第6章 图', 'type': 'algorithm'},
            {'step': 2, 'title': '欧拉回路', 'chapter': '第6章 图', 'type': 'algorithm'},
            {'step': 3, 'title': '哈密顿回路', 'chapter': '第6章 图', 'type': 'algorithm'},
            {'step': 4, 'title': '图的着色', 'chapter': '第6章 图', 'type': 'advanced'},
            {'step': 5, 'title': '匹配问题', 'chapter': '第6章 图', 'type': 'advanced'},
            {'step': 6, 'title': '网络流', 'chapter': '第6章 图', 'type': 'advanced'},
        ]
    elif target == 'exam':
        paths = [
            {'step': 1, 'title': '最短路径算法综合', 'chapter': '第6章 图', 'type': 'review'},
            {'step': 2, 'title': '最小生成树算法综合', 'chapter': '第6章 图', 'type': 'review'},
            {'step': 3, 'title': '图的连通性', 'chapter': '第6章 图', 'type': 'review'},
            {'step': 4, 'title': '图论证明题技巧', 'chapter': '第6章 图', 'type': 'review'},
            {'step': 5, 'title': '综合应用题', 'chapter': '第6章 图', 'type': 'practice'},
        ]

    if user_id:
        completed_items = []
        quiz_answers = QuizAnswer.query.filter_by(user_id=user_id, is_correct=True).all()
        for qa in quiz_answers:
            if qa.chapter and '图' in qa.chapter:
                completed_items.append(qa.chapter)

        for path in paths:
            path['completed'] = any(path['chapter'] in ci for ci in completed_items)

    return jsonify({
        'learning_path': paths,
        'target': target
    })


# ===================== 证明训练器（Proof Trainer） =====================

@knowledge_bp.route('/proofs')
def proofs_list():
    """证明训练器列表页"""
    return render_template('knowledge_proofs.html')


@knowledge_bp.route('/api/proofs')
def api_proofs_list():
    """获取证明题列表"""
    chapter = request.args.get('chapter', '')
    difficulty = request.args.get('difficulty', '')

    from app.utils.proof_data import get_proofs_by_chapter, get_proofs_by_difficulty

    if chapter:
        proofs = get_proofs_by_chapter(chapter)
    elif difficulty:
        proofs = get_proofs_by_difficulty(difficulty)
    else:
        from app.utils.proof_data import PROOFS
        proofs = PROOFS

    chapters = sorted(set(p['chapter'] for p in proofs))
    difficulties = ['easy', 'medium', 'hard']

    return jsonify({
        'proofs': proofs,
        'chapters': chapters,
        'difficulties': difficulties
    })


@knowledge_bp.route('/api/proofs/<int:proof_id>')
def api_proofs_detail(proof_id):
    """获取单个证明题详情"""
    from app.utils.proof_data import get_proof_by_id
    proof = get_proof_by_id(proof_id)
    if not proof:
        return jsonify({'success': False, 'message': '证明题不存在'}), 404

    return jsonify({
        'success': True,
        'proof': proof
    })


@knowledge_bp.route('/api/proofs/verify', methods=['POST'])
def api_proofs_verify():
    """验证证明步骤答案"""
    data = request.get_json()
    proof_id = data.get('proof_id')
    step_index = data.get('step_index')
    user_answer = data.get('answer', '').strip()

    from app.utils.proof_data import get_proof_by_id
    proof = get_proof_by_id(proof_id)
    if not proof:
        return jsonify({'success': False, 'message': '证明题不存在'}), 404

    if step_index < 0 or step_index >= len(proof['steps']):
        return jsonify({'success': False, 'message': '步骤索引无效'}), 400

    step = proof['steps'][step_index]
    correct_answer = step['answer']

    keywords = [k.strip() for k in correct_answer.split('，') if k.strip()]
    score = 0
    for keyword in keywords:
        if keyword in user_answer:
            score += 25

    is_correct = score >= 75

    if is_correct and step_index >= len(proof['steps']) - 1 and g.user:
        try:
            record_proof_complete(g.user.id, proof_id)
        except Exception:
            pass

    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'score': score,
        'correct_answer': correct_answer,
        'hint': step.get('hint'),
        'next_hint': step.get('next_hint'),
        'has_next': step_index < len(proof['steps']) - 1
    })
