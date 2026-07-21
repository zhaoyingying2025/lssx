from flask import Blueprint, render_template, request, jsonify
from app.models import KnowledgeItem
from app import db
from collections import deque

innovation_bp = Blueprint('innovation', __name__)

# ========================================
# 离散数学章节结构（基于 Rosen 教材）
# ========================================
DISCRETE_MATH_CHAPTERS = [
    {"id": 1, "label": "命题逻辑", "chapter": 1, "chapter_name": "第1章", "group": "logic",
     "info": "命题逻辑基础，包括命题、逻辑联结词、真值表、等价式与推理规则"},
    {"id": 2, "label": "集合与函数", "chapter": 2, "chapter_name": "第2章", "group": "set",
     "info": "集合、函数、序列与求和，离散数学的基本结构"},
    {"id": 3, "label": "算法", "chapter": 3, "chapter_name": "第3章", "group": "algorithm",
     "info": "算法复杂度、搜索与排序算法"},
    {"id": 4, "label": "数论", "chapter": 4, "chapter_name": "第4章", "group": "number",
     "info": "整除、素数、同余与数论算法"},
    {"id": 5, "label": "归纳与递归", "chapter": 5, "chapter_name": "第5章", "group": "logic",
     "info": "数学归纳法、强归纳与递归定义"},
    {"id": 6, "label": "计数", "chapter": 6, "chapter_name": "第6章", "group": "counting",
     "info": "排列、组合、鸽巢原理与二项式系数"},
    {"id": 7, "label": "离散概率", "chapter": 7, "chapter_name": "第7章", "group": "counting",
     "info": "概率论基础、条件概率与贝叶斯定理"},
    {"id": 8, "label": "高级计数", "chapter": 8, "chapter_name": "第8章", "group": "counting",
     "info": "递推关系、生成函数与容斥原理"},
    {"id": 9, "label": "关系", "chapter": 9, "chapter_name": "第9章", "group": "relation",
     "info": "关系的性质、等价关系、偏序与闭包"},
    {"id": 10, "label": "图论", "chapter": 10, "chapter_name": "第10章", "group": "graph",
     "info": "图的表示、欧拉路径、最短路径与图着色"},
    {"id": 11, "label": "树", "chapter": 11, "chapter_name": "第11章", "group": "graph",
     "info": "树的性质、生成树、哈夫曼编码与树遍历"},
    {"id": 12, "label": "布尔代数", "chapter": 12, "chapter_name": "第12章", "group": "logic",
     "info": "布尔代数、逻辑电路与函数最小化"},
]

# 章节间关联关系（source → target，source 为前置/基础）
INTER_CHAPTER_LINKS = [
    {"source": 1, "target": 5, "label": "依赖"},
    {"source": 10, "target": 11, "label": "包含"},
    {"source": 2, "target": 9, "label": "基础"},
    {"source": 1, "target": 12, "label": "应用"},
    {"source": 2, "target": 6, "label": "基础"},
    {"source": 4, "target": 6, "label": "应用"},
    {"source": 6, "target": 8, "label": "扩展"},
    {"source": 5, "target": 8, "label": "应用"},
    {"source": 2, "target": 3, "label": "基础"},
    {"source": 3, "target": 5, "label": "应用"},
    {"source": 9, "target": 10, "label": "基础"},
    {"source": 2, "target": 10, "label": "应用"},
    {"source": 6, "target": 7, "label": "扩展"},
    {"source": 3, "target": 4, "label": "应用"},
    {"source": 6, "target": 9, "label": "应用"},
    {"source": 1, "target": 3, "label": "基础"},
]


@innovation_bp.route('/')
def index():
    return render_template('innovation.html')


@innovation_bp.route('/graph')
def graph():
    return render_template('innovation_graph.html')


@innovation_bp.route('/path')
def path():
    return render_template('innovation_path.html')


@innovation_bp.route('/example')
def example():
    return render_template('innovation_example.html')


