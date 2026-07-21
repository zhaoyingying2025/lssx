# -*- coding: utf-8 -*-
"""
离散数学典型例题库数据模块。

按 Rosen《离散数学及其应用》教材的 13 章组织，全部使用中文描述，
每章约 8 道典型例题，共 104 道题，每题带详细分步解析。

steps 字段格式：
    [{"title": "步骤标题", "content": "步骤内容"}, ...]

graph_data 字段（可选）：JSON 字符串，存储画板联动数据，
    格式与 canvas.html 中 GraphCanvas.toJSON() 输出一致：
    { "type": "graph"/"tree",
      "vertices": [{"id":1,"x":..,"y":..,"label":"A","color":"#2E8B57","radius":22}, ...],
      "edges":    [{"id":1,"source":1,"target":2,"directed":false,"weight":5,"color":"#444"}, ...],
      "annotations": [], "freeDraws": [] }

提供 import_example_data() 函数，用于将内置例题写入数据库。
"""

from datetime import datetime
import json


# 章节标题对照表（chapter -> chapter_title）
EXAMPLE_CHAPTER_TITLES = {
    "第1章": "逻辑与证明",
    "第2章": "集合与函数",
    "第3章": "算法复杂度",
    "第4章": "数论与密码学",
    "第5章": "数学归纳法",
    "第6章": "计数原理",
    "第7章": "离散概率",
    "第8章": "高级计数",
    "第9章": "关系",
    "第10章": "图论",
    "第11章": "树",
    "第12章": "布尔代数",
    "第13章": "图论算法",
}


# 辅助函数：构造简单带权图数据（供画板联动使用）
def _graph(vertices, edges, directed=False):
    """构造画板数据。
    vertices: [(label, x, y), ...]
    edges:    [(src_idx, tgt_idx, weight), ...]  (索引从 1 开始)
    返回 JSON 字符串。
    """
    vs = []
    for i, (label, x, y) in enumerate(vertices, start=1):
        vs.append({
            "id": i, "x": x, "y": y, "label": label,
            "color": "#2E8B57", "radius": 22
        })
    es = []
    for i, (s, t, w) in enumerate(edges, start=1):
        es.append({
            "id": i, "source": s, "target": t,
            "directed": directed, "weight": w, "color": "#444"
        })
    return json.dumps({
        "name": "例题关联图", "type": "graph",
        "vertices": vs, "edges": es,
        "annotations": [], "freeDraws": []
    }, ensure_ascii=False)


# 辅助函数：构造二叉树数据（节点按层排列）
def _tree(values, levels=None):
    """构造完全二叉树画板数据。
    values: [根, 左, 右, ...] 按层序
    """
    n = len(values)
    if levels is None:
        levels = 1
        while (2 ** levels - 1) < n:
            levels += 1
    base_y = 60
    v_spacing = 80
    canvas_w = 800
    base_x = canvas_w / 2
    bottom_count = 2 ** (levels - 1)
    bottom_spacing = min(70, (canvas_w - 80) / max(1, bottom_count - 1)) if bottom_count > 1 else 0

    vs = []
    es = []
    for i in range(n):
        depth = i.bit_length() if i > 0 else 0
        depth = 0 if i == 0 else (i.bit_length() - 1)
        pos_in_level = i - (2 ** depth - 1)
        level_count = 2 ** depth
        level_spacing = bottom_spacing * (2 ** (levels - 1 - depth))
        x = base_x - (level_count - 1) * level_spacing / 2 + pos_in_level * level_spacing
        y = base_y + depth * v_spacing
        vs.append({
            "id": i + 1, "x": x, "y": y, "label": str(values[i]),
            "color": "#2E8B57", "radius": 22
        })
        if i > 0:
            parent_idx = (i - 1) // 2
            es.append({
                "id": i, "source": parent_idx + 1, "target": i + 1,
                "directed": True, "weight": None, "color": "#444"
            })
    return json.dumps({
        "name": "例题关联树", "type": "tree",
        "vertices": vs, "edges": es,
        "annotations": [], "freeDraws": []
    }, ensure_ascii=False)