@innovation_bp.route('/api/graph-data')
def api_graph_data():
    """获取知识点关联图谱数据"""
    nodes = []
    links = []

    # 添加章节级节点
    for ch in DISCRETE_MATH_CHAPTERS:
        nodes.append({
            "id": ch["id"],
            "label": ch["label"],
            "chapter": ch["chapter"],
            "chapter_name": ch["chapter_name"],
            "group": ch["group"],
            "type": "chapter",
            "info": ch["info"]
        })

    # 添加章节间关联
    for link in INTER_CHAPTER_LINKS:
        links.append(dict(link))

    # 从数据库获取知识条目，补充小节级节点
    try:
        items = KnowledgeItem.query.all()
        chapter_sections = {}
        for item in items:
            if item.chapter and item.section:
                key = item.chapter
                if key not in chapter_sections:
                    chapter_sections[key] = {}
                if item.section not in chapter_sections[key]:
                    chapter_sections[key][item.section] = []
                chapter_sections[key][item.section].append(item)

        node_id = 100
        for ch in DISCRETE_MATH_CHAPTERS:
            ch_key = ch["chapter_name"]
            if ch_key in chapter_sections:
                sections = chapter_sections[ch_key]
                section_ids = []
                for sec_name, sec_items in sections.items():
                    node_id += 1
                    content_preview = ''
                    if sec_items and sec_items[0].content:
                        content_preview = sec_items[0].content[:120]
                    nodes.append({
                        "id": node_id,
                        "label": sec_name,
                        "chapter": ch["chapter"],
                        "chapter_name": ch["chapter_name"],
                        "group": ch["group"],
                        "type": "section",
                        "info": f"{ch['chapter_name']} {sec_name}：{content_preview}"
                    })
                    links.append({"source": ch["id"], "target": node_id, "label": "包含"})
                    section_ids.append(node_id)

                # 同章节内小节关联
                for i in range(len(section_ids) - 1):
                    links.append({"source": section_ids[i], "target": section_ids[i + 1], "label": "关联"})
    except Exception:
        pass

    return jsonify({"nodes": nodes, "links": links})


@innovation_bp.route('/api/recommend-path', methods=['POST'])
def api_recommend_path():
    """根据已掌握知识点推荐学习路径（拓扑排序 + 分层）"""
    data = request.get_json() or {}
    mastered_ids = set(data.get('mastered', []))

    # 构建邻接表（source → target 表示 source 是前置）
    adj = {ch["id"]: [] for ch in DISCRETE_MATH_CHAPTERS}
    in_degree = {ch["id"]: 0 for ch in DISCRETE_MATH_CHAPTERS}
    out_degree = {ch["id"]: 0 for ch in DISCRETE_MATH_CHAPTERS}

    for link in INTER_CHAPTER_LINKS:
        s, t = link["source"], link["target"]
        adj[s].append((t, link["label"]))
        in_degree[t] += 1
        out_degree[s] += 1

    # Kahn 拓扑排序
    queue = deque()
    for nid in in_degree:
        if in_degree[nid] == 0:
            queue.append(nid)

    topo_order = []
    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for target, _ in adj[node]:
            in_degree[target] -= 1
            if in_degree[target] == 0:
                queue.append(target)

    # 按拓扑顺序计算深度（最长路径分层）
    # 拓扑序保证所有前驱节点先于当前节点处理，确保深度正确
    depth = {nid: 0 for nid in in_degree}
    for nid in topo_order:
        for target, _ in adj[nid]:
            depth[target] = max(depth[target], depth[nid] + 1)

    # 分层
    layers = {}
    for nid in topo_order:
        d = depth[nid]
        if d not in layers:
            layers[d] = []
        layers[d].append(nid)
    layer_list = [{"layer": d, "nodes": nodes} for d, nodes in sorted(layers.items())]

    # 章节信息映射
    ch_map = {ch["id"]: ch for ch in DISCRETE_MATH_CHAPTERS}

    # 构建路径节点
    path_nodes = []
    for nid in topo_order:
        ch = ch_map[nid]
        is_mastered = nid in mastered_ids
        path_nodes.append({
            "id": nid,
            "label": ch["label"],
            "chapter": ch["chapter"],
            "chapter_name": ch["chapter_name"],
            "group": ch["group"],
            "depth": depth[nid],
            "is_mastered": is_mastered,
            "is_core": out_degree[nid] >= 2,
            "is_prerequisite": sum(1 for link in INTER_CHAPTER_LINKS if link["target"] == nid) >= 2,
            "estimated_hours": _estimate_hours(nid),
            "prerequisites": [link["source"] for link in INTER_CHAPTER_LINKS if link["target"] == nid],
            "info": ch["info"]
        })

    return jsonify({
        "path": path_nodes,
        "layers": layer_list,
        "total_nodes": len(path_nodes),
        "mastered_count": len(mastered_ids),
        "remaining_count": len(path_nodes) - len(mastered_ids)
    })


def _estimate_hours(chapter_id):
    """估算章节学习时间（小时）"""
    estimates = {1: 6, 2: 6, 3: 5, 4: 5, 5: 4, 6: 6,
                 7: 4, 8: 5, 9: 6, 10: 7, 11: 5, 12: 4}
    return estimates.get(chapter_id, 5)