EXAMPLES = [
    # ===================== 第1章 逻辑与证明（8道） =====================
    {
        "chapter": "第1章", "title": "命题的否定",
        "question": "写出命题\"所有素数都是奇数\"的否定。",
        "question_type": "proof", "difficulty": "easy",
        "steps": [
            {"title": "分析命题类型", "content": "原命题为\"所有素数都是奇数\"，是全称命题，形式为 ∀x P(x)，其中 P(x) 表示\"x 是奇数\"，论域为素数集合。"},
            {"title": "应用否定规则", "content": "全称命题的否定是特称命题：¬(∀x P(x)) ≡ ∃x ¬P(x)，即\"存在一个素数不是奇数\"（也就是存在一个素数是偶数）。"},
            {"title": "写出否定", "content": "存在一个素数，它是偶数。"},
            {"title": "验证", "content": "2 是素数且 2 是偶数，故原命题为假，其否定为真。这验证了否定结果的正确性。"}
        ],
        "answer": "存在一个素数是偶数。",
        "summary": "全称命题 ∀x P(x) 的否定是特称命题 ∃x ¬P(x)；反之亦然。这是量词德摩根律的核心。",
        "tags": "命题逻辑,否定,量词"
    },
    {
        "chapter": "第1章", "title": "真值表判定永真式",
        "question": "用真值表判定命题 (p → q) ∧ (q → r) → (p → r) 是否为永真式。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "分析命题结构", "content": "命题为 ((p → q) ∧ (q → r)) → (p → r)，含三个变元 p、q、r，真值表共 2³ = 8 行。"},
            {"title": "列出所有赋值", "content": "依次枚举 (p,q,r) 的 8 种组合：TTT, TTF, TFT, TFF, FTT, FTF, FFT, FFF。"},
            {"title": "计算子公式", "content": "对每一行计算 p→q、q→r、(p→q)∧(q→r)、p→r 的真值。注意 p→q 仅在 p=T,q=F 时为假。"},
            {"title": "计算最终蕴含", "content": "最后计算 ((p→q)∧(q→r)) → (p→r)。当且仅当前件为真且后件为假时结果为假。"},
            {"title": "得出结论", "content": "所有 8 行中结果均为真，故该命题是永真式。这是假言三段论（hypothetical syllogism）。"}
        ],
        "answer": "该命题是永真式（假言三段论）。",
        "summary": "假言三段论：(p→q)∧(q→r) ⟹ (p→r)。是逻辑推理的基本规则之一。",
        "tags": "真值表,永真式,假言三段论"
    },
    {
        "chapter": "第1章", "title": "德摩根律应用",
        "question": "用等价变换化简 ¬(p ∧ (¬p ∨ q))。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "外层取反", "content": "原式 = ¬(p ∧ (¬p ∨ q))。先应用德摩根律 ¬(A ∧ B) ≡ ¬A ∨ ¬B，得：¬p ∨ ¬(¬p ∨ q)。"},
            {"title": "继续德摩根律", "content": "对 ¬(¬p ∨ q) 再次应用德摩根律：¬(¬p ∨ q) ≡ p ∧ ¬q。"},
            {"title": "代入化简", "content": "代入得：¬p ∨ (p ∧ ¬q)。"},
            {"title": "应用分配律", "content": "利用分配律 A ∨ (B ∧ C) ≡ (A ∨ B) ∧ (A ∨ C)，得：(¬p ∨ p) ∧ (¬p ∨ ¬q)。"},
            {"title": "应用排中律", "content": "¬p ∨ p ≡ T（排中律），故原式 = T ∧ (¬p ∨ ¬q) = ¬p ∨ ¬q。"}
        ],
        "answer": "¬p ∨ ¬q，即等价于 ¬(p ∧ q)。",
        "summary": "德摩根律与分配律、排中律、同一律配合，可化简大多数命题公式。",
        "tags": "德摩根律,等价变换,分配律"
    },
    {
        "chapter": "第1章", "title": "条件命题的否定",
        "question": "求命题\"如果今天是周末，那么我就不去上课\"的否定。",
        "question_type": "proof", "difficulty": "easy",
        "steps": [
            {"title": "符号化", "content": "设 p：今天是周末；q：我去上课。原命题为 p → ¬q。"},
            {"title": "应用否定规则", "content": "关键易错点：¬(p → q) ≡ p ∧ ¬q，而不是 ¬p → ¬q。所以 ¬(p → ¬q) ≡ p ∧ ¬(¬q) ≡ p ∧ q。"},
            {"title": "解释结果", "content": "p ∧ q 表示\"今天是周末且我去上课\"，这正是与原命题\"若周末则不上课\"直接矛盾的情况。"}
        ],
        "answer": "今天是周末，但我去上课了。",
        "summary": "条件命题 p→q 的否定是 p ∧ ¬q，不是 ¬p → ¬q。这是常见易错点。",
        "tags": "条件命题,否定,易错点"
    },
    {
        "chapter": "第1章", "title": "推理规则验证",
        "question": "验证以下推理是否有效：\"如果今天下雨，则路会湿。路没湿。所以今天没下雨。\"",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "符号化前提与结论", "content": "设 p：今天下雨；q：路湿。前提1：p → q；前提2：¬q；结论：¬p。"},
            {"title": "识别推理规则", "content": "这符合取拒式（modus tollens）：若 p → q 为真且 ¬q 为真，则 ¬p 为真。"},
            {"title": "验证逻辑有效性", "content": "利用等价式 p → q ≡ ¬q → ¬p（逆否命题）。由 ¬q 为真，应用假言推理得 ¬p 为真。"},
            {"title": "得出结论", "content": "推理有效，结论\"今天没下雨\"必然成立。"}
        ],
        "answer": "推理有效（取拒式 Modus Tollens）。",
        "summary": "取拒式：p→q, ¬q ⊢ ¬p。是假言推理的对偶形式，常用于反证。",
        "tags": "推理规则,取拒式,逆否命题"
    },
    {
        "chapter": "第1章", "title": "量词否定嵌套",
        "question": "写出命题\"对于每个实数 x，都存在实数 y，使得 x + y = 0\"的否定。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "符号化原命题", "content": "原命题为 ∀x ∃y (x + y = 0)。"},
            {"title": "应用量词德摩根律", "content": "¬(∀x ∃y P(x,y)) ≡ ∃x ¬(∃y P(x,y)) ≡ ∃x ∀y ¬P(x,y)。即\"存在 x，使得对所有 y，x + y ≠ 0\"。"},
            {"title": "翻译为自然语言", "content": "存在一个实数 x，对任意实数 y，都有 x + y ≠ 0。"},
            {"title": "分析真值", "content": "原命题为真（取 y = -x 即可），其否定为假。"}
        ],
        "answer": "存在一个实数 x，使得对任意实数 y 都有 x + y ≠ 0。",
        "summary": "否定嵌套量词时，∀ 与 ∃ 互换，最内层取反。¬(∀x ∃y P) ≡ ∃x ∀y ¬P。",
        "tags": "嵌套量词,否定,量词顺序"
    },
    {
        "chapter": "第1章", "title": "命题符号化",
        "question": "将命题\"只有你努力学习，才能通过考试\"符号化，并写出其逆否命题。",
        "question_type": "proof", "difficulty": "easy",
        "steps": [
            {"title": "识别\"只有...才\"结构", "content": "\"只有 A 才 B\"等价于\"B → A\"。设 p：你努力学习；q：你通过考试。"},
            {"title": "写出符号化", "content": "原命题符号化为 q → p（通过考试蕴含努力学习）。"},
            {"title": "求逆否命题", "content": "逆否命题：¬p → ¬q，即\"如果你不努力学习，那么你就不能通过考试\"。"},
            {"title": "强调等价性", "content": "原命题与其逆否命题逻辑等价，即 q → p ≡ ¬p → ¬q。"}
        ],
        "answer": "符号化为 q → p；逆否命题为 ¬p → ¬q（不努力则不能通过）。",
        "summary": "\"只有 A 才 B\" 翻译为 B → A。逆否命题与原命题等价。",
        "tags": "命题符号化,逆否命题,条件命题"
    },
    {
        "chapter": "第1章", "title": "证明 √2 是无理数",
        "question": "用反证法证明 √2 是无理数。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "假设结论不成立", "content": "假设 √2 是有理数，则存在互素的正整数 p、q，使得 √2 = p/q。"},
            {"title": "两边平方并整理", "content": "两边平方得 2 = p²/q²，即 p² = 2q²。"},
            {"title": "分析 p 的奇偶性", "content": "由 p² = 2q² 知 p² 是偶数，故 p 是偶数。设 p = 2k。"},
            {"title": "代入并分析 q", "content": "代入得 (2k)² = 2q²，即 2k² = q²，所以 q² 是偶数，故 q 也是偶数。"},
            {"title": "得出矛盾", "content": "p、q 都是偶数，有公因数 2，与\"互素\"矛盾。故假设不成立。"},
            {"title": "结论", "content": "因此 √2 是无理数。"}
        ],
        "answer": "√2 是无理数。",
        "summary": "反证法三步：假设结论不成立 → 推出矛盾 → 肯定原结论。适用于直接证明困难的命题。",
        "tags": "反证法,无理数,证明"
    },

    # ===================== 第2章 集合与函数（8道） =====================
    {
        "chapter": "第2章", "title": "集合运算化简",
        "question": "化简 (A ∪ B) ∩ (A ∪ Bᶜ)。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "识别分配律", "content": "原式形如 (A ∪ X) ∩ (A ∪ Y)，可应用分配律：(A ∪ X) ∩ (A ∪ Y) = A ∪ (X ∩ Y)。"},
            {"title": "应用分配律", "content": "(A ∪ B) ∩ (A ∪ Bᶜ) = A ∪ (B ∩ Bᶜ)。"},
            {"title": "化简内部", "content": "B ∩ Bᶜ = ∅（任何集合与其补集的交为空集）。"},
            {"title": "最终化简", "content": "原式 = A ∪ ∅ = A。"}
        ],
        "answer": "A",
        "summary": "集合分配律 (A∪X)∩(A∪Y) = A∪(X∩Y)；任何集合与空集的并为自身。",
        "tags": "集合运算,分配律,化简"
    },
    {
        "chapter": "第2章", "title": "笛卡尔积基数",
        "question": "设 |A| = 3，|B| = 4，求 |A × B × A|。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "回顾笛卡尔积定义", "content": "A × B = {(a,b) : a ∈ A, b ∈ B}。其基数 |A × B| = |A| · |B|。"},
            {"title": "推广到三元笛卡尔积", "content": "|A × B × A| = |A| · |B| · |A|。"},
            {"title": "代入计算", "content": "= 3 · 4 · 3 = 36。"}
        ],
        "answer": "36",
        "summary": "笛卡尔积的基数等于各分量基数之积：|A₁ × A₂ × ... × Aₙ| = ∏|Aᵢ|。",
        "tags": "笛卡尔积,基数,计数"
    },
    {
        "chapter": "第2章", "title": "函数性质判定",
        "question": "设 f: Z → Z，f(x) = x² + 1。判断 f 是否为单射、满射、双射。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "判断单射性", "content": "单射要求 x₁ ≠ x₂ ⟹ f(x₁) ≠ f(x₂)。但 f(1) = 2，f(-1) = 2，即 1 ≠ -1 但 f(1) = f(-1)，故 f 不是单射。"},
            {"title": "判断满射性", "content": "满射要求 ∀y ∈ Z, ∃x ∈ Z 使 f(x) = y。但 f(x) = x² + 1 ≥ 1，故 y = 0 在 Z 中无原像。"},
            {"title": "得出双射性", "content": "f 既不是单射也不是满射，因此不是双射。"}
        ],
        "answer": "f 既不是单射，也不是满射，更不是双射。",
        "summary": "判定函数性质：单射看\"不同输入是否产生不同输出\"；满射看\"陪域每个元素是否有原像\"；双射 = 单射 + 满射。",
        "tags": "函数,单射,满射,双射"
    },
    {
        "chapter": "第2章", "title": "集合恒等式证明",
        "question": "证明 (A − B) ∪ (A ∩ B) = A。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "改写差集", "content": "A − B = A ∩ Bᶜ。原式变为 (A ∩ Bᶜ) ∪ (A ∩ B)。"},
            {"title": "应用分配律", "content": "(A ∩ Bᶜ) ∪ (A ∩ B) = A ∩ (Bᶜ ∪ B)。"},
            {"title": "应用补集律", "content": "Bᶜ ∪ B = U（全集），故 A ∩ U = A。"},
            {"title": "结论", "content": "因此 (A − B) ∪ (A ∩ B) = A。"}
        ],
        "answer": "等式成立，(A − B) ∪ (A ∩ B) = A。",
        "summary": "差集 A−B = A∩Bᶜ，再利用分配律和补集律可化简许多集合恒等式。",
        "tags": "集合恒等式,差集,分配律"
    },
    {
        "chapter": "第2章", "title": "幂集计算",
        "question": "设 A = {1, 2, 3}，求 A 的幂集 P(A) 并指出 |P(A)|。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "回顾幂集定义", "content": "幂集 P(A) 是 A 所有子集构成的集合。若 |A| = n，则 |P(A)| = 2ⁿ。"},
            {"title": "计算基数", "content": "|A| = 3，故 |P(A)| = 2³ = 8。"},
            {"title": "枚举所有子集", "content": "P(A) = {∅, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3}}。"}
        ],
        "answer": "|P(A)| = 8。P(A) = {∅, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3}}。",
        "summary": "n 元集合的幂集有 2ⁿ 个元素，对应 n 位二进制串的所有可能。",
        "tags": "幂集,子集,基数"
    },
    {
        "chapter": "第2章", "title": "复合函数求值",
        "question": "设 f(x) = 2x + 1，g(x) = x²。求 (f ∘ g)(3) 和 (g ∘ f)(3)。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "理解复合函数", "content": "(f ∘ g)(x) = f(g(x))，即先内层 g 后外层 f。"},
            {"title": "计算 (f ∘ g)(3)", "content": "g(3) = 3² = 9，f(9) = 2·9 + 1 = 19。所以 (f ∘ g)(3) = 19。"},
            {"title": "计算 (g ∘ f)(3)", "content": "f(3) = 2·3 + 1 = 7，g(7) = 7² = 49。所以 (g ∘ f)(3) = 49。"},
            {"title": "比较结果", "content": "(f ∘ g)(3) ≠ (g ∘ f)(3)，说明复合函数一般不可交换。"}
        ],
        "answer": "(f ∘ g)(3) = 19；(g ∘ f)(3) = 49。",
        "summary": "复合函数 f∘g 表示先 g 后 f。一般 f∘g ≠ g∘f，复合运算不满足交换律。",
        "tags": "复合函数,求值,不可交换"
    },
    {
        "chapter": "第2章", "title": "可数集判定",
        "question": "证明正整数集合 N⁺ 的平方构成的集合 S = {n² : n ∈ N⁺} 是可数集。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "回顾可数集定义", "content": "集合 S 可数当且仅当存在从 N⁺ 到 S 的双射（或 S 有限或与 N⁺ 等势）。"},
            {"title": "构造双射", "content": "定义 f: N⁺ → S，f(n) = n²。"},
            {"title": "验证单射", "content": "若 n₁² = n₂² 且 n₁, n₂ > 0，则 n₁ = n₂，故 f 是单射。"},
            {"title": "验证满射", "content": "对任意 s ∈ S，由 S 定义，存在 n ∈ N⁺ 使 s = n²，即 s = f(n)。故 f 是满射。"},
            {"title": "得出结论", "content": "f 是 N⁺ 到 S 的双射，故 S 可数。"}
        ],
        "answer": "S 是可数集（与 N⁺ 等势）。",
        "summary": "证明可数集的关键是构造与正整数集的双射。可数集的子集仍可数。",
        "tags": "可数集,双射,基数"
    },
    {
        "chapter": "第2章", "title": "鸽巢原理（集合应用）",
        "question": "从 1 到 100 的整数中任取 51 个数，证明必有两个数其中一个是另一个的倍数。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "构造鸽巢", "content": "将每个正整数 n 写成 n = 2ᵏ · m 的形式，其中 m 为奇数（即剥离所有因子 2）。m 称为\"奇部分\"。"},
            {"title": "确定鸽巢数", "content": "1 到 100 中奇数共 50 个，所以奇部分 m 的可能取值有 50 种。"},
            {"title": "应用鸽巢原理", "content": "任取 51 个数，它们的奇部分 m 只有 50 种取值，故必有两个数 a、b 奇部分相同。"},
            {"title": "分析两数关系", "content": "设 a = 2ⁱ · m，b = 2ʲ · m。若 i < j，则 b = 2^(j−i) · a，即 b 是 a 的倍数；反之 a 是 b 的倍数。"},
            {"title": "结论", "content": "故必有两数其中一个是另一个的倍数。"}
        ],
        "answer": "命题成立。",
        "summary": "鸽巢原理：n+1 个物体放入 n 个鸽巢，必有鸽巢含至少 2 个物体。关键在于巧妙构造鸽巢。",
        "tags": "鸽巢原理,倍数,证明"
    },

    # ===================== 第3章 算法复杂度（8道） =====================
    {
        "chapter": "第3章", "title": "时间复杂度分析",
        "question": "分析以下算法的时间复杂度：\nfor i = 1 to n:\n    for j = 1 to i:\n        print(i, j)",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "分析外层循环", "content": "外层循环 i 从 1 到 n，共执行 n 次。"},
            {"title": "分析内层循环", "content": "对每个固定的 i，内层循环 j 从 1 到 i，执行 i 次。"},
            {"title": "计算总执行次数", "content": "总次数 = 1 + 2 + 3 + ... + n = n(n+1)/2。"},
            {"title": "用大 O 表示", "content": "n(n+1)/2 = (n²+n)/2，最高阶项为 n²/2。在大 O 表示法中忽略常数和低阶项，得 O(n²)。"}
        ],
        "answer": "O(n²)",
        "summary": "嵌套循环的总执行次数通常是各层循环次数的乘积或求和；求和 1+2+...+n = n(n+1)/2 = Θ(n²)。",
        "tags": "时间复杂度,大O,嵌套循环"
    },
    {
        "chapter": "第3章", "title": "对数复杂度识别",
        "question": "分析算法：\ni = 1\nwhile i < n:\n    i = i * 2\n求其时间复杂度。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "观察变量变化", "content": "i 每次翻倍：1, 2, 4, 8, ..., 直到 i ≥ n。"},
            {"title": "计算迭代次数", "content": "设经过 k 次迭代后 i ≥ n，即 2ᵏ ≥ n，故 k ≥ log₂ n。最少需要 ⌈log₂ n⌉ 次。"},
            {"title": "得出复杂度", "content": "迭代次数为 Θ(log n)，即时间复杂度为 O(log n)。"}
        ],
        "answer": "O(log n)",
        "summary": "变量每次乘以常数倍（如 ×2）的循环，复杂度通常为对数级 O(log n)。",
        "tags": "时间复杂度,对数,迭代"
    },
    {
        "chapter": "第3章", "title": "大O运算性质",
        "question": "若 f(n) = O(n²) 且 g(n) = O(n³)，证明 f(n) + g(n) = O(n³)。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "回顾大 O 定义", "content": "f(n) = O(g(n)) 表示存在正常数 C、n₀，使 ∀n ≥ n₀，有 |f(n)| ≤ C·g(n)。"},
            {"title": "应用已知条件", "content": "f(n) = O(n²)：存在 C₁, n₁ 使 f(n) ≤ C₁n² (n ≥ n₁)。g(n) = O(n³)：存在 C₂, n₂ 使 g(n) ≤ C₂n³ (n ≥ n₂)。"},
            {"title": "求和", "content": "f(n) + g(n) ≤ C₁n² + C₂n³。对于 n ≥ 1，n² ≤ n³，故 C₁n² ≤ C₁n³。"},
            {"title": "放缩", "content": "f(n) + g(n) ≤ C₁n³ + C₂n³ = (C₁ + C₂)n³。取 C = C₁ + C₂，n₀ = max(n₁, n₂, 1)。"},
            {"title": "结论", "content": "故 f(n) + g(n) = O(n³)。"}
        ],
        "answer": "f(n) + g(n) = O(n³)。",
        "summary": "大 O 求和规则：O(f) + O(g) = O(max(f, g))。取高阶项。",
        "tags": "大O,求和,渐进分析"
    },
    {
        "chapter": "第3章", "title": "二分查找复杂度",
        "question": "分析二分查找算法在最坏情况下的时间复杂度。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾算法", "content": "二分查找在有序数组中查找元素，每次比较中间元素，根据大小关系将查找区间减半。"},
            {"title": "建立递推关系", "content": "设 T(n) 为规模 n 的查找次数。每次比较后问题规模减半，故 T(n) = T(n/2) + 1。"},
            {"title": "求解递推", "content": "展开递推：T(n) = T(n/2) + 1 = T(n/4) + 2 = ... = T(n/2ᵏ) + k。当 n/2ᵏ = 1 时停止，即 k = log₂ n。"},
            {"title": "得出复杂度", "content": "T(n) = log₂ n + T(1) = Θ(log n)。"}
        ],
        "answer": "O(log n)",
        "summary": "二分查找每次将问题规模减半，时间复杂度为 O(log n)，远优于线性查找的 O(n)。",
        "tags": "二分查找,递推,对数复杂度"
    },
    {
        "chapter": "第3章", "title": "冒泡排序分析",
        "question": "分析冒泡排序在最坏情况下的时间复杂度。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾算法", "content": "冒泡排序：n 个元素，进行 n-1 轮比较，每轮将最大元素\"冒泡\"到末尾。"},
            {"title": "分析最坏情况", "content": "最坏情况为数组完全逆序。第 i 轮需进行 (n-i) 次比较和交换。"},
            {"title": "计算总次数", "content": "总比较次数 = (n-1) + (n-2) + ... + 1 = n(n-1)/2。"},
            {"title": "得出复杂度", "content": "n(n-1)/2 = (n²-n)/2，忽略常数和低阶项，最坏复杂度为 O(n²)。"}
        ],
        "answer": "最坏时间复杂度 O(n²)。",
        "summary": "冒泡排序最坏、平均复杂度均为 O(n²)，最好情况（已有序）为 O(n)。",
        "tags": "冒泡排序,最坏复杂度,平方级"
    },
    {
        "chapter": "第3章", "title": "归并排序分析",
        "question": "分析归并排序的时间复杂度。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "回顾算法", "content": "归并排序：将数组对半分成两半，分别排序后合并。"},
            {"title": "建立递推", "content": "T(n) = 2T(n/2) + O(n)。其中 2T(n/2) 是两个子问题，O(n) 是合并代价。"},
            {"title": "应用主定理", "content": "主定理：T(n) = aT(n/b) + f(n)，a=2, b=2, f(n)=n。n^(log_b a) = n^(log_2 2) = n。f(n) = Θ(n^(log_b a))，故 T(n) = Θ(n log n)。"},
            {"title": "结论", "content": "归并排序时间复杂度为 O(n log n)，最坏、平均、最好情况均相同。"}
        ],
        "answer": "O(n log n)。",
        "summary": "归并排序基于分治，递推 T(n) = 2T(n/2) + O(n)，由主定理得 O(n log n)。",
        "tags": "归并排序,主定理,分治"
    },
    {
        "chapter": "第3章", "title": "最大公约数算法",
        "question": "分析欧几里得算法（辗转相除法）求 gcd(a, b) 的时间复杂度，其中 a > b > 0。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "回顾算法", "content": "欧几里得算法：gcd(a,b) = gcd(b, a mod b)，递归进行直到 b = 0。"},
            {"title": "分析递归次数", "content": "关键事实：每两次递归后，第一个参数至少减半。即 a_{k+2} ≤ a_k / 2。"},
            {"title": "估计上界", "content": "若 a < 2ᵏ，则递归至多 2k 次。故递归次数 ≤ 2 log₂ a。"},
            {"title": "结论", "content": "欧几里得算法的时间复杂度为 O(log min(a, b))，远优于线性。"}
        ],
        "answer": "O(log min(a, b))",
        "summary": "欧几里得算法每两步参数减半，时间复杂度 O(log min(a, b))，是数论算法的基石。",
        "tags": "欧几里得算法,对数复杂度,数论"
    },
    {
        "chapter": "第3章", "title": "递归算法复杂度",
        "question": "求下列递推式的解：T(n) = 2T(n-1) + 1，T(1) = 1。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "展开递推", "content": "T(n) = 2T(n-1) + 1 = 2[2T(n-2) + 1] + 1 = 4T(n-2) + 2 + 1。"},
            {"title": "继续展开", "content": "= 4[2T(n-3) + 1] + 3 = 8T(n-3) + 4 + 2 + 1。"},
            {"title": "归纳通项", "content": "归纳得 T(n) = 2ᵏ T(n-k) + (2ᵏ - 1)。当 n-k = 1 时停止，k = n-1。"},
            {"title": "代入求值", "content": "T(n) = 2^(n-1) · T(1) + (2^(n-1) - 1) = 2^(n-1) + 2^(n-1) - 1 = 2ⁿ - 1。"},
            {"title": "得出复杂度", "content": "T(n) = 2ⁿ - 1 = Θ(2ⁿ)，这是指数级复杂度。"}
        ],
        "answer": "T(n) = 2ⁿ - 1 = Θ(2ⁿ)。",
        "summary": "递推 T(n) = aT(n-1) + f(n) 形式解为 Θ(aⁿ)（a > 1 时），递归减 1 易产生指数复杂度。",
        "tags": "递推,递归,指数复杂度"
    },

    # ===================== 第4章 数论与密码学（8道） =====================
    {
        "chapter": "第4章", "title": "模运算基本性质",
        "question": "求 3²⁰²³ mod 7。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "利用费马小定理", "content": "7 是素数，3 与 7 互素，由费马小定理：3⁶ ≡ 1 (mod 7)。"},
            {"title": "分解指数", "content": "2023 = 6 · 337 + 1，故 3²⁰²³ = 3^(6·337+1) = (3⁶)^337 · 3¹。"},
            {"title": "应用费马小定理", "content": "(3⁶)^337 ≡ 1^337 ≡ 1 (mod 7)，故 3²⁰²³ ≡ 1 · 3 ≡ 3 (mod 7)。"}
        ],
        "answer": "3²⁰²³ mod 7 = 3。",
        "summary": "费马小定理：若 p 素且 gcd(a,p)=1，则 a^(p-1) ≡ 1 (mod p)。用于降次幂。",
        "tags": "模运算,费马小定理,降幂"
    },
    {
        "chapter": "第4章", "title": "扩展欧几里得算法",
        "question": "求 5⁻¹ mod 17，即 5 在模 17 下的乘法逆元。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "判断可逆性", "content": "gcd(5, 17) = 1，故 5 在模 17 下存在乘法逆元。"},
            {"title": "用扩展欧几里得算法", "content": "求整数 x, y 使 5x + 17y = 1。"},
            {"title": "辗转相除", "content": "17 = 3·5 + 2；5 = 2·2 + 1；2 = 2·1 + 0。回代：1 = 5 - 2·2 = 5 - 2(17 - 3·5) = 7·5 - 2·17。"},
            {"title": "求逆元", "content": "故 x = 7。验证：5·7 = 35 = 2·17 + 1 ≡ 1 (mod 17)。所以 5⁻¹ ≡ 7 (mod 17)。"}
        ],
        "answer": "5⁻¹ ≡ 7 (mod 17)。",
        "summary": "扩展欧几里得算法：求 ax + by = gcd(a,b) 的解；当 gcd=1 时，x 即为 a 模 b 的逆元。",
        "tags": "扩展欧几里得,逆元,模运算"
    },
    {
        "chapter": "第4章", "title": "中国剩余定理",
        "question": "求满足以下同余方程组的最小正整数 x：\nx ≡ 2 (mod 3)\nx ≡ 3 (mod 5)\nx ≡ 2 (mod 7)",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "回顾中国剩余定理", "content": "若模数两两互素，方程组存在唯一解（模数乘积意义下）。3、5、7 两两互素，N = 3·5·7 = 105。"},
            {"title": "计算部分积", "content": "N₁ = N/3 = 35，N₂ = N/5 = 21，N₃ = N/7 = 15。"},
            {"title": "求各逆元", "content": "求 N₁⁻¹ mod 3：35 mod 3 = 2，2⁻¹ mod 3 = 2（因 2·2=4≡1）。\n求 N₂⁻¹ mod 5：21 mod 5 = 1，1⁻¹ = 1。\n求 N₃⁻¹ mod 7：15 mod 7 = 1，1⁻¹ = 1。"},
            {"title": "代入公式", "content": "x = (a₁·N₁·M₁ + a₂·N₂·M₂ + a₃·N₃·M₃) mod N\n= (2·35·2 + 3·21·1 + 2·15·1) mod 105\n= (140 + 63 + 30) mod 105\n= 233 mod 105\n= 23。"},
            {"title": "验证", "content": "23 mod 3 = 2 ✓；23 mod 5 = 3 ✓；23 mod 7 = 2 ✓。"}
        ],
        "answer": "x = 23",
        "summary": "中国剩余定理（孙子定理）：模数两两互素时，同余方程组在模数乘积下有唯一解。",
        "tags": "中国剩余定理,同余方程,逆元"
    },
    {
        "chapter": "第4章", "title": "RSA 加密计算",
        "question": "在 RSA 中，取 p = 3，q = 11，e = 7，明文 m = 2。求公钥、私钥和密文 c。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "计算模数", "content": "n = p · q = 3 · 11 = 33。公钥包含 (n, e) = (33, 7)。"},
            {"title": "计算欧拉函数", "content": "φ(n) = (p-1)(q-1) = 2 · 10 = 20。"},
            {"title": "求私钥 d", "content": "d 满足 e·d ≡ 1 (mod φ(n))，即 7d ≡ 1 (mod 20)。\n试值：7·3 = 21 ≡ 1 (mod 20)，故 d = 3。"},
            {"title": "加密", "content": "密文 c = m^e mod n = 2⁷ mod 33 = 128 mod 33 = 128 - 3·33 = 128 - 99 = 29。"},
            {"title": "验证解密", "content": "解密：m' = c^d mod n = 29³ mod 33 = 24389 mod 33。24389 / 33 = 739 余 2，故 m' = 2 = m ✓。"}
        ],
        "answer": "公钥 (n=33, e=7)，私钥 d=3，密文 c=29。",
        "summary": "RSA 流程：选 p,q → 算 n, φ(n) → 选 e → 求 d=e⁻¹ mod φ(n) → 加密 c=m^e mod n → 解密 m=c^d mod n。",
        "tags": "RSA,加密,公钥密码"
    },
    {
        "chapter": "第4章", "title": "线性同余方程",
        "question": "求解 9x ≡ 12 (mod 15)。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "判断可解性", "content": "d = gcd(9, 15) = 3。判断 3 | 12：是，故方程有解，且模 15 下有 d=3 个解。"},
            {"title": "化简方程", "content": "原方程两边同除以 d=3：3x ≡ 4 (mod 5)。"},
            {"title": "求逆元", "content": "求 3⁻¹ mod 5：3·2 = 6 ≡ 1 (mod 5)，故 3⁻¹ ≡ 2 (mod 5)。"},
            {"title": "求解", "content": "x ≡ 4 · 2 ≡ 8 ≡ 3 (mod 5)。即 x = 3 + 5k，k ∈ Z。"},
            {"title": "写出模 15 下所有解", "content": "k = 0, 1, 2 时 x = 3, 8, 13。故模 15 下的解为 x ≡ 3, 8, 13 (mod 15)。"}
        ],
        "answer": "x ≡ 3, 8, 13 (mod 15)。",
        "summary": "线性同余 ax ≡ b (mod m) 有解当且仅当 gcd(a,m) | b；解的个数为 gcd(a,m)。",
        "tags": "线性同余,方程求解,逆元"
    },
    {
        "chapter": "第4章", "title": "欧拉函数计算",
        "question": "求 φ(360)。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "分解质因数", "content": "360 = 2³ × 3² × 5¹。"},
            {"title": "应用欧拉函数公式", "content": "若 n = p₁^a₁ × p₂^a₂ × ... × pₖ^aₖ，则 φ(n) = n × ∏(1 - 1/pᵢ)。"},
            {"title": "代入计算", "content": "φ(360) = 360 × (1 - 1/2) × (1 - 1/3) × (1 - 1/5)\n= 360 × (1/2) × (2/3) × (4/5)\n= 360 × (1·2·4)/(2·3·5)\n= 360 × 8/30\n= 360 × 4/15\n= 96。"},
            {"title": "验证", "content": "也可分别计算：φ(2³) = 2²(2-1) = 4，φ(3²) = 3(3-1) = 6，φ(5) = 4。φ(360) = 4·6·4 = 96 ✓。"}
        ],
        "answer": "φ(360) = 96。",
        "summary": "欧拉函数 φ(n) = n∏(1 - 1/pᵢ)，对 n 的质因数分解；φ 是积性函数：gcd(a,b)=1 时 φ(ab)=φ(a)φ(b)。",
        "tags": "欧拉函数,质因数分解,积性函数"
    },
    {
        "chapter": "第4章", "title": "素数判定与因数",
        "question": "用试除法判定 91 是否为素数。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "确定试除范围", "content": "若 n 是合数，则必有不超过 √n 的素因数。√91 ≈ 9.54，只需试除 2, 3, 5, 7。"},
            {"title": "逐一试除", "content": "91 ÷ 2 余 1（奇数，不被 2 整除）；91 ÷ 3：9+1=10，10 不被 3 整除；91 ÷ 5：末位 1，不被 5 整除；91 ÷ 7 = 13 整除！"},
            {"title": "得出结论", "content": "91 = 7 × 13，故 91 是合数，不是素数。"}
        ],
        "answer": "91 不是素数，91 = 7 × 13。",
        "summary": "试除法：只需检查不超过 √n 的素数；n 能被其中任一整除即为合数。",
        "tags": "素数判定,试除法,因数分解"
    },
    {
        "chapter": "第4章", "title": "凯撒密码解密",
        "question": "已知凯撒密码密文 \"KHOOR\"，密钥 k = 3，求明文。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "回顾凯撒密码", "content": "凯撒密码：加密 c = (m + k) mod 26，解密 m = (c - k) mod 26。"},
            {"title": "逐字符解密", "content": "K(10) - 3 = 7 → H\nH(7) - 3 = 4 → E\nO(14) - 3 = 11 → L\nO(14) - 3 = 11 → L\nR(17) - 3 = 14 → O"},
            {"title": "拼出明文", "content": "明文为 \"HELLO\"。"}
        ],
        "answer": "明文为 HELLO。",
        "summary": "凯撒密码是最简单的替换密码，密钥空间仅 25，安全性极低，但概念基础。",
        "tags": "凯撒密码,古典密码,替换密码"
    },

    # ===================== 第5章 数学归纳法（8道） =====================
    {
        "chapter": "第5章", "title": "求和公式归纳证明",
        "question": "用数学归纳法证明：1 + 2 + 3 + ... + n = n(n+1)/2 对所有正整数 n 成立。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "归纳基础", "content": "n = 1 时，左式 = 1，右式 = 1·2/2 = 1，相等。基础成立。"},
            {"title": "归纳假设", "content": "假设对某个正整数 k，命题成立：1 + 2 + ... + k = k(k+1)/2。"},
            {"title": "归纳步骤", "content": "需证 n = k+1 时命题成立：1 + 2 + ... + k + (k+1) = (k+1)(k+2)/2。"},
            {"title": "应用假设", "content": "左式 = [k(k+1)/2] + (k+1)（应用归纳假设）= (k+1)(k/2 + 1) = (k+1)(k+2)/2。"},
            {"title": "结论", "content": "由归纳原理，对所有正整数 n，1+2+...+n = n(n+1)/2 成立。"}
        ],
        "answer": "公式 1+2+...+n = n(n+1)/2 成立。",
        "summary": "数学归纳法三步：基础（n=1）、假设（n=k）、推导（n=k+1）。",
        "tags": "数学归纳法,求和,证明"
    },
    {
        "chapter": "第5章", "title": "不等式归纳证明",
        "question": "用归纳法证明：2ⁿ > n，对所有正整数 n 成立。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "归纳基础", "content": "n = 1 时，2¹ = 2 > 1。成立。"},
            {"title": "归纳假设", "content": "假设对某个正整数 k，2ᵏ > k 成立。"},
            {"title": "归纳步骤", "content": "需证 2^(k+1) > k+1。"},
            {"title": "推导", "content": "2^(k+1) = 2 · 2ᵏ > 2k（归纳假设）≥ k + 1（当 k ≥ 1 时 2k ≥ k+1）。"},
            {"title": "结论", "content": "由归纳原理，对所有正整数 n，2ⁿ > n 成立。"}
        ],
        "answer": "命题成立。",
        "summary": "不等式归纳中常利用 2·(假设不等式) 与目标不等式的关系进行放缩。",
        "tags": "归纳法,不等式,指数"
    },
    {
        "chapter": "第5章", "title": "整除性归纳证明",
        "question": "用归纳法证明：对所有正整数 n，3 整除 n³ - n。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "归纳基础", "content": "n = 1 时，1³ - 1 = 0，3 | 0。成立。"},
            {"title": "归纳假设", "content": "假设对某个正整数 k，3 | (k³ - k)，即 k³ - k ≡ 0 (mod 3)。"},
            {"title": "归纳步骤", "content": "需证 3 | ((k+1)³ - (k+1))。"},
            {"title": "展开计算", "content": "(k+1)³ - (k+1) = k³ + 3k² + 3k + 1 - k - 1 = (k³ - k) + 3k² + 3k = (k³ - k) + 3(k² + k)。"},
            {"title": "应用假设", "content": "由归纳假设 3 | (k³ - k)，且显然 3 | 3(k² + k)，故 3 | ((k+1)³ - (k+1))。"},
            {"title": "结论", "content": "由归纳原理，对所有正整数 n，3 | (n³ - n)。"}
        ],
        "answer": "命题成立。",
        "summary": "整除性归纳关键：将目标式表示为\"归纳假设 + 3 的倍数\"的形式。",
        "tags": "归纳法,整除,同余"
    },
    {
        "chapter": "第5章", "title": "强归纳法应用",
        "question": "用强归纳法证明：每个正整数 n ≥ 2 都能表示为素数的乘积。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "回顾强归纳法", "content": "强归纳法：假设对所有 k < n 命题成立，证明对 n 也成立。"},
            {"title": "归纳基础", "content": "n = 2：2 本身是素数，可视为\"一个素数的乘积\"，成立。"},
            {"title": "归纳假设", "content": "假设对所有满足 2 ≤ m < n 的正整数 m，m 都能表示为素数乘积。"},
            {"title": "归纳步骤", "content": "考虑 n：\n- 若 n 是素数，则 n 本身即素数乘积，成立。\n- 若 n 是合数，则 n = a · b，其中 2 ≤ a, b < n。"},
            {"title": "应用假设", "content": "由归纳假设，a 和 b 都能表示为素数乘积：a = p₁p₂...pₛ，b = q₁q₂...qₜ。故 n = a·b = p₁...pₛ·q₁...qₜ，也是素数乘积。"},
            {"title": "结论", "content": "由强归纳法，所有 n ≥ 2 都能表示为素数乘积。"}
        ],
        "answer": "命题成立（算术基本定理）。",
        "summary": "强归纳法假设对全部更小情形成立，适用于递推关系不局限于 n-1 的命题。这是算术基本定理的存在性证明。",
        "tags": "强归纳法,素数分解,算术基本定理"
    },
    {
        "chapter": "第5章", "title": "递归数列求解",
        "question": "已知 a₁ = 1，aₙ = 2·aₙ₋₁ + 1 (n ≥ 2)。求 aₙ 的通项公式，并用归纳法验证。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "枚举前几项", "content": "a₁ = 1, a₂ = 3, a₃ = 7, a₄ = 15, a₅ = 31。猜想 aₙ = 2ⁿ - 1。"},
            {"title": "验证通项", "content": "代入递推：若 aₙ₋₁ = 2^(n-1) - 1，则 aₙ = 2·(2^(n-1) - 1) + 1 = 2ⁿ - 2 + 1 = 2ⁿ - 1。符合。"},
            {"title": "归纳基础", "content": "n=1：a₁ = 1 = 2¹ - 1 = 1 ✓。"},
            {"title": "归纳步骤", "content": "假设 aₖ = 2ᵏ - 1，则 aₖ₊₁ = 2·aₖ + 1 = 2(2ᵏ - 1) + 1 = 2^(k+1) - 1。"},
            {"title": "结论", "content": "由归纳法，aₙ = 2ⁿ - 1 对所有正整数 n 成立。"}
        ],
        "answer": "aₙ = 2ⁿ - 1。",
        "summary": "解线性递推：先枚举前几项猜通项 → 用归纳法严格验证。这是发现与证明并用的思路。",
        "tags": "递推,通项,归纳验证"
    },
    {
        "chapter": "第5章", "title": "集合恒等式归纳",
        "question": "用归纳法证明：若 |A| = n，则 |P(A)| = 2ⁿ。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "归纳基础", "content": "n = 0：A = ∅，P(A) = {∅}，|P(A)| = 1 = 2⁰。成立。"},
            {"title": "归纳假设", "content": "假设对某个 k ≥ 0，所有 |A| = k 的集合满足 |P(A)| = 2ᵏ。"},
            {"title": "归纳步骤", "content": "设 |A| = k+1，取 a ∈ A，令 B = A - {a}，则 |B| = k。"},
            {"title": "分析 P(A) 结构", "content": "A 的子集分两类：不含 a 的子集（即 B 的子集）和含 a 的子集。前者有 |P(B)| = 2ᵏ 个；后者可通过\"在 B 的子集中加入 a\"得到，也有 2ᵏ 个。"},
            {"title": "计算总数", "content": "|P(A)| = 2ᵏ + 2ᵏ = 2·2ᵏ = 2^(k+1)。"},
            {"title": "结论", "content": "由归纳法，|A| = n 时 |P(A)| = 2ⁿ。"}
        ],
        "answer": "命题成立。",
        "summary": "幂集基数归纳证明的关键：将子集按是否包含某元素分为两类计数。",
        "tags": "幂集,归纳,集合"
    },
    {
        "chapter": "第5章", "title": "汉诺塔问题",
        "question": "汉诺塔有 n 个圆盘，求最少移动次数 H(n) 并用归纳法证明。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "建立递推", "content": "H(1) = 1；H(n) = 2·H(n-1) + 1：把 n-1 个盘子从 A 移到 B（H(n-1) 次），把最大盘从 A 移到 C（1 次），再把 n-1 个盘从 B 移到 C（H(n-1) 次）。"},
            {"title": "猜想通项", "content": "枚举 H(1)=1, H(2)=3, H(3)=7, H(4)=15。猜想 H(n) = 2ⁿ - 1。"},
            {"title": "归纳基础", "content": "n = 1：2¹ - 1 = 1 = H(1) ✓。"},
            {"title": "归纳步骤", "content": "假设 H(k) = 2ᵏ - 1。则 H(k+1) = 2·H(k) + 1 = 2(2ᵏ - 1) + 1 = 2^(k+1) - 1。"},
            {"title": "结论", "content": "由归纳法，H(n) = 2ⁿ - 1。"}
        ],
        "answer": "H(n) = 2ⁿ - 1。",
        "summary": "分治递推：把问题分解为同型子问题，是算法设计与归纳证明的共同思路。",
        "tags": "汉诺塔,分治,递推"
    },
    {
        "chapter": "第5章", "title": "第二归纳法",
        "question": "用第二数学归纳法证明：第 n 个斐波那契数 F(n) ≤ 2ⁿ，其中 F(1)=F(2)=1, F(n)=F(n-1)+F(n-2)。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "回顾第二归纳法", "content": "第二归纳法：假设对所有 k < n 命题成立，证明对 n 成立。"},
            {"title": "归纳基础", "content": "n = 1：F(1) = 1 ≤ 2¹ = 2 ✓。\nn = 2：F(2) = 1 ≤ 2² = 4 ✓。"},
            {"title": "归纳假设", "content": "假设对所有 1 ≤ k < n（n ≥ 3），F(k) ≤ 2ᵏ。"},
            {"title": "归纳步骤", "content": "F(n) = F(n-1) + F(n-2) ≤ 2^(n-1) + 2^(n-2)（应用归纳假设两次）= 2^(n-2)(2 + 1) = 3·2^(n-2)。"},
            {"title": "放缩", "content": "需证 F(n) ≤ 2ⁿ。由 3·2^(n-2) ≤ 2ⁿ ⟺ 3 ≤ 4 ✓（n ≥ 2 时成立）。故 F(n) ≤ 2ⁿ。"},
            {"title": "结论", "content": "由第二归纳法，F(n) ≤ 2ⁿ 对所有正整数 n 成立。"}
        ],
        "answer": "命题成立。",
        "summary": "第二归纳法（强归纳）允许使用所有更小情形的假设，适用于递推依赖多个前值的命题。",
        "tags": "第二归纳法,斐波那契,不等式"
    },

    # ===================== 第6章 计数原理（8道） =====================
    {
        "chapter": "第6章", "title": "排列组合基础",
        "question": "5 个人排成一排，有多少种排法？若其中甲、乙必须相邻呢？",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "无约束的排列", "content": "5 人排成排的排列数 P(5,5) = 5! = 120。"},
            {"title": "甲乙相邻的处理", "content": "将甲乙视为一个整体，则共有 4 个对象（整体 + 其余 3 人），排列数 4! = 24。"},
            {"title": "甲乙内部排列", "content": "甲乙在整体内部有 2 种排法（甲乙或乙甲）。"},
            {"title": "总排列数", "content": "总排法 = 4! × 2 = 48。"}
        ],
        "answer": "无约束 120 种；甲乙相邻 48 种。",
        "summary": "相邻问题用\"捆绑法\"：将相邻元素视为整体，再乘以内部排列。",
        "tags": "排列,捆绑法,相邻问题"
    },
    {
        "chapter": "第6章", "title": "组合数性质",
        "question": "证明：C(n, k) = C(n, n-k)。",
        "question_type": "proof", "difficulty": "easy",
        "steps": [
            {"title": "代入组合数公式", "content": "C(n, k) = n! / (k!(n-k)!)。"},
            {"title": "替换 k 为 n-k", "content": "C(n, n-k) = n! / ((n-k)!(n-(n-k))!) = n! / ((n-k)!·k!) = C(n, k)。"},
            {"title": "组合解释", "content": "选 k 个元素等价于选 n-k 个不选的元素，故二者计数相同。"}
        ],
        "answer": "等式成立。",
        "summary": "C(n,k) = C(n, n-k) 反映了\"选\"与\"不选\"的对偶性，是组合对称性的体现。",
        "tags": "组合数,对称性,二项式"
    },
    {
        "chapter": "第6章", "title": "容斥原理应用",
        "question": "100 名学生中，60 人选修数学，50 人选修物理，30 人选修化学，20 人同时选数学和物理，15 人同时选数学和化学，10 人同时选物理和化学，5 人三门全选。求至少选一门的学生数。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "回顾容斥原理", "content": "三集合并的容斥：|A∪B∪C| = |A| + |B| + |C| - |A∩B| - |A∩C| - |B∩C| + |A∩B∩C|。"},
            {"title": "代入数据", "content": "|A∪B∪C| = 60 + 50 + 30 - 20 - 15 - 10 + 5 = 100。"},
            {"title": "解释", "content": "100 名学生全部至少选了一门，恰好覆盖了整个学生群体。"}
        ],
        "answer": "100 人。",
        "summary": "容斥原理：奇数个集合相加，偶数个集合相减。注意\"+三交集\"在最后。",
        "tags": "容斥原理,集合,并集"
    },
    {
        "chapter": "第6章", "title": "二项式定理",
        "question": "求 (x + y)⁵ 展开式中 x³y² 的系数。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "回顾二项式定理", "content": "(x + y)ⁿ = Σ C(n, k) x^(n-k) yᵏ，其中 k = 0,1,...,n。"},
            {"title": "对应 k 值", "content": "x³y² 对应 n = 5, k = 2（即 y² 项）。"},
            {"title": "代入系数", "content": "系数 = C(5, 2) = 5!/(2!·3!) = (5·4)/(2·1) = 10。"}
        ],
        "answer": "10",
        "summary": "二项式系数 C(n, k) 给出展开式中 x^(n-k)yᵏ 的系数，组合意义是选 k 个 y。",
        "tags": "二项式定理,展开式,组合"
    },
    {
        "chapter": "第6章", "title": "鸽巢原理应用",
        "question": "证明：从 1 到 2n 的整数中任取 n+1 个数，必有两个数互为倍数关系。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "构造鸽巢", "content": "将每个数 m 写成 m = 2ᵏ · t（t 为奇数），称为\"奇部分\"。1 到 2n 中奇数有 n 个：1, 3, ..., 2n-1。"},
            {"title": "确定鸽巢数", "content": "奇部分 t 的取值共有 n 种（1 到 2n-1 中的奇数）。"},
            {"title": "应用鸽巢原理", "content": "取 n+1 个数，其奇部分 t 只有 n 种取值，故必有两个数 a, b 奇部分相同。"},
            {"title": "分析两数关系", "content": "设 a = 2ⁱ · t，b = 2ʲ · t。若 i ≤ j，则 b = 2^(j-i) · a，b 是 a 的倍数；反之亦然。"},
            {"title": "结论", "content": "故必有两数互为倍数关系。"}
        ],
        "answer": "命题成立。",
        "summary": "鸽巢原理应用关键：通过适当分组构造鸽巢，使目标关系自然成立。",
        "tags": "鸽巢原理,倍数,证明"
    },
    {
        "chapter": "第6章", "title": "重复排列",
        "question": "单词 \"MATHEMATICS\" 的 11 个字母可以排成多少种不同的字母排列？",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "分析字母重复", "content": "MATHEMATICS 中字母：M(2), A(2), T(2), H(1), E(1), I(1), C(1), S(1)。共 11 个字母。"},
            {"title": "应用重复排列公式", "content": "重排数 = n! / (n₁! · n₂! · ... · nₖ!)，其中 n=11, n₁=n₂=n₃=2，其余为 1。"},
            {"title": "代入计算", "content": "= 11! / (2! · 2! · 2!) = 39916800 / 8 = 4989600。"}
        ],
        "answer": "4989600 种。",
        "summary": "重复排列：n 个物品中有组内相同，重排数为 n!/(∏nᵢ!)。",
        "tags": "重复排列,字母重排,除法原理"
    },
    {
        "chapter": "第6章", "title": "可重复组合",
        "question": "从 4 种甜点中选购 6 份（每种可重复选购），有多少种选购方式？",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "识别问题类型", "content": "可重复组合：从 n 类物品中选 r 个，每类可选多次。公式为 C(n+r-1, r)。"},
            {"title": "代入公式", "content": "n = 4（类），r = 6（份）。方案数 = C(4+6-1, 6) = C(9, 6)。"},
            {"title": "利用对称性化简", "content": "C(9, 6) = C(9, 3) = 9!/(3!·6!) = (9·8·7)/(3·2·1) = 84。"}
        ],
        "answer": "84 种。",
        "summary": "可重复组合公式 C(n+r-1, r) = \"隔板法\"：n 类物品间有 n-1 个隔板，共 n+r-1 个位置选 n-1 个隔板。",
        "tags": "可重复组合,隔板法,等价转化"
    },
    {
        "chapter": "第6章", "title": "错排问题",
        "question": "4 封信装入 4 个信封，求全部装错的方法数 D₄。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "回顾错排公式", "content": "错排数 Dₙ = n! · Σ((-1)^k / k!), k=0..n。即用容斥：总数减去至少 1 封正确，加上至少 2 封正确，..."},
            {"title": "代入公式", "content": "D₄ = 4! · (1 - 1 + 1/2 - 1/6 + 1/24)\n= 24 · (1/2 - 1/6 + 1/24)\n= 24 · (12/24 - 4/24 + 1/24)\n= 24 · 9/24\n= 9。"},
            {"title": "验证", "content": "也可递推：Dₙ = (n-1)(Dₙ₋₁ + Dₙ₋₂)。D₁=0, D₂=1, D₃=2·(1+0)=2, D₄=3·(2+1)=9 ✓。"}
        ],
        "answer": "D₄ = 9。",
        "summary": "错排公式：Dₙ = n!·Σ(-1)^k/k!；递推 Dₙ = (n-1)(Dₙ₋₁ + Dₙ₋₂)。",
        "tags": "错排,容斥,递推"
    },

    # ===================== 第7章 离散概率（8道） =====================
    {
        "chapter": "第7章", "title": "古典概型",
        "question": "从 52 张扑克牌中随机抽取 5 张，求得到\"两对\"（两对相同点数 + 1 张其他）的概率。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "计算总抽取数", "content": "总抽法 = C(52, 5) = 2598960。"},
            {"title": "选择两对的点数", "content": "从 13 个点数中选 2 个点数：C(13, 2) = 78。"},
            {"title": "选两对的 suit", "content": "每个点数选 2 张花色：C(4, 2) = 6，两个点数共 6 × 6 = 36 种。"},
            {"title": "选第 5 张牌", "content": "第 5 张从剩余 11 个点数中选一个（44 张牌），有 44 种选法。"},
            {"title": "计算有利事件数", "content": "有利事件 = 78 × 36 × 44 = 123552。"},
            {"title": "计算概率", "content": "P = 123552 / 2598960 ≈ 0.0475 = 4.75%。"}
        ],
        "answer": "约 4.75%。",
        "summary": "古典概型 = 有利事件 / 总事件；扑克问题关键是\"有序选择\"与\"无序选择\"的区分。",
        "tags": "古典概型,扑克,组合"
    },
    {
        "chapter": "第7章", "title": "条件概率",
        "question": "某疾病发病率为 1%。检测方法：真阳性率 99%，假阳性率 5%。某人检测为阳性，求其真实患病的概率。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "定义事件", "content": "D：患病，Dᶜ：未患病；T：检测阳性。P(D) = 0.01, P(Dᶜ) = 0.99, P(T|D) = 0.99, P(T|Dᶜ) = 0.05。"},
            {"title": "应用贝叶斯公式", "content": "P(D|T) = P(T|D)·P(D) / P(T)，其中 P(T) = P(T|D)·P(D) + P(T|Dᶜ)·P(Dᶜ)。"},
            {"title": "计算分母", "content": "P(T) = 0.99 × 0.01 + 0.05 × 0.99 = 0.0099 + 0.0495 = 0.0594。"},
            {"title": "计算后验", "content": "P(D|T) = 0.0099 / 0.0594 ≈ 0.1667 = 16.67%。"},
            {"title": "解释", "content": "尽管检测准确率看似高，但发病率低导致阳性结果中真阳性比例仅约 16.7%。"}
        ],
        "answer": "约 16.67%。",
        "summary": "贝叶斯公式：P(D|T) = P(T|D)·P(D) / P(T)。当发病率低时，假阳性会显著拉低阳性预测值。",
        "tags": "贝叶斯,条件概率,医学统计"
    },
    {
        "chapter": "第7章", "title": "期望值计算",
        "question": "掷一颗公平骰子，求点数 X 的期望 E[X] 和方差 Var(X)。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "确定分布", "content": "X 取值 1, 2, 3, 4, 5, 6，每个概率 1/6。"},
            {"title": "求期望", "content": "E[X] = (1+2+3+4+5+6)/6 = 21/6 = 3.5。"},
            {"title": "求 E[X²]", "content": "E[X²] = (1+4+9+16+25+36)/6 = 91/6 ≈ 15.167。"},
            {"title": "求方差", "content": "Var(X) = E[X²] - (E[X])² = 91/6 - (3.5)² = 91/6 - 12.25 = 15.167 - 12.25 = 2.917 ≈ 35/12。"}
        ],
        "answer": "E[X] = 3.5，Var(X) = 35/12 ≈ 2.917。",
        "summary": "期望：E[X] = Σ x·P(x)；方差：Var(X) = E[X²] - (E[X])²。",
        "tags": "期望,方差,离散分布"
    },
    {
        "chapter": "第7章", "title": "独立事件",
        "question": "甲乙两人各掷一颗骰子，A = \"甲掷出 6\"，B = \"乙掷出偶数\"。判断 A、B 是否独立。",
        "question_type": "proof", "difficulty": "easy",
        "steps": [
            {"title": "计算 P(A)", "content": "P(A) = 1/6（甲掷出 6 的概率）。"},
            {"title": "计算 P(B)", "content": "P(B) = 3/6 = 1/2（乙掷出 2、4、6 中任一个）。"},
            {"title": "计算 P(A∩B)", "content": "甲乙独立掷骰，A 与 B 同时发生：P(A∩B) = P(A)·P(B) = (1/6)·(1/2) = 1/12。"},
            {"title": "验证独立", "content": "P(A∩B) = P(A)·P(B) 成立，故 A、B 独立。"}
        ],
        "answer": "A、B 相互独立。",
        "summary": "事件 A、B 独立当且仅当 P(A∩B) = P(A)·P(B)。不同骰子结果天然独立。",
        "tags": "独立事件,概率,乘法规则"
    },
    {
        "chapter": "第7章", "title": "二项分布",
        "question": "掷一枚公平硬币 10 次，求恰好得到 7 次正面的概率。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "识别分布", "content": "n 次独立伯努利试验，每次成功概率 p，成功次数 X ~ B(n, p)。此处 n=10, p=0.5。"},
            {"title": "应用二项分布公式", "content": "P(X = k) = C(n, k) · pᵏ · (1-p)^(n-k)。"},
            {"title": "代入计算", "content": "P(X = 7) = C(10, 7) · (0.5)⁷ · (0.5)³ = 120 · (1/2)¹⁰ = 120/1024 = 15/128 ≈ 0.1172。"}
        ],
        "answer": "P(X = 7) ≈ 0.1172 (约 11.72%)。",
        "summary": "二项分布：n 次独立伯努利试验中成功 k 次的概率，公式 P(X=k) = C(n,k)·pᵏ·(1-p)^(n-k)。",
        "tags": "二项分布,伯努利,概率"
    },
    {
        "chapter": "第7章", "title": "全概率公式",
        "question": "三个盒子：A 含 2 金 1 银，B 含 1 金 2 银，C 含 2 金 2 银。随机选一个盒子并随机取一球。求取到金球的概率。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "设定事件", "content": "选盒概率 P(A)=P(B)=P(C)=1/3。金球概率：P(G|A)=2/3, P(G|B)=1/3, P(G|C)=2/4=1/2。"},
            {"title": "应用全概率公式", "content": "P(G) = P(G|A)·P(A) + P(G|B)·P(B) + P(G|C)·P(C)。"},
            {"title": "代入计算", "content": "P(G) = (2/3)·(1/3) + (1/3)·(1/3) + (1/2)·(1/3) = 2/9 + 1/9 + 1/6 = 4/18 + 2/18 + 3/18 = 9/18 = 1/2。"}
        ],
        "answer": "P(G) = 1/2。",
        "summary": "全概率公式：将复杂事件分解为互斥情形之和，P(B) = Σ P(B|Aᵢ)·P(Aᵢ)。",
        "tags": "全概率公式,分解,条件概率"
    },
    {
        "chapter": "第7章", "title": "几何概型",
        "question": "在区间 [0, 1] 上随机取两个数 x, y，求 |x - y| < 1/2 的概率。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "几何表示", "content": "把 (x, y) 视为单位正方形 [0,1]×[0,1] 内的随机点，总面积为 1。"},
            {"title": "分析目标区域", "content": "|x - y| < 1/2 等价于 -1/2 < x - y < 1/2，即 y < x + 1/2 且 y > x - 1/2。"},
            {"title": "计算补集", "content": "补集：|x - y| ≥ 1/2，即 y ≥ x + 1/2 或 y ≤ x - 1/2，是两个直角三角形，每个腰长 1/2，面积均为 (1/2)·(1/2)·(1/2) = 1/8。"},
            {"title": "总补集面积", "content": "补集总面积 = 2 × 1/8 = 1/4。"},
            {"title": "目标概率", "content": "P = 1 - 1/4 = 3/4。"}
        ],
        "answer": "P = 3/4。",
        "summary": "几何概型：概率 = 目标区域测度 / 总测度。常转化为平面区域面积计算。",
        "tags": "几何概型,面积,补集法"
    },
    {
        "chapter": "第7章", "title": "生日问题",
        "question": "30 人中至少两人生日相同的概率约为多少？（设一年 365 天，生日均匀分布）",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "计算补集", "content": "P(至少两人生日相同) = 1 - P(30 人生日互不相同)。"},
            {"title": "计算互不相同概率", "content": "P(互不相同) = (365/365)·(364/365)·...·(336/365) = 365!/(335!·365³⁰)。"},
            {"title": "近似计算", "content": "利用近似：P(互不相同) ≈ exp(-30·29/(2·365)) = exp(-435/365) ≈ exp(-1.19) ≈ 0.304。"},
            {"title": "最终概率", "content": "P(至少两人相同) ≈ 1 - 0.304 = 0.696 ≈ 70%。"}
        ],
        "answer": "约 70%。",
        "summary": "生日问题展示\"直觉与概率相悖\"：30 人中两人同生日的概率已超 70%。补集法和近似是常用技巧。",
        "tags": "生日问题,补集法,近似计算"
    },

    # ===================== 第8章 高级计数（8道） =====================
    {
        "chapter": "第8章", "title": "线性齐次递推求解",
        "question": "解递推 aₙ = 2aₙ₋₁ + 3aₙ₋₂，初始条件 a₀ = 1, a₁ = 2。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "写出特征方程", "content": "递推 aₙ - 2aₙ₋₁ - 3aₙ₋₂ = 0 的特征方程：r² - 2r - 3 = 0。"},
            {"title": "求特征根", "content": "r = (2 ± √(4+12))/2 = (2 ± 4)/2，得 r₁ = 3, r₂ = -1。两个不同实根。"},
            {"title": "写出通解", "content": "通解 aₙ = C₁·3ⁿ + C₂·(-1)ⁿ。"},
            {"title": "代入初始条件", "content": "n=0: C₁ + C₂ = 1；\nn=1: 3C₁ - C₂ = 2。"},
            {"title": "解方程组", "content": "由 C₂ = 1 - C₁ 代入第二式：3C₁ - (1 - C₁) = 2，4C₁ = 3，C₁ = 3/4，C₂ = 1/4。"},
            {"title": "写出特解", "content": "aₙ = (3/4)·3ⁿ + (1/4)·(-1)ⁿ = (3ⁿ⁺¹ + (-1)ⁿ)/4。"}
        ],
        "answer": "aₙ = (3ⁿ⁺¹ + (-1)ⁿ) / 4。",
        "summary": "线性齐次递推求解：写特征方程 → 求根 → 通解 → 代初始条件定常数。",
        "tags": "递推,特征方程,通解"
    },
    {
        "chapter": "第8章", "title": "线性非齐次递推",
        "question": "解递推 aₙ = 2aₙ₋₁ + 3，a₀ = 1。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "分解问题", "content": "通解 = 齐次通解 + 非齐次特解。"},
            {"title": "求齐次通解", "content": "齐次方程 aₙ - 2aₙ₋₁ = 0 的特征方程 r - 2 = 0，r = 2。通解 aₙ^(h) = C·2ⁿ。"},
            {"title": "求特解", "content": "非齐次项 f(n) = 3 是常数。设特解 aₙ^(p) = A（常数），代入：A = 2A + 3，得 A = -3。"},
            {"title": "写出通解", "content": "aₙ = C·2ⁿ - 3。"},
            {"title": "代入初始条件", "content": "n=0: C - 3 = 1，C = 4。"},
            {"title": "写出特解", "content": "aₙ = 4·2ⁿ - 3。"}
        ],
        "answer": "aₙ = 4·2ⁿ - 3。",
        "summary": "非齐次递推：通解 = 齐次通解 + 非齐次特解。特解形式与非齐次项同型。",
        "tags": "非齐次递推,特解,通解"
    },
    {
        "chapter": "第8章", "title": "生成函数应用",
        "question": "用生成函数求递推 aₙ = aₙ₋₁ + aₙ₋₂，a₀ = 0, a₁ = 1（斐波那契数列）的通项公式。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "构造生成函数", "content": "设 G(x) = a₀ + a₁x + a₂x² + ... = Σ aₙxⁿ。"},
            {"title": "利用递推", "content": "由 aₙ = aₙ₋₁ + aₙ₋₂ (n≥2)，乘以 xⁿ 并求和：Σaₙxⁿ = x·Σaₙ₋₁xⁿ⁻¹ + x²·Σaₙ₋₂xⁿ⁻²。\n即 G(x) - a₀ - a₁x = x(G(x) - a₀) + x²G(x)。"},
            {"title": "代入初始值", "content": "a₀=0, a₁=1：G(x) - x = x·G(x) + x²·G(x)，即 G(x)(1 - x - x²) = x。"},
            {"title": "解出 G(x)", "content": "G(x) = x / (1 - x - x²)。"},
            {"title": "部分分式分解", "content": "1 - x - x² = -(x² + x - 1) = -(x - α)(x - β)，其中 α = (-1+√5)/2, β = (-1-√5)/2。\nG(x) = x / (-(x-α)(x-β)) = -x/((x-α)(x-β))。"},
            {"title": "展开求系数", "content": "经部分分式与展开，得 aₙ = (φⁿ - ψⁿ)/√5，其中 φ = (1+√5)/2, ψ = (1-√5)/2。"}
        ],
        "answer": "aₙ = (φⁿ - ψⁿ)/√5，φ=(1+√5)/2, ψ=(1-√5)/2。",
        "summary": "生成函数将递推转化为代数方程，通过部分分式和幂级数展开获得通项。",
        "tags": "生成函数,斐波那契,部分分式"
    },
    {
        "chapter": "第8章", "title": "分递推主定理",
        "question": "用主定理求 T(n) = 4T(n/2) + n² 的渐近阶。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "识别参数", "content": "T(n) = aT(n/b) + f(n)，a = 4, b = 2, f(n) = n²。"},
            {"title": "计算 n^(log_b a)", "content": "log_b a = log₂ 4 = 2，故 n^(log_b a) = n²。"},
            {"title": "比较 f(n) 与 n^(log_b a)", "content": "f(n) = n² = Θ(n^(log_b a))，属主定理情形 2（二者同阶）。"},
            {"title": "应用主定理", "content": "情形 2：T(n) = Θ(n^(log_b a) · log n) = Θ(n² log n)。"}
        ],
        "answer": "T(n) = Θ(n² log n)。",
        "summary": "主定理：比较 f(n) 与 n^(log_b a)，分三种情形确定 T(n) 的渐近阶。",
        "tags": "主定理,分治,渐近分析"
    },
    {
        "chapter": "第8章", "title": "分步计数原理",
        "question": "从 5 男 4 女中选 3 人，要求至少有 1 名女生，有多少种选法？",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "用补集法", "content": "总选法 - 全男选法。总选法 = C(9, 3) = 84；全男选法 = C(5, 3) = 10。"},
            {"title": "求差", "content": "至少 1 女 = 84 - 10 = 74。"},
            {"title": "验证（分类法）", "content": "1女2男：C(4,1)·C(5,2) = 4·10 = 40；\n2女1男：C(4,2)·C(5,1) = 6·5 = 30；\n3女0男：C(4,3) = 4；\n合计：40+30+4 = 74 ✓。"}
        ],
        "answer": "74 种。",
        "summary": "\"至少\"型问题用补集法常更简洁；分类法可作验证。",
        "tags": "分步计数,补集法,组合"
    },
    {
        "chapter": "第8章", "title": "Stirling 数应用",
        "question": "求将 5 个不同的元素划分为 3 个非空子集的方法数 S(5, 3)。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "回顾第二类 Stirling 数", "content": "S(n, k) 表示将 n 个不同元素划分为 k 个非空子集的方式数。递推：S(n, k) = k·S(n-1, k) + S(n-1, k-1)，S(0,0)=1, S(n,0)=0 (n>0), S(n,1)=S(n,n)=1。"},
            {"title": "逐步计算", "content": "S(1,1)=1;\nS(2,1)=1, S(2,2)=1;\nS(3,1)=1, S(3,2)=2·1+1=3, S(3,3)=1;\nS(4,1)=1, S(4,2)=2·1+3=7, S(4,3)=3·1+3=6, S(4,4)=1;\nS(5,1)=1, S(5,2)=2·1+7=15, S(5,3)=3·6+7=25。"},
            {"title": "结论", "content": "S(5, 3) = 25。"}
        ],
        "answer": "S(5, 3) = 25。",
        "summary": "第二类 Stirling 数 S(n,k) 表示将 n 个不同元素分成 k 个非空子集的方式数。",
        "tags": "Stirling数,集合划分,递推"
    },
    {
        "chapter": "第8章", "title": "指数生成函数",
        "question": "用生成函数求从 {1,2,3} 中允许重复地取 r 个，且 1 出现偶数次的取法数 aᵣ 的通项。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "构造生成函数", "content": "每个数字对应一个因子：\n1 偶数次：1 + x²/2! + x⁴/4! + ... = (eˣ + e⁻ˣ)/2 = cosh(x)\n2 任意次：1 + x + x²/2! + ... = eˣ\n3 任意次：eˣ"},
            {"title": "乘积", "content": "G(x) = cosh(x) · eˣ · eˣ = cosh(x) · e²ˣ = (eˣ + e⁻ˣ)/2 · e²ˣ = (e³ˣ + eˣ)/2。"},
            {"title": "展开", "content": "(e³ˣ + eˣ)/2 = (1/2)·Σ(3ⁿxⁿ/n!) + (1/2)·Σ(xⁿ/n!) = Σ[(3ⁿ + 1)/2]·xⁿ/n!。"},
            {"title": "提取系数", "content": "故 aᵣ = (3ʳ + 1)/2。"}
        ],
        "answer": "aᵣ = (3ʳ + 1)/2。",
        "summary": "指数生成函数适用于\"带重复限制\"的排列计数；eˣ 对应无限制，cosh(x) 对应偶数次。",
        "tags": "指数生成函数,排列,计数"
    },
    {
        "chapter": "第8章", "title": "Catalan 数",
        "question": "求 n = 4 时的 Catalan 数 C₄，并解释其组合意义。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾 Catalan 公式", "content": "Cₙ = C(2n, n)/(n+1) = (1/(n+1))·(2n)!/(n!)²。"},
            {"title": "代入 n = 4", "content": "C₄ = C(8, 4)/5 = 70/5 = 14。"},
            {"title": "组合意义", "content": "C₄ = 14 表示：4 对括号的合法配对方式、4×4 网格从左下到右上的不穿过对角线的路径数、4 个节点的不同二叉树形状数等都是 14。"}
        ],
        "answer": "C₄ = 14。",
        "summary": "Catalan 数 Cₙ = C(2n,n)/(n+1)，组合意义包括合法括号、不交叉路径、二叉树形状等。",
        "tags": "Catalan数,组合意义,二叉树"
    },

    # ===================== 第9章 关系（8道） =====================
    {
        "chapter": "第9章", "title": "等价关系判定",
        "question": "设 R 是整数集 Z 上的关系：aRb 当且仅当 a - b 是 3 的倍数。证明 R 是等价关系，并写出其等价类。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "验证自反性", "content": "对任意 a ∈ Z，a - a = 0 = 3·0，故 aRa。自反性成立。"},
            {"title": "验证对称性", "content": "若 aRb，则 a - b = 3k，故 b - a = -3k 也是 3 的倍数，即 bRa。对称性成立。"},
            {"title": "验证传递性", "content": "若 aRb 且 bRc，则 a - b = 3k, b - c = 3m，故 a - c = (a-b)+(b-c) = 3(k+m) 是 3 的倍数，即 aRc。传递性成立。"},
            {"title": "确定等价类", "content": "R 是等价关系。等价类为：[0] = {..., -6, -3, 0, 3, 6, ...}（模 3 余 0）；[1] = {..., -5, -2, 1, 4, 7, ...}（模 3 余 1）；[2] = {..., -4, -1, 2, 5, 8, ...}（模 3 余 2）。"}
        ],
        "answer": "R 是等价关系；等价类为 [0]、[1]、[2]（模 3 同余类）。",
        "summary": "等价关系 = 自反 + 对称 + 传递。同余关系是典型等价关系，等价类对应模数的余数。",
        "tags": "等价关系,同余,等价类"
    },
    {
        "chapter": "第9章", "title": "偏序关系判定",
        "question": "设 A = {1, 2, 3, 4, 6, 12}，R 为整除关系（a | b）。证明 (A, |) 是偏序集，并判断是否为全序。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "验证自反性", "content": "对任意 a ∈ A，a | a（因 a = a·1）。成立。"},
            {"title": "验证反对称性", "content": "若 a | b 且 b | a，则 a ≤ b 且 b ≤ a，故 a = b。成立。"},
            {"title": "验证传递性", "content": "若 a | b 且 b | c，则 b = a·m, c = b·n = a·mn，故 a | c。成立。"},
            {"title": "结论：偏序", "content": "(A, |) 是偏序集。"},
            {"title": "判断全序", "content": "2 与 3 不可比（2 ∤ 3 且 3 ∤ 2），故不是全序。"}
        ],
        "answer": "(A, |) 是偏序集但非全序集（如 2、3 不可比）。",
        "summary": "偏序 = 自反 + 反对称 + 传递；全序还要求任意两元素可比。整除关系是典型偏序。",
        "tags": "偏序,整除,反对称"
    },
    {
        "chapter": "第9章", "title": "关系闭包计算",
        "question": "设 A = {1, 2, 3}，R = {(1,2), (2,3)}。求 R 的传递闭包 t(R)。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾传递闭包", "content": "传递闭包 t(R) 是包含 R 的最小传递关系。常用 Warshall 算法或直接枚举。"},
            {"title": "初始矩阵", "content": "R 对应矩阵 M = [[0,1,0],[0,0,1],[0,0,0]]。"},
            {"title": "应用 Warshall 算法", "content": "对每个中间点 k：\n- k=1：无新对（没有 (x,1) 且 (1,y) 同时存在）。\n- k=2：(1,2) 与 (2,3) 同时存在，加入 (1,3)。\n- k=3：无新对。"},
            {"title": "结果", "content": "t(R) = {(1,2), (2,3), (1,3)}。"}
        ],
        "answer": "t(R) = {(1,2), (2,3), (1,3)}。",
        "summary": "传递闭包：通过中间点逐步添加 (a,c) 使得存在 b 使 (a,b),(b,c)∈R。Warshall 算法是经典方法。",
        "tags": "传递闭包,Warshall,关系"
    },
    {
        "chapter": "第9章", "title": "关系复合",
        "question": "设 A = {1,2,3,4}，R = {(1,2), (2,3), (3,4)}，S = {(2,4), (3,1)}。求 R ∘ S。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "回顾复合定义", "content": "R ∘ S = {(a, c) : ∃b, (a, b) ∈ S 且 (b, c) ∈ R}（先 S 后 R）。"},
            {"title": "逐对检查", "content": "对 (2,4) ∈ S：检查是否存在 (4, c) ∈ R？没有。\n对 (3,1) ∈ S：检查 (1, c) ∈ R？有 (1,2)，故 (3, 2) ∈ R∘S。"},
            {"title": "结果", "content": "R ∘ S = {(3, 2)}。"}
        ],
        "answer": "R ∘ S = {(3, 2)}。",
        "summary": "关系复合 R∘S = {(a,c) : ∃b, (a,b)∈S 且 (b,c)∈R}。注意运算顺序：先 S 后 R。",
        "tags": "关系复合,运算,顺序"
    },
    {
        "chapter": "第9章", "title": "Hasse 图绘制",
        "question": "设 A = {1, 2, 3, 6, 12}，偏序为整除关系。画出其 Hasse 图并指出极大元、极小元、最大元、最小元。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "分析覆盖关系", "content": "去除自反和传递边后，覆盖关系：1 | 2, 1 | 3, 2 | 6, 3 | 6, 6 | 12。"},
            {"title": "绘制 Hasse 图", "content": "层 1：1（底部）；层 2：2, 3；层 3：6；层 4：12（顶部）。边：1-2, 1-3, 2-6, 3-6, 6-12。"},
            {"title": "确定极小元", "content": "极小元：没有比它更小的元素，是 1。"},
            {"title": "确定极大元", "content": "极大元：没有比它更大的元素，是 12。"},
            {"title": "确定最小最大元", "content": "最小元：1（所有元素都整除它）；最大元：12（被所有元素整除）。"}
        ],
        "answer": "极小元 = 最小元 = 1；极大元 = 最大元 = 12。",
        "summary": "Hasse 图省略自反边和传递边，仅保留覆盖关系。最小元/最大元若存在则唯一。",
        "tags": "Hasse图,偏序,极值元"
    },
    {
        "chapter": "第9章", "title": "划分与等价关系",
        "question": "设 A = {1, 2, 3, 4, 5}，划分 P = {{1,2}, {3,4}, {5}}。求该划分对应的等价关系 R。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾对应关系", "content": "每个划分唯一确定一个等价关系 R = {(a, b) : a 和 b 在同一块中}。"},
            {"title": "枚举各块内的对", "content": "{1,2} 块：(1,1), (1,2), (2,1), (2,2)。\n{3,4} 块：(3,3), (3,4), (4,3), (4,4)。\n{5} 块：(5,5)。"},
            {"title": "汇总", "content": "R = {(1,1), (1,2), (2,1), (2,2), (3,3), (3,4), (4,3), (4,4), (5,5)}。"}
        ],
        "answer": "R = {(1,1),(1,2),(2,1),(2,2),(3,3),(3,4),(4,3),(4,4),(5,5)}。",
        "summary": "等价关系与划分一一对应：每块内元素彼此相关，块间元素无关。",
        "tags": "划分,等价关系,对应"
    },
    {
        "chapter": "第9章", "title": "Warshall 算法",
        "question": "用 Warshall 算法求 R = {(1,2),(2,3),(3,1)} 在 A = {1,2,3} 上的传递闭包。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "初始矩阵", "content": "M₀ = [[0,1,0],[0,0,1],[1,0,0]]（行 i 列 j 表示 (i,j)）。"},
            {"title": "k = 1", "content": "若 (i,1) 且 (1,j) 在 R 中，则添加 (i,j)。\n(3,1) 存在且 (1,2) 存在，故添加 (3,2)。\nM₁ = [[0,1,0],[0,0,1],[1,1,0]]。"},
            {"title": "k = 2", "content": "(1,2) 和 (3,2) 存在，(2,3) 存在，故添加 (1,3) 和 (3,3)。\nM₂ = [[0,1,1],[0,0,1],[1,1,1]]。"},
            {"title": "k = 3", "content": "存在 (1,3) 与 (3,1), (3,3)；添加 (1,1), (1,3)(已有)。\n存在 (2,3) 与 (3,1), (3,2), (3,3)；添加 (2,1), (2,2), (2,3)(已有)。\nM₃ = [[1,1,1],[1,1,1],[1,1,1]]。"},
            {"title": "结论", "content": "传递闭包为全关系 A×A。"}
        ],
        "answer": "t(R) = A×A = 全部 9 个有序对。",
        "summary": "Warshall 算法：依次以每个点为中间点，更新可达关系。O(n³) 复杂度。",
        "tags": "Warshall算法,传递闭包,矩阵"
    },
    {
        "chapter": "第9章", "title": "函数与关系",
        "question": "设 R 是 A = {1, 2, 3, 4} 上的关系，R = {(1,2), (2,3), (3,4), (4,1)}。判断 R 是否为函数？是否为双射？",
        "question_type": "proof", "difficulty": "easy",
        "steps": [
            {"title": "判断函数", "content": "函数要求每个定义域元素恰有一个像。R 中 1→2, 2→3, 3→4, 4→1，每个元素恰有一个像，定义域为 A 全体，故是函数。"},
            {"title": "判断单射", "content": "不同输入对应不同输出（2,3,4,1 互不相同），是单射。"},
            {"title": "判断满射", "content": "陪域 {1,2,3,4} 中每个元素都有原像（1←4, 2←1, 3←2, 4←3），是满射。"},
            {"title": "结论", "content": "R 既是单射又是满射，是双射。"}
        ],
        "answer": "R 是函数，且是双射。",
        "summary": "函数是特殊关系：每个定义域元素恰有一个像。双射 = 单射 + 满射。",
        "tags": "函数,双射,关系"
    },

    # ===================== 第10章 图论（8道） =====================
    {
        "chapter": "第10章", "title": "握手定理应用",
        "question": "一个图有 6 个顶点，度数分别为 5, 4, 3, 3, 2, 1。判断该图是否可能存在。",
        "question_type": "proof", "difficulty": "easy",
        "steps": [
            {"title": "回顾握手定理", "content": "握手定理：所有顶点度数之和 = 2 × 边数，故度数之和必须是偶数。"},
            {"title": "计算度数和", "content": "5 + 4 + 3 + 3 + 2 + 1 = 18，是偶数。"},
            {"title": "进一步分析", "content": "边数 = 18/2 = 9。度数为 5 的顶点与所有其他 5 个顶点都相邻，但度数为 1 的顶点只能与一个顶点相邻，矛盾（度数 5 的顶点不可能与度数 1 的顶点相邻）。"},
            {"title": "结论", "content": "虽然度数和为偶数，但具体度数序列不满足可实现性条件（Havel-Hakimi 不通过）。该图不可能存在。"}
        ],
        "answer": "该图不可能存在。",
        "summary": "握手定理：度数之和 = 2×边数。必要条件但非充分，还需 Havel-Hakimi 等进一步判定。",
        "tags": "握手定理,度数,图存在性"
    },
    {
        "chapter": "第10章", "title": "欧拉回路判定",
        "question": "判断以下图是否存在欧拉回路：完全图 K₅ 和完全二分图 K₃,₃。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "回顾判定定理", "content": "连通图存在欧拉回路当且仅当所有顶点的度数均为偶数。"},
            {"title": "分析 K₅", "content": "K₅ 中每个顶点度数 = 4（与其他 4 个顶点都相连），均为偶数。连通。"},
            {"title": "结论 K₅", "content": "K₅ 存在欧拉回路。"},
            {"title": "分析 K₃,₃", "content": "K₃,₃ 中每个顶点度数 = 3（与对面 3 个顶点都相连），均为奇数。"},
            {"title": "结论 K₃,₃", "content": "K₃,₃ 不存在欧拉回路（但所有顶点度数为奇数 3，存在欧拉路径但不存在回路）。"}
        ],
        "answer": "K₅ 存在欧拉回路；K₃,₃ 不存在欧拉回路。",
        "summary": "欧拉回路 ⟺ 连通 + 所有点度数为偶数。欧拉路径 ⟺ 连通 + 恰有 0 或 2 个奇度点。",
        "tags": "欧拉回路,完全图,度数"
    },
    {
        "chapter": "第10章", "title": "哈密顿回路判定",
        "question": "判断完全图 K₅ 和彼得森图是否存在哈密顿回路。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "回顾判定", "content": "哈密顿回路经过每个顶点恰一次并回到起点。无简单充要条件，但完全图 Kₙ (n ≥ 3) 一定有哈密顿回路。"},
            {"title": "分析 K₅", "content": "K₅ 是完全图，任意顶点顺序都构成哈密顿回路。故存在。"},
            {"title": "分析彼得森图", "content": "彼得森图是著名的反例：3-正则图，10 个顶点。可证明它不存在哈密顿回路。"},
            {"title": "彼得森证明思路", "content": "彼得森图是 3-正则且每个顶点都在某个 5-圈上。假设存在哈密顿回路（10 个顶点的圈），但与外圈 5 个\"辐条\"的连接方式矛盾。详细证明需分情况讨论。"},
            {"title": "结论", "content": "K₅ 有哈密顿回路；彼得森图没有。"}
        ],
        "answer": "K₅ 有哈密顿回路；彼得森图无。",
        "summary": "哈密顿回路判定困难，无简单充要条件。完全图必有，彼得森图是经典反例。",
        "tags": "哈密顿回路,完全图,彼得森图"
    },
    {
        "chapter": "第10章", "title": "图的矩阵表示",
        "question": "设图 G 的邻接矩阵 A = [[0,1,1],[1,0,1],[1,1,0]]（K₃）。求 A² 并解释其含义。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾邻接矩阵", "content": "A[i][j] = 1 表示顶点 i 与 j 相邻。Aⁿ[i][j] 表示从 i 到 j 长度为 n 的路径数。"},
            {"title": "计算 A²", "content": "A² = A·A，元素 (A²)[i][j] = Σ A[i][k]·A[k][j]。\n(A²)[1][1] = 0·0 + 1·1 + 1·1 = 2\n(A²)[1][2] = 0·1 + 1·0 + 1·1 = 1\n对称地，A² = [[2,1,1],[1,2,1],[1,1,2]]。"},
            {"title": "解释含义", "content": "对角元 (A²)[i][i] = 2 表示从每个顶点回到自身长度为 2 的路径有 2 条（经过另外两个顶点）。非对角元 (A²)[i][j] = 1 表示从 i 到 j 长度为 2 的路径恰有 1 条。"}
        ],
        "answer": "A² = [[2,1,1],[1,2,1],[1,1,2]]，表示长度为 2 的路径数。",
        "summary": "邻接矩阵的幂 Aᵏ 表示长度为 k 的路径数；对角元反映回到自身的路径数。",
        "tags": "邻接矩阵,矩阵幂,路径"
    },
    {
        "chapter": "第10章", "title": "二分图判定",
        "question": "判断 K₃,₃ 是否为二分图，并说明二分图的判定条件。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "回顾二分图定义", "content": "二分图：顶点集可分为两部分 X、Y，所有边的两端分别在 X 和 Y 中（X、Y 内部无边）。"},
            {"title": "分析 K₃,₃", "content": "K₃,₃ 本身就是按定义构造的：两部分各 3 个顶点，所有边横跨两部分。"},
            {"title": "判定条件", "content": "图是二分图 ⟺ 不含奇圈 ⟺ 可用两种颜色正常 2-着色。"},
            {"title": "结论", "content": "K₃,₃ 是二分图，无奇圈。"}
        ],
        "answer": "K₃,₃ 是二分图。",
        "summary": "二分图判定：图不含奇圈 ⟺ 二分图 ⟺ 2-着色。",
        "tags": "二分图,奇圈,着色"
    },
    {
        "chapter": "第10章", "title": "平面图判定",
        "question": "判断 K₅ 和 K₃,₃ 是否为平面图。",
        "question_type": "proof", "difficulty": "hard",
        "steps": [
            {"title": "回顾 Kuratowski 定理", "content": "图是平面图 ⟺ 不含 K₅ 或 K₃,₃ 的细分（同胚）。"},
            {"title": "分析 K₅", "content": "K₅ 本身就是被禁的子图，故不是平面图。也可用欧拉公式验证：n=5, m=10, 若平面则面数 f = 2 - n + m + 1 = 2 - 5 + 10 + 1 = 8？但平面图要求 m ≤ 3n - 6 = 9，矛盾（10 > 9）。"},
            {"title": "分析 K₃,₃", "content": "K₃,₃ 本身是被禁子图。验证：n = 6, m = 9，对二分图 m ≤ 2n - 4 = 8，9 > 8，矛盾。"},
            {"title": "结论", "content": "K₅ 和 K₃,₃ 都不是平面图，它们是最小的非平面图。"}
        ],
        "answer": "两者都不是平面图。",
        "summary": "Kuratowski 定理：平面图 ⟺ 不含 K₅ 或 K₃,₃ 细分。欧拉公式可作辅助验证。",
        "tags": "平面图,Kuratowski定理,欧拉公式"
    },
    {
        "chapter": "第10章", "title": "图着色问题",
        "question": "求完全图 K₄、圈 C₅ 和完全二分图 K₃,₃ 的色数。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾色数定义", "content": "色数 χ(G) 是给图 G 顶点着色所需的最少颜色数，使相邻顶点不同色。"},
            {"title": "K₄ 的色数", "content": "K₄ 中任意两顶点相邻，每顶点需不同色。χ(K₄) = 4。"},
            {"title": "C₅ 的色数", "content": "C₅ 是长度为 5 的圈（奇圈）。奇圈色数为 3。可用贪心：依次着色 1,2,1,2,3。χ(C₅) = 3。"},
            {"title": "K₃,₃ 的色数", "content": "K₃,₃ 是二分图，两部分各用一色。χ(K₃,₃) = 2。"}
        ],
        "answer": "χ(K₄) = 4；χ(C₅) = 3；χ(K₃,₃) = 2。",
        "summary": "完全图 χ(Kₙ) = n；二分图 χ = 2（非平凡）；奇圈 χ = 3，偶圈 χ = 2。",
        "tags": "图着色,色数,完全图"
    },
    {
        "chapter": "第10章", "title": "欧拉公式应用",
        "question": "一个连通平面图有 8 个顶点和 12 条边，求面数。验证是否满足平面图条件。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾欧拉公式", "content": "连通平面图满足：n - m + f = 2，其中 n 顶点数、m 边数、f 面数（含外侧面）。"},
            {"title": "代入求 f", "content": "8 - 12 + f = 2，得 f = 6。"},
            {"title": "验证平面图条件", "content": "平面图要求 m ≤ 3n - 6 = 3·8 - 6 = 18，12 ≤ 18 ✓。满足平面图必要条件。"}
        ],
        "answer": "面数 f = 6。",
        "summary": "欧拉公式：n - m + f = 2（连通平面图）。平面图必要条件：m ≤ 3n - 6。",
        "tags": "欧拉公式,平面图,面数"
    },

    # ===================== 第11章 树（8道） =====================
    {
        "chapter": "第11章", "title": "生成树计数",
        "question": "完全图 K₄ 有多少棵不同的生成树？",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "回顾 Cayley 公式", "content": "完全图 Kₙ 的生成树数为 n^(n-2)。"},
            {"title": "代入 n = 4", "content": "K₄ 的生成树数 = 4^(4-2) = 4² = 16。"}
        ],
        "answer": "16 棵。",
        "summary": "Cayley 公式：完全图 Kₙ 有 n^(n-2) 棵生成树。",
        "tags": "生成树,Cayley公式,完全图"
    },
    {
        "chapter": "第11章", "title": "二叉树性质",
        "question": "一棵满二叉树有 7 个内点（含根）。求总顶点数、叶节点数。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "回顾性质", "content": "满二叉树：每个内点都有 2 个子节点。叶节点数 L = 内点数 I + 1。总顶点数 n = 2I + 1。"},
            {"title": "代入计算", "content": "I = 7，叶节点数 L = 7 + 1 = 8。总顶点数 n = 2·7 + 1 = 15。"}
        ],
        "answer": "总顶点数 15，叶节点数 8。",
        "summary": "满二叉树性质：L = I + 1；n = 2I + 1 = 2L - 1。",
        "tags": "二叉树,满二叉树,叶节点"
    },
    {
        "chapter": "第11章", "title": "树的边数",
        "question": "证明：n 个顶点的树恰有 n - 1 条边。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "回顾树定义", "content": "树是连通无回路的无向图。"},
            {"title": "归纳基础", "content": "n = 1：单顶点无边，0 = 1 - 1。成立。"},
            {"title": "归纳假设", "content": "假设对所有 k 个顶点的树，边数为 k - 1。"},
            {"title": "归纳步骤", "content": "考虑 n = k+1 的树 T。T 连通且无回路，必存在叶节点 v（度数为 1）。删去 v 及其关联边得 T' = T - v，T' 仍是树（连通无回路），且 |V(T')| = k。"},
            {"title": "应用假设", "content": "由归纳假设，|E(T')| = k - 1。又 |E(T)| = |E(T')| + 1 = (k-1) + 1 = k = (k+1) - 1 = n - 1。"},
            {"title": "结论", "content": "由归纳法，所有 n 顶点的树有 n - 1 条边。"}
        ],
        "answer": "命题成立。",
        "summary": "树的等价定义之一：连通 + n-1 条边。叶节点的存在是关键。",
        "tags": "树,边数,归纳"
    },
    {
        "chapter": "第11章", "title": "Huffman 编码",
        "question": "对字符频率 A:5, B:2, C:1, D:1 构造 Huffman 编码。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "初始化", "content": "森林：{A:5, B:2, C:1, D:1}。"},
            {"title": "合并最小两个", "content": "C:1, D:1 最小，合并为 (CD):2。森林：{A:5, B:2, (CD):2}。"},
            {"title": "继续合并", "content": "B:2, (CD):2 最小（并列取任一），合并为 (B(CD)):4。森林：{A:5, (B(CD)):4}。"},
            {"title": "最后一次合并", "content": "A:5, (B(CD)):4 合并为根 (A(B(CD))):9。"},
            {"title": "分配编码", "content": "左 0 右 1：A=0, B=10, C=110, D=111。"},
            {"title": "验证", "content": "编码无前缀冲突，加权路径长 = 5·1 + 2·2 + 1·3 + 1·3 = 5+4+3+3 = 15。"}
        ],
        "answer": "A=0, B=10, C=110, D=111。",
        "summary": "Huffman 编码：每次合并频率最小的两棵树，自底向上构造；保证前缀码且加权路径最短。",
        "tags": "Huffman编码,前缀码,最优编码"
    },
    {
        "chapter": "第11章", "title": "二叉搜索树插入",
        "question": "依次插入 5, 3, 7, 2, 4, 6, 8 到空 BST。画出最终的 BST。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "插入 5", "content": "树空，5 成为根。"},
            {"title": "插入 3", "content": "3 < 5，进入左子树，左子树空，3 成为 5 的左子。"},
            {"title": "插入 7", "content": "7 > 5，进入右子树，右子树空，7 成为 5 的右子。"},
            {"title": "插入 2", "content": "2 < 5（左），2 < 3（左），左空，2 成为 3 的左子。"},
            {"title": "插入 4", "content": "4 < 5（左），4 > 3（右），右空，4 成为 3 的右子。"},
            {"title": "插入 6", "content": "6 > 5（右），6 < 7（左），左空，6 成为 7 的左子。"},
            {"title": "插入 8", "content": "8 > 5（右），8 > 7（右），右空，8 成为 7 的右子。"},
            {"title": "最终结构", "content": "5 是根；左子树：3（左 2，右 4）；右子树：7（左 6，右 8）。"}
        ],
        "answer": "BST 结构：5(根)；左子 3(左 2, 右 4)；右子 7(左 6, 右 8)。",
        "summary": "BST 插入：从根开始比较，小则入左子树，大则入右子树，递归直至空位。中序遍历得有序序列。",
        "tags": "二叉搜索树,BST,插入",
        "graph_data": _tree([5, 3, 7, 2, 4, 6, 8], levels=3)
    },
    {
        "chapter": "第11章", "title": "前序中序遍历",
        "question": "已知二叉树前序遍历 A B D E C F，中序遍历 D B E A F C，重建该二叉树。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "识别根", "content": "前序第一个为根：A。"},
            {"title": "分割中序", "content": "在中序中找 A，左侧 D B E 为左子树，右侧 F C 为右子树。"},
            {"title": "递归左子树", "content": "左子树前序 B D E，中序 D B E。根为 B。中序中 B 左侧 D 为左子，右侧 E 为右子。"},
            {"title": "递归右子树", "content": "右子树前序 C F，中序 F C。根为 C。中序中 C 左侧 F 为左子。"},
            {"title": "重建结果", "content": "A 是根；左子 B（左 D，右 E）；右子 C（左 F，右空）。"}
        ],
        "answer": "树结构：A(根) → 左 B(D, E)，右 C(F, -)。",
        "summary": "前序+中序唯一确定二叉树：前序找根，中序分左右子树，递归处理。",
        "tags": "前序遍历,中序遍历,二叉树重建"
    },
    {
        "chapter": "第11章", "title": "最小生成树 Kruskal",
        "question": "给定带权图：顶点 {A,B,C,D}，边及权：(A,B,1), (A,C,5), (B,C,2), (B,D,4), (C,D,3)。用 Kruskal 算法求最小生成树。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "按权重排序", "content": "将所有边按权升序排列：(A,B,1) < (B,C,2) < (C,D,3) < (B,D,4) < (A,C,5)。"},
            {"title": "初始化", "content": "每个顶点自成一集合：{A},{B},{C},{D}。MST 边集 T = ∅。"},
            {"title": "选 (A,B,1)", "content": "A、B 属不同集合，加入 T。合并得 {A,B},{C},{D}。"},
            {"title": "选 (B,C,2)", "content": "B 在 {A,B}，C 在 {C}，不同集合，加入 T。合并得 {A,B,C},{D}。"},
            {"title": "选 (C,D,3)", "content": "C 在 {A,B,C}，D 在 {D}，不同集合，加入 T。合并得 {A,B,C,D}。"},
            {"title": "检查后续边", "content": "(B,D,4)：B、D 同属 {A,B,C,D}，跳过（避免成环）。(A,C,5)：同理跳过。"},
            {"title": "得出结果", "content": "MST 共 3 条边：(A,B,1)、(B,C,2)、(C,D,3)，权值之和 = 1+2+3 = 6。"}
        ],
        "answer": "MST = {(A,B,1), (B,C,2), (C,D,3)}，权值和为 6。",
        "summary": "Kruskal 算法：边按权排序后从小到大选择，使用并查集判断是否成环，不成环则加入。共选 n-1 条边。",
        "tags": "最小生成树,Kruskal,并查集",
        "graph_data": _graph(
            [("A", 150, 80), ("B", 350, 80), ("C", 350, 260), ("D", 150, 260)],
            [(1, 2, 1), (1, 3, 5), (2, 3, 2), (2, 4, 4), (3, 4, 3)]
        )
    },
    {
        "chapter": "第11章", "title": "Huffman 树构造",
        "question": "给定字符频率 f(a)=5, f(b)=9, f(c)=12, f(d)=13, f(e)=16, f(f)=45。构造 Huffman 树并求编码总长。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "初始化森林", "content": "将每个字符作为单独的树，按频率升序排列：a(5), b(9), c(12), d(13), e(16), f(45)。"},
            {"title": "第一次合并", "content": "取最小的 a(5) 和 b(9) 合并为新节点 N1(14)。森林变为：c(12), d(13), N1(14), e(16), f(45)。"},
            {"title": "第二次合并", "content": "取 c(12) 和 d(13) 合并为 N2(25)。森林：N1(14), e(16), N2(25), f(45)。"},
            {"title": "第三次合并", "content": "取 N1(14) 和 e(16) 合并为 N3(30)。森林：N2(25), N3(30), f(45)。"},
            {"title": "第四次合并", "content": "取 N2(25) 和 N3(30) 合并为 N4(55)。森林：f(45), N4(55)。"},
            {"title": "根合并", "content": "取 f(45) 和 N4(55) 合并为根 R(100)。Huffman 树构造完成。"},
            {"title": "求编码总长", "content": "带权路径长度 WPL = 45·1 + 16·3 + 12·3 + 13·3 + 5·4 + 9·4 = 45 + 48 + 36 + 39 + 20 + 36 = 224。"}
        ],
        "answer": "WPL = 224，即编码总长度为 224。",
        "summary": "Huffman 树：每次取权值最小的两棵树合并，重复直至只剩一棵树。WPL = Σ（叶权 × 路径长），是最优前缀码。",
        "tags": "Huffman树,最优二叉树,前缀码"
    },

    # ===================== 第12章 布尔代数（8道） =====================
    {
        "chapter": "第12章", "title": "布尔表达式求值",
        "question": "在布尔代数中求 (1 · 0) + (1 + 0)·(0 + 1) 的值。",
        "question_type": "calc", "difficulty": "easy",
        "steps": [
            {"title": "明确运算", "content": "布尔代数中 + 表示或（最大元为 1），· 表示与（最小元为 0）。1·0 = 0，1+0 = 1。"},
            {"title": "计算括号", "content": "第一项 1·0 = 0；第二项中 (1+0) = 1，(0+1) = 1。"},
            {"title": "计算乘积", "content": "第二项 (1+0)·(0+1) = 1·1 = 1。"},
            {"title": "求和", "content": "原式 = 0 + 1 = 1。"}
        ],
        "answer": "1",
        "summary": "布尔代数运算优先级：先 · 后 +；· 满足交换、结合、分配律；0 是 · 单位元，1 是 + 单位元。",
        "tags": "布尔代数,求值,运算"
    },
    {
        "chapter": "第12章", "title": "布尔代数德摩根律",
        "question": "化简布尔表达式 ¬(x · y + ¬x · z)。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "外层否定", "content": "应用德摩根律 ¬(A + B) = ¬A · ¬B，得：¬(x · y) · ¬(¬x · z)。"},
            {"title": "继续德摩根律", "content": "对每个因子再应用 ¬(A · B) = ¬A + ¬B：得 (¬x + ¬y) · (x + ¬z)。"},
            {"title": "展开乘积", "content": "应用分配律展开 (¬x + ¬y)·(x + ¬z) = ¬x·x + ¬x·¬z + ¬y·x + ¬y·¬z。"},
            {"title": "化简互补项", "content": "¬x·x = 0（互补律），故原式 = ¬x·¬z + x·¬y + ¬y·¬z。"},
            {"title": "冗余项吸收", "content": "¬y·¬z 可被两项覆盖，但保留最简形式为：¬x·¬z + x·¬y（一致性定理）。"}
        ],
        "answer": "¬x·¬z + x·¬y（最简形式）。",
        "summary": "布尔代数德摩根律：¬(A+B)=¬A·¬B，¬(A·B)=¬A+¬B。配合互补律、分配律、一致性定理可化简表达式。",
        "tags": "布尔代数,德摩根律,化简"
    },
    {
        "chapter": "第12章", "title": "逻辑电路真值表",
        "question": "化简逻辑函数 F(A,B,C) = Σm(1, 3, 5, 7) 并用基本门实现。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "列真值表", "content": "m1=001, m3=011, m5=101, m7=111。观察可知这 4 个最小项的公共特征是 C=1。"},
            {"title": "卡诺图化简", "content": "在 3 变量卡诺图中，m1、m3、m5、m7 形成 2×2 的相邻块（C=1 的整列）。"},
            {"title": "写出最简式", "content": "F = C。A、B 都是冗余变量，可被吸收。"},
            {"title": "验证", "content": "C=1 时，无论 A、B 取何值，对应最小项均包含在内（m1,m3,m5,m7），故 F=C 正确。"}
        ],
        "answer": "F = C（最简形式）。",
        "summary": "卡诺图化简：相邻最小项可合并消去变量。本题中所有 1 值最小项共享 C=1，故函数直接等于 C。",
        "tags": "卡诺图,逻辑函数,化简"
    },
    {
        "chapter": "第12章", "title": "布尔表达式对偶式",
        "question": "求布尔表达式 F = x + y·(z + x·¬y) 的对偶式 Fᴅ。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "对偶规则", "content": "对偶式：将 + 与 · 互换，0 与 1 互换，但变量和补运算不变，保持运算顺序。"},
            {"title": "应用对偶", "content": "原式 F = x + y·(z + x·¬y)。+ ↔ ·：得 Fᴅ = x · (y + (z · x·¬y))。注意括号保持不变。"},
            {"title": "验证运算顺序", "content": "原式中 y·(z+x·¬y) 先算 z+x·¬y（先 · 后 +），对偶后相应位置 y+(z·x·¬y) 也是先 · 后 +。"},
            {"title": "结论", "content": "Fᴅ = x · (y + z·x·¬y)。"}
        ],
        "answer": "Fᴅ = x · (y + z · x · ¬y)。",
        "summary": "对偶原则：互换 + 与 ·、0 与 1，变量和补不变，括号保持。若 F=G 则 Fᴅ=Gᴅ，是布尔代数基本定理。",
        "tags": "对偶式,布尔代数,定理"
    },
    {
        "chapter": "第12章", "title": "吸收律应用",
        "question": "化简布尔表达式 F = A·B + A·B·C + A·B·D + A·B·(C+D)。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "提取公因子", "content": "每项都含 A·B，提取得：F = A·B·(1 + C + D + (C+D))。"},
            {"title": "应用同一律", "content": "1 + 任何 = 1，故 F = A·B·1 = A·B。"},
            {"title": "验证吸收律", "content": "也可逐项应用吸收律 A·B + A·B·X = A·B：A·B·C 被 A·B 吸收，A·B·D 被吸收，A·B·(C+D) 也被吸收。"},
            {"title": "结论", "content": "F = A·B。"}
        ],
        "answer": "F = A·B。",
        "summary": "吸收律：A + A·B = A，A·(A+B) = A。任何项若含另一项的全部因子，则可被吸收。",
        "tags": "吸收律,化简,布尔代数"
    },
    {
        "chapter": "第12章", "title": "卡诺图化简四变量",
        "question": "用卡诺图化简 F(A,B,C,D) = Σm(0, 2, 5, 7, 8, 10, 13, 15)。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "画卡诺图", "content": "4 变量卡诺图 4×4，行 AB（00,01,11,10），列 CD（00,01,11,10）。"},
            {"title": "填入最小项", "content": "m0(0000)在(00,00)；m2(0010)在(00,10)；m5(0101)在(01,01)；m7(0111)在(01,11)；m8(1000)在(10,00)；m10(1010)在(10,10)；m13(1101)在(11,01)；m15(1111)在(11,11)。"},
            {"title": "分组", "content": "第一组：m0,m2,m8,m10 形成四角块（B=0, D=0，即 ¬B·¬D）。第二组：m5,m7,m13,m15 形成 2×2 块（B=1, D=1，即 B·D）。"},
            {"title": "写出最简式", "content": "F = ¬B·¬D + B·D。"}
        ],
        "answer": "F = ¬B·¬D + B·D（即 B 与 D 同或）。",
        "summary": "4 变量卡诺图分组规则：相邻 2^k 个最小项可合并，消去 k 个变量。注意卡诺图可循环相邻（首尾相接）。",
        "tags": "卡诺图,四变量,化简"
    },
    {
        "chapter": "第12章", "title": "逻辑门电路转换",
        "question": "将表达式 F = (A+B)·(C+D) 转换为只用与非门（NAND）实现的形式。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "理解与非门完备性", "content": "与非门 {↑} 是功能完备集，可表达任意布尔函数。需要把 + 和 · 都转换为 ↑。"},
            {"title": "转 ¬A", "content": "¬A = A ↑ A。"},
            {"title": "转 A·B", "content": "A·B = ¬(A ↑ B) = (A ↑ B) ↑ (A ↑ B)。"},
            {"title": "转 A+B", "content": "A+B = ¬A ↑ ¬B = (A↑A) ↑ (B↑B)（德摩根律）。"},
            {"title": "代入原式", "content": "F = (A+B)·(C+D)。令 X = A+B = (A↑A)↑(B↑B)，Y = C+D = (C↑C)↑(D↑D)。"},
            {"title": "组合", "content": "F = X·Y = (X↑Y) ↑ (X↑Y)。即两次 NAND 实现 AND。"}
        ],
        "answer": "F = (X↑Y)↑(X↑Y)，其中 X=(A↑A)↑(B↑B)，Y=(C↑C)↑(D↑D)。",
        "summary": "与非门完备集：¬A=A↑A；A·B=(A↑B)↑(A↑B)；A+B=(A↑A)↑(B↑B)。任何布尔函数都可用纯 NAND 实现。",
        "tags": "与非门,完备集,逻辑电路"
    },
    {
        "chapter": "第12章", "title": "布尔代数公理验证",
        "question": "验证布尔代数中 (x + y)·(x + ¬y) = x。",
        "question_type": "proof", "difficulty": "medium",
        "steps": [
            {"title": "应用分配律", "content": "(x + y)·(x + ¬y) = x + (y · ¬y)（分配律 A+B 与 A+C 的乘积等于 A+(B·C)）。"},
            {"title": "应用互补律", "content": "y · ¬y = 0（互补律：变量与补的乘积为 0）。"},
            {"title": "应用同一律", "content": "x + 0 = x（同一律：与 0 求和等于自身）。"},
            {"title": "结论", "content": "故 (x + y)·(x + ¬y) = x。"}
        ],
        "answer": "(x + y)·(x + ¬y) = x。",
        "summary": "布尔代数基本公理：分配律、互补律（x·¬x=0, x+¬x=1）、同一律（x+0=x, x·1=x）。常用于化简共识项。",
        "tags": "布尔代数,公理,分配律"
    },

    # ===================== 第13章 图论算法（8道） =====================
    {
        "chapter": "第13章", "title": "Dijkstra 最短路径",
        "question": "给定有向带权图：顶点 {A,B,C,D,E}，边权：A→B=10, A→C=3, B→D=2, C→B=4, C→D=8, D→E=5, C→E=12。用 Dijkstra 算法求 A 到 E 的最短路径。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "初始化", "content": "dist[A]=0, dist[其他]=∞。已确定集合 S = ∅。所有边权非负，可使用 Dijkstra。"},
            {"title": "选 A", "content": "选最小 dist 的 A 加入 S。更新邻接：dist[B]=10, dist[C]=3。"},
            {"title": "选 C", "content": "dist[C]=3 最小，加入 S。更新：dist[B] = min(10, 3+4) = 7；dist[D] = 3+8 = 11；dist[E] = 3+12 = 15。"},
            {"title": "选 B", "content": "dist[B]=7 最小，加入 S。更新：dist[D] = min(11, 7+2) = 9。"},
            {"title": "选 D", "content": "dist[D]=9 最小，加入 S。更新：dist[E] = min(15, 9+5) = 14。"},
            {"title": "选 E", "content": "dist[E]=14 最小，加入 S。算法结束。"},
            {"title": "回溯路径", "content": "E←D←B←C←A，即 A→C→B→D→E，长度 3+4+2+5=14。"}
        ],
        "answer": "A 到 E 的最短路径为 A→C→B→D→E，长度为 14。",
        "summary": "Dijkstra 算法：贪心策略，每次选未确定中 dist 最小的顶点加入 S，松弛其邻接边。仅适用于非负权图。",
        "tags": "Dijkstra,最短路径,贪心",
        "graph_data": _graph(
            [("A", 80, 200), ("B", 260, 80), ("C", 260, 320), ("D", 440, 80), ("E", 620, 200)],
            [(1, 2, 10), (1, 3, 3), (2, 4, 2), (3, 2, 4), (3, 4, 8), (4, 5, 5), (3, 5, 12)],
            directed=True
        )
    },
    {
        "chapter": "第13章", "title": "BFS 广度优先遍历",
        "question": "对无向图 G，顶点 {A,B,C,D,E,F}，边 {A-B, A-C, B-D, C-D, C-E, D-F, E-F}，从 A 开始进行 BFS 遍历，写出访问顺序。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "初始化", "content": "访问 A，入队 Q = [A]。访问集 visited = {A}。"},
            {"title": "处理 A", "content": "出队 A，访问其未访问邻接 B、C，按字母序入队：Q = [B, C]，visited = {A,B,C}。"},
            {"title": "处理 B", "content": "出队 B，邻接 D 未访问，入队：Q = [C, D]，visited = {A,B,C,D}。"},
            {"title": "处理 C", "content": "出队 C，邻接 D 已访问、E 未访问，入队：Q = [D, E]，visited = {A,B,C,D,E}。"},
            {"title": "处理 D", "content": "出队 D，邻接 F 未访问，入队：Q = [E, F]，visited = {A,B,C,D,E,F}。"},
            {"title": "处理 E、F", "content": "出队 E、F，邻接均已访问，队空结束。"},
            {"title": "访问顺序", "content": "BFS 访问顺序：A → B → C → D → E → F。"}
        ],
        "answer": "A → B → C → D → E → F。",
        "summary": "BFS 用队列实现，按层访问。从源点开始，先访问所有距离为 1 的顶点，再访问距离为 2 的，依此类推。可求无权图最短路径。",
        "tags": "BFS,广度优先,遍历",
        "graph_data": _graph(
            [("A", 100, 200), ("B", 260, 100), ("C", 260, 300), ("D", 420, 200), ("E", 420, 360), ("F", 580, 280)],
            [(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 4, 1), (3, 5, 1), (4, 6, 1), (5, 6, 1)]
        )
    },
    {
        "chapter": "第13章", "title": "DFS 深度优先遍历",
        "question": "对无向图 G，顶点 {A,B,C,D,E}，边 {A-B, A-C, B-D, C-D, D-E}，从 A 开始进行 DFS 遍历，写出访问顺序。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "初始化", "content": "访问 A，visited = {A}，栈/递归从 A 出发。"},
            {"title": "访问邻接 B", "content": "A 的未访问邻接按字母序取 B，访问 B，visited = {A,B}。"},
            {"title": "从 B 继续", "content": "B 的未访问邻接 D，访问 D，visited = {A,B,D}。"},
            {"title": "从 D 继续", "content": "D 的未访问邻接 E，访问 E，visited = {A,B,D,E}。"},
            {"title": "从 E 回溯", "content": "E 无未访问邻接，回溯到 D，D 已无未访问邻接，回溯到 B，回溯到 A。"},
            {"title": "从 A 继续", "content": "A 还有未访问邻接 C，访问 C，visited = {A,B,D,E,C}。C 的邻接 D 已访问，回溯结束。"},
            {"title": "访问顺序", "content": "DFS 访问顺序：A → B → D → E → C。"}
        ],
        "answer": "A → B → D → E → C。",
        "summary": "DFS 用栈或递归实现，沿一条路径深入到底再回溯。常用于连通分量、环检测、拓扑排序等。",
        "tags": "DFS,深度优先,遍历",
        "graph_data": _graph(
            [("A", 100, 200), ("B", 260, 100), ("C", 260, 300), ("D", 420, 200), ("E", 580, 200)],
            [(1, 2, 1), (1, 3, 1), (2, 4, 1), (3, 4, 1), (4, 5, 1)]
        )
    },
    {
        "chapter": "第13章", "title": "Floyd-Warshall 全源最短路径",
        "question": "给定有向图顶点 {1,2,3}，边权矩阵 W（∞ 表示无直接边）：W[1,2]=4, W[1,3]=11, W[2,3]=2, W[3,1]=3, W[2,1]=∞, W[3,2]=∞。用 Floyd 算法求所有顶点对的最短路径。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "初始化距离矩阵", "content": "D⁰ = [[0,4,11],[∞,0,2],[3,∞,0]]，对角线为 0。"},
            {"title": "k=1（经过顶点 1）", "content": "检查所有 (i,j)：若 D[i,1]+D[1,j] < D[i,j] 则更新。D[2,3] 已是 2，无需改；D[3,2] = min(∞, D[3,1]+D[1,2]) = min(∞, 3+4)=7。"},
            {"title": "k=2（经过顶点 2）", "content": "D[1,3] = min(11, D[1,2]+D[2,3]) = min(11, 4+2)=6。其他项无改进。"},
            {"title": "k=3（经过顶点 3）", "content": "D[1,2] = min(4, D[1,3]+D[3,2]) = min(4, 6+7)=4 不变。D[2,1] = min(∞, D[2,3]+D[3,1]) = min(∞, 2+3)=5。"},
            {"title": "结果矩阵", "content": "D = [[0,4,6],[5,0,2],[3,7,0]]。"}
        ],
        "answer": "最短距离矩阵 D = [[0,4,6],[5,0,2],[3,7,0]]。",
        "summary": "Floyd-Warshall：动态规划，依次允许经过顶点 1..k，更新 D[i,j] = min(D[i,j], D[i,k]+D[k,j])。时间复杂度 O(n³)。",
        "tags": "Floyd,全源最短路径,动态规划"
    },
    {
        "chapter": "第13章", "title": "拓扑排序",
        "question": "给定有向无环图（DAG）顶点 {A,B,C,D,E,F}，边：A→C, B→C, B→D, C→E, D→E, E→F。用 Kahn 算法（入度法）求一个拓扑排序。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "计算入度", "content": "入度：A=0, B=0, C=2, D=1, E=2, F=1。"},
            {"title": "初始入队", "content": "入度为 0 的顶点入队：Q = [A, B]（按字母序）。"},
            {"title": "处理 A", "content": "出队 A，输出序列：A。A→C：C 的入度减 1 得 1。"},
            {"title": "处理 B", "content": "出队 B，输出序列：A, B。B→C：C 的入度减 1 得 0，入队；B→D：D 的入度减 1 得 0，入队。Q = [C, D]。"},
            {"title": "处理 C、D", "content": "出队 C，输出：A,B,C。C→E：E 入度减 1 得 1。出队 D，输出：A,B,C,D。D→E：E 入度减 1 得 0，入队。Q = [E]。"},
            {"title": "处理 E、F", "content": "出队 E，输出：A,B,C,D,E。E→F：F 入度减 1 得 0，入队。出队 F，输出：A,B,C,D,E,F。"},
            {"title": "结果", "content": "拓扑排序：A, B, C, D, E, F。"}
        ],
        "answer": "拓扑排序：A, B, C, D, E, F。",
        "summary": "Kahn 算法：每次取入度为 0 的顶点输出并删除其出边，重复直至无顶点。若输出顶点数少于总数则存在环。",
        "tags": "拓扑排序,Kahn算法,DAG",
        "graph_data": _graph(
            [("A", 80, 100), ("B", 80, 300), ("C", 260, 100), ("D", 260, 300), ("E", 440, 200), ("F", 620, 200)],
            [(1, 3, 1), (2, 3, 1), (2, 4, 1), (3, 5, 1), (4, 5, 1), (5, 6, 1)],
            directed=True
        )
    },
    {
        "chapter": "第13章", "title": "Warshall 传递闭包",
        "question": "给定有向图顶点 {1,2,3,4}，边：1→2, 2→3, 3→4。用 Warshall 算法求传递闭包矩阵。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "初始化邻接矩阵", "content": "M⁰[i,j]=1 当且仅当存在边 i→j。对角线为 0（无自环）。M⁰ = [[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,0,0,0]]。"},
            {"title": "k=1", "content": "允许经过顶点 1。检查所有 (i,j)：若 M[i,1]=1 且 M[1,j]=1 则 M[i,j]=1。第一行已有 1→2，无新加项。M¹ = M⁰。"},
            {"title": "k=2", "content": "允许经过顶点 2。M[1,2]=1 且 M[2,3]=1，故 M[1,3]=1。M² = [[0,1,1,0],[0,0,1,0],[0,0,0,1],[0,0,0,0]]。"},
            {"title": "k=3", "content": "允许经过顶点 3。M[1,3]=1 且 M[3,4]=1，故 M[1,4]=1。M[2,3]=1 且 M[3,4]=1，故 M[2,4]=1。M³ = [[0,1,1,1],[0,0,1,1],[0,0,0,1],[0,0,0,0]]。"},
            {"title": "k=4", "content": "顶点 4 无出边，无更新。最终传递闭包 = M³。"}
        ],
        "answer": "传递闭包矩阵 = [[0,1,1,1],[0,0,1,1],[0,0,0,1],[0,0,0,0]]。",
        "summary": "Warshall 算法：M[i,j] = M[i,j] ∨ (M[i,k] ∧ M[k,j])，依次允许经过 k=1..n。是 Floyd 的布尔版本。",
        "tags": "Warshall,传递闭包,可达性"
    },
    {
        "chapter": "第13章", "title": "最大流 Ford-Fulkerson",
        "question": "给定网络：源点 s，汇点 t，中间顶点 {A,B}。边及容量：s→A=10, s→B=5, A→B=4, A→t=8, B→t=10。用 Ford-Fulkerson 算法求最大流。",
        "question_type": "calc", "difficulty": "hard",
        "steps": [
            {"title": "初始化", "content": "所有边的流量为 0，剩余图 = 原图。最大流 f = 0。"},
            {"title": "找增广路径 1", "content": "找路径 s→A→t，瓶颈容量 min(10, 8) = 8。增流 8，f = 8。剩余：s→A=2, A→t=0（满）。"},
            {"title": "找增广路径 2", "content": "找路径 s→B→t，瓶颈 min(5, 10) = 5。增流 5，f = 13。剩余：s→B=0, B→t=5。"},
            {"title": "找增广路径 3", "content": "找路径 s→A→B→t，瓶颈 min(2, 4, 5) = 2。增流 2，f = 15。剩余：s→A=0, A→B=2, B→t=3。"},
            {"title": "无新路径", "content": "s 的出边已饱和（s→A=0, s→B=0），无更多增广路径。"},
            {"title": "验证最小割", "content": "最小割为 ({s,A,B}, {t})，割边为 A→t(8) 和 B→t(10)，容量 8+10=18。但实际流 f=15，说明割应是 ({s}, {A,B,t})：s→A+s→B = 10+5 = 15。"},
            {"title": "结论", "content": "最大流 = 15，等于最小割容量，验证正确。"}
        ],
        "answer": "最大流为 15（最小割也为 15，验证 max-flow min-cut 定理）。",
        "summary": "Ford-Fulkerson：反复找增广路径增流直至无路径。最大流 = 最小割容量（最大流最小割定理）。",
        "tags": "最大流,Ford-Fulkerson,最小割",
        "graph_data": _graph(
            [("s", 80, 200), ("A", 280, 100), ("B", 280, 300), ("t", 480, 200)],
            [(1, 2, 10), (1, 3, 5), (2, 3, 4), (2, 4, 8), (3, 4, 10)],
            directed=True
        )
    },
    {
        "chapter": "第13章", "title": "Prim 最小生成树",
        "question": "给定带权图：顶点 {A,B,C,D}，边及权：(A,B,1), (A,C,5), (B,C,2), (B,D,4), (C,D,3)。用 Prim 算法从 A 出发求最小生成树。",
        "question_type": "calc", "difficulty": "medium",
        "steps": [
            {"title": "初始化", "content": "从 A 出发，S = {A}。候选边集（与 S 相连的最小权边）：A-B(1), A-C(5)。"},
            {"title": "选最小权边", "content": "最小权边 A-B(1)，将 B 加入 S = {A,B}。更新候选边集：A-C(5), B-C(2), B-D(4)。"},
            {"title": "继续选最小", "content": "最小权边 B-C(2)，将 C 加入 S = {A,B,C}。更新候选边集：C-D(3)（B-D(4) 被 C-D(3) 替代）。"},
            {"title": "最后选边", "content": "最小权边 C-D(3)，将 D 加入 S = {A,B,C,D}。共 3 条边，算法结束。"},
            {"title": "结果", "content": "MST = {(A,B,1), (B,C,2), (C,D,3)}，权值和 = 6。与 Kruskal 结果一致。"}
        ],
        "answer": "MST = {(A,B,1), (B,C,2), (C,D,3)}，权值和为 6。",
        "summary": "Prim 算法：从任一顶点出发，每次将与当前生成树相连的最小权边加入。时间复杂度 O(V²)（邻接矩阵）或 O(E log V)（堆优化）。",
        "tags": "最小生成树,Prim,贪心",
        "graph_data": _graph(
            [("A", 150, 80), ("B", 350, 80), ("C", 350, 260), ("D", 150, 260)],
            [(1, 2, 1), (1, 3, 5), (2, 3, 2), (2, 4, 4), (3, 4, 3)]
        )
    }
]


def import_example_data():
    """将内置例题导入数据库。

    使用方式：在 Flask shell 中调用
        from app.utils.example_data import import_example_data
        import_example_data()
    或在应用启动时调用（参见 app/__init__.py 的迁移流程）。
    """
    from app import db
    from app.models import Example

    # 清空旧数据
    db.session.query(Example).delete()
    db.session.commit()

    # 写入新数据
    for idx, item in enumerate(EXAMPLES, start=1):
        ex = Example(
            chapter=item.get("chapter", ""),
            title=item.get("title", ""),
            question=item.get("question", ""),
            question_type=item.get("question_type", "calc"),
            difficulty=item.get("difficulty", "medium"),
            steps_json=json.dumps(item.get("steps", []), ensure_ascii=False),
            answer=item.get("answer", ""),
            summary=item.get("summary", ""),
            graph_data=item.get("graph_data"),
            tags=item.get("tags", ""),
            sort_order=idx,
            created_at=datetime.utcnow()
        )
        db.session.add(ex)

    db.session.commit()
    return len(EXAMPLES)


import_examples = import_example_data
