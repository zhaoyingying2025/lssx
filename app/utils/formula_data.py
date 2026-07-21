# -*- coding: utf-8 -*-
"""
离散数学公式速查表数据模块。

按 Rosen《离散数学及其应用》13 章组织，预置 80+ 条核心公式，
每条含名称、公式（含 LaTeX）、文字描述、适用条件与标签。

数据结构：FORMULAS = [ { chapter, category, name, formula, description, latex, condition, tags } ]
"""

FORMULAS = [
    # ===================== 第1章 逻辑与证明 (8个) =====================
    {
        "chapter": "第1章 逻辑与证明",
        "category": "命题逻辑",
        "name": "德摩根律",
        "formula": "¬(p ∧ q) ≡ ¬p ∨ ¬q\n¬(p ∨ q) ≡ ¬p ∧ ¬q",
        "description": "否定的分配律：与的否定等于否定的或，或的否定等于否定的与",
        "latex": r"\neg(p \wedge q) \equiv \neg p \vee \neg q \\ \neg(p \vee q) \equiv \neg p \wedge \neg q",
        "condition": "适用于任意命题 p 和 q",
        "tags": "逻辑,德摩根律,等价"
    },
    {
        "chapter": "第1章 逻辑与证明",
        "category": "命题逻辑",
        "name": "分配律",
        "formula": "p ∨ (q ∧ r) ≡ (p ∨ q) ∧ (p ∨ r)\np ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)",
        "description": "析取对合取的分配，以及合取对析取的分配",
        "latex": r"p \vee (q \wedge r) \equiv (p \vee q) \wedge (p \vee r) \\ p \wedge (q \vee r) \equiv (p \wedge q) \vee (p \wedge r)",
        "condition": "适用于任意命题 p, q, r",
        "tags": "逻辑,分配律,等价"
    },
    {
        "chapter": "第1章 逻辑与证明",
        "category": "命题逻辑",
        "name": "蕴含等价",
        "formula": "p → q ≡ ¬p ∨ q\np → q ≡ ¬q → ¬p",
        "description": "蕴含可改写为析取；逆否命题与原命题等价",
        "latex": r"p \rightarrow q \equiv \neg p \vee q \\ p \rightarrow q \equiv \neg q \rightarrow \neg p",
        "condition": "适用于任意命题 p 和 q",
        "tags": "逻辑,蕴含,逆否"
    },
    {
        "chapter": "第1章 逻辑与证明",
        "category": "命题逻辑",
        "name": "双条件等价",
        "formula": "p ↔ q ≡ (p → q) ∧ (q → p)",
        "description": "双条件等价于两个方向蕴含的合取",
        "latex": r"p \leftrightarrow q \equiv (p \rightarrow q) \wedge (q \rightarrow p)",
        "condition": "适用于任意命题 p 和 q",
        "tags": "逻辑,双条件,等价"
    },
    {
        "chapter": "第1章 逻辑与证明",
        "category": "谓词逻辑",
        "name": "量词否定",
        "formula": "¬∀x P(x) ≡ ∃x ¬P(x)\n¬∃x P(x) ≡ ∀x ¬P(x)",
        "description": "全称量词的否定等价于存在量词否定，反之亦然",
        "latex": r"\neg \forall x\, P(x) \equiv \exists x\, \neg P(x) \\ \neg \exists x\, P(x) \equiv \forall x\, \neg P(x)",
        "condition": "适用于任意谓词 P(x)",
        "tags": "逻辑,量词,否定"
    },
    {
        "chapter": "第1章 逻辑与证明",
        "category": "谓词逻辑",
        "name": "量词分配",
        "formula": "∀x (P(x) ∧ Q(x)) ≡ ∀x P(x) ∧ ∀x Q(x)\n∃x (P(x) ∨ Q(x)) ≡ ∃x P(x) ∨ ∃x Q(x)",
        "description": "全称量词对合取可分配，存在量词对析取可分配",
        "latex": r"\forall x\,(P(x) \wedge Q(x)) \equiv \forall x\, P(x) \wedge \forall x\, Q(x) \\ \exists x\,(P(x) \vee Q(x)) \equiv \exists x\, P(x) \vee \exists x\, Q(x)",
        "condition": "适用于任意谓词 P(x) 和 Q(x)",
        "tags": "逻辑,量词,分配"
    },
    {
        "chapter": "第1章 逻辑与证明",
        "category": "推理规则",
        "name": "假言推理",
        "formula": "p → q, p ⊢ q",
        "description": "若 p 蕴含 q 且 p 成立，则 q 成立",
        "latex": r"p \rightarrow q,\ p \ \vdash\ q",
        "condition": "前提 p → q 与 p 同时成立",
        "tags": "逻辑,推理,假言推理"
    },
    {
        "chapter": "第1章 逻辑与证明",
        "category": "推理规则",
        "name": "析取三段论",
        "formula": "p ∨ q, ¬p ⊢ q",
        "description": "若 p 或 q 成立且 p 不成立，则 q 成立",
        "latex": r"p \vee q,\ \neg p \ \vdash\ q",
        "condition": "前提 p ∨ q 与 ¬p 同时成立",
        "tags": "逻辑,推理,析取三段论"
    },

    # ===================== 第2章 集合、函数、序列、求和 (7个) =====================
    {
        "chapter": "第2章 基本结构",
        "category": "集合运算",
        "name": "容斥原理（两集合）",
        "formula": "|A ∪ B| = |A| + |B| − |A ∩ B|",
        "description": "两集合并集的元素数等于各自元素数之和减去交集元素数",
        "latex": r"|A \cup B| = |A| + |B| - |A \cap B|",
        "condition": "有限集合 A 和 B",
        "tags": "集合,容斥,计数"
    },
    {
        "chapter": "第2章 基本结构",
        "category": "集合运算",
        "name": "容斥原理（三集合）",
        "formula": "|A ∪ B ∪ C| = |A| + |B| + |C| − |A∩B| − |A∩C| − |B∩C| + |A∩B∩C|",
        "description": "三个集合并集的元素数：单加、双减、三加",
        "latex": r"|A \cup B \cup C| = |A| + |B| + |C| - |A \cap B| - |A \cap C| - |B \cap C| + |A \cap B \cap C|",
        "condition": "有限集合 A, B, C",
        "tags": "集合,容斥,计数"
    },
    {
        "chapter": "第2章 基本结构",
        "category": "集合恒等",
        "name": "补集律",
        "formula": "A ∪ Aᶜ = U\nA ∩ Aᶜ = ∅",
        "description": "集合与其补集之并等于全集，交集为空集",
        "latex": r"A \cup A^c = U \\ A \cap A^c = \emptyset",
        "condition": "A 为全集 U 的子集",
        "tags": "集合,补集,恒等"
    },
    {
        "chapter": "第2章 基本结构",
        "category": "函数",
        "name": "函数复合",
        "formula": "(f ∘ g)(x) = f(g(x))",
        "description": "先对 x 作用 g，再对结果作用 f",
        "latex": r"(f \circ g)(x) = f(g(x))",
        "condition": "g 的值域在 f 的定义域内",
        "tags": "函数,复合,映射"
    },
    {
        "chapter": "第2章 基本结构",
        "category": "序列求和",
        "name": "等差数列求和",
        "formula": "Σ_{k=1}^{n} (a + (k-1)d) = n·a + n(n-1)d/2",
        "description": "首项 a 公差 d 的等差数列前 n 项和",
        "latex": r"\sum_{k=1}^{n} \left(a + (k-1)d\right) = na + \frac{n(n-1)d}{2}",
        "condition": "首项 a，公差 d",
        "tags": "序列,等差,求和"
    },
    {
        "chapter": "第2章 基本结构",
        "category": "序列求和",
        "name": "等比数列求和",
        "formula": "Σ_{k=0}^{n-1} ar^k = a(1 − r^n) / (1 − r),  r ≠ 1",
        "description": "首项 a 公比 r 的等比数列前 n 项和",
        "latex": r"\sum_{k=0}^{n-1} ar^k = \frac{a(1 - r^n)}{1 - r}, \quad r \neq 1",
        "condition": "公比 r ≠ 1",
        "tags": "序列,等比,求和"
    },
    {
        "chapter": "第2章 基本结构",
        "category": "基数",
        "name": "幂集基数",
        "formula": "|P(S)| = 2^|S|",
        "description": "含 n 个元素的集合的幂集有 2^n 个元素",
        "latex": r"|\mathcal{P}(S)| = 2^{|S|}",
        "condition": "S 为有限集合",
        "tags": "集合,幂集,基数"
    },

    # ===================== 第3章 算法 (5个) =====================
    {
        "chapter": "第3章 算法",
        "category": "复杂度",
        "name": "大O定义",
        "formula": "f(n) = O(g(n)) ⟺ ∃C, n₀: ∀n≥n₀, |f(n)| ≤ C|g(n)|",
        "description": "f 的增长受 g 的常数倍控制",
        "latex": r"f(n) = O(g(n)) \iff \exists\, C, n_0: \forall n \geq n_0,\ |f(n)| \leq C|g(n)|",
        "condition": "n 趋于无穷",
        "tags": "算法,复杂度,大O"
    },
    {
        "chapter": "第3章 算法",
        "category": "复杂度",
        "name": "大Ω定义",
        "formula": "f(n) = Ω(g(n)) ⟺ ∃C, n₀: ∀n≥n₀, |f(n)| ≥ C|g(n)|",
        "description": "f 的增长至少为 g 的常数倍",
        "latex": r"f(n) = \Omega(g(n)) \iff \exists\, C, n_0: \forall n \geq n_0,\ |f(n)| \geq C|g(n)|",
        "condition": "n 趋于无穷",
        "tags": "算法,复杂度,大Ω"
    },
    {
        "chapter": "第3章 算法",
        "category": "复杂度",
        "name": "大Θ定义",
        "formula": "f(n) = Θ(g(n)) ⟺ f = O(g) ∧ f = Ω(g)",
        "description": "f 与 g 同阶增长",
        "latex": r"f(n) = \Theta(g(n)) \iff f = O(g) \wedge f = \Omega(g)",
        "condition": "n 趋于无穷",
        "tags": "算法,复杂度,大Θ"
    },
    {
        "chapter": "第3章 算法",
        "category": "排序算法",
        "name": "线性查找复杂度",
        "formula": "T(n) = O(n)",
        "description": "在 n 个元素中顺序查找目标值的最坏时间复杂度",
        "latex": r"T(n) = O(n)",
        "condition": "无序数组",
        "tags": "算法,查找,复杂度"
    },
    {
        "chapter": "第3章 算法",
        "category": "排序算法",
        "name": "二分查找复杂度",
        "formula": "T(n) = O(log n)",
        "description": "在有序数组中二分查找的最坏时间复杂度",
        "latex": r"T(n) = O(\log n)",
        "condition": "数组已排序",
        "tags": "算法,二分查找,复杂度"
    },

    # ===================== 第4章 数论与密码学 (8个) =====================
    {
        "chapter": "第4章 数论与密码学",
        "category": "整除",
        "name": "带余除法",
        "formula": "a = bq + r,  0 ≤ r < b",
        "description": "任意整数 a 和正整数 b，存在唯一商 q 和余数 r",
        "latex": r"a = bq + r,\quad 0 \leq r < b",
        "condition": "b > 0",
        "tags": "数论,整除,带余除法"
    },
    {
        "chapter": "第4章 数论与密码学",
        "category": "最大公约数",
        "name": "贝祖等式",
        "formula": "∃x,y: gcd(a,b) = ax + by",
        "description": "a 与 b 的最大公约数可表示为 a, b 的整系数线性组合",
        "latex": r"\exists\, x, y: \gcd(a, b) = ax + by",
        "condition": "a, b 为整数（不全为零）",
        "tags": "数论,gcd,贝祖"
    },
    {
        "chapter": "第4章 数论与密码学",
        "category": "最大公约数",
        "name": "GCD与LCM关系",
        "formula": "gcd(a,b) · lcm(a,b) = |ab|",
        "description": "两数最大公约数与最小公倍数之积等于两数之积的绝对值",
        "latex": r"\gcd(a, b) \cdot \mathrm{lcm}(a, b) = |ab|",
        "condition": "a, b 为正整数",
        "tags": "数论,gcd,lcm"
    },
    {
        "chapter": "第4章 数论与密码学",
        "category": "模运算",
        "name": "模运算加法",
        "formula": "(a + b) mod n = ((a mod n) + (b mod n)) mod n",
        "description": "模运算对加法可分配，避免大数溢出",
        "latex": r"(a + b) \bmod n = ((a \bmod n) + (b \bmod n)) \bmod n",
        "condition": "n 为正整数",
        "tags": "数论,模运算,加法"
    },
    {
        "chapter": "第4章 数论与密码学",
        "category": "模运算",
        "name": "模运算乘法",
        "formula": "(a · b) mod n = ((a mod n) · (b mod n)) mod n",
        "description": "模运算对乘法可分配",
        "latex": r"(a \cdot b) \bmod n = ((a \bmod n) \cdot (b \bmod n)) \bmod n",
        "condition": "n 为正整数",
        "tags": "数论,模运算,乘法"
    },
    {
        "chapter": "第4章 数论与密码学",
        "category": "费马小定理",
        "name": "费马小定理",
        "formula": "若 p 为素数且 gcd(a,p)=1，则 a^(p−1) ≡ 1 (mod p)",
        "description": "素数模下与 a 互素的数的幂同余 1",
        "latex": r"a^{p-1} \equiv 1 \pmod{p}",
        "condition": "p 为素数，gcd(a, p) = 1",
        "tags": "数论,费马小定理,素数"
    },
    {
        "chapter": "第4章 数论与密码学",
        "category": "欧拉定理",
        "name": "欧拉定理",
        "formula": "若 gcd(a,n)=1，则 a^φ(n) ≡ 1 (mod n)",
        "description": "费马小定理的推广：a 的欧拉函数次幂模 n 同余 1",
        "latex": r"a^{\varphi(n)} \equiv 1 \pmod{n}",
        "condition": "gcd(a, n) = 1",
        "tags": "数论,欧拉定理,欧拉函数"
    },
    {
        "chapter": "第4章 数论与密码学",
        "category": "欧拉函数",
        "name": "欧拉函数公式",
        "formula": "若 n = p₁^a₁ · p₂^a₂ · ... · pₖ^aₖ，则\nφ(n) = n · Π_{i=1}^{k} (1 − 1/pᵢ)",
        "description": "小于 n 且与 n 互素的正整数个数",
        "latex": r"\varphi(n) = n \prod_{i=1}^{k} \left(1 - \frac{1}{p_i}\right)",
        "condition": "n 的素因子分解为 p₁^a₁ ... pₖ^aₖ",
        "tags": "数论,欧拉函数,积性"
    },

    # ===================== 第5章 归纳与递归 (5个) =====================
    {
        "chapter": "第5章 归纳与递归",
        "category": "数学归纳法",
        "name": "数学归纳法步骤",
        "formula": "P(1) ∧ (∀k: P(k) → P(k+1)) ⟹ ∀n≥1 P(n)",
        "description": "证明基例 P(1) 成立；假设 P(k) 推 P(k+1)，则对所有 n 成立",
        "latex": r"P(1) \wedge \left(\forall k: P(k) \rightarrow P(k+1)\right) \Longrightarrow \forall n \geq 1\, P(n)",
        "condition": "命题族 P(n) 定义在正整数上",
        "tags": "归纳,数学归纳法"
    },
    {
        "chapter": "第5章 归纳与递归",
        "category": "数学归纳法",
        "name": "强归纳法步骤",
        "formula": "P(1) ∧ (∀k: P(1)∧...∧P(k) → P(k+1)) ⟹ ∀n≥1 P(n)",
        "description": "强归纳：假设所有更小情形都成立推出下一项",
        "latex": r"P(1) \wedge \left(\forall k: \bigwedge_{i=1}^{k} P(i) \rightarrow P(k+1)\right) \Longrightarrow \forall n \geq 1\, P(n)",
        "condition": "适用于递推依赖多个前驱的情形",
        "tags": "归纳,强归纳法"
    },
    {
        "chapter": "第5章 归纳与递归",
        "category": "递推关系",
        "name": "斐波那契递推",
        "formula": "F(n) = F(n−1) + F(n−2), F(0)=0, F(1)=1",
        "description": "斐波那契数列：当前项等于前两项之和",
        "latex": r"F(n) = F(n-1) + F(n-2),\quad F(0)=0,\ F(1)=1",
        "condition": "n ≥ 2",
        "tags": "递推,斐波那契"
    },
    {
        "chapter": "第5章 归纳与递归",
        "category": "递推关系",
        "name": "斐波那契通项（比内公式）",
        "formula": "F(n) = (φ^n − ψ^n) / √5,  φ=(1+√5)/2, ψ=(1−√5)/2",
        "description": "斐波那契数列的闭式解",
        "latex": r"F(n) = \frac{\varphi^n - \psi^n}{\sqrt{5}},\quad \varphi = \frac{1+\sqrt{5}}{2},\ \psi = \frac{1-\sqrt{5}}{2}",
        "condition": "n ≥ 0",
        "tags": "递推,斐波那契,通项"
    },
    {
        "chapter": "第5章 归纳与递归",
        "category": "良序原理",
        "name": "良序原理",
        "formula": "任意非空正整数集有最小元",
        "description": "正整数集的每个非空子集都有最小元素",
        "latex": r"\forall S \subseteq \mathbb{N}^+,\ S \neq \emptyset \Longrightarrow \exists\, m \in S,\ \forall s \in S,\ m \leq s",
        "condition": "S 为正整数的非空子集",
        "tags": "归纳,良序原理"
    },

    # ===================== 第6章 计数 (10个) =====================
    {
        "chapter": "第6章 计数",
        "category": "乘法原理",
        "name": "乘法原理",
        "formula": "若任务1有 n₁ 种方式，任务2有 n₂ 种方式，则两任务共有 n₁·n₂ 种方式",
        "description": "独立任务的组合方式数等于各任务方式数之积",
        "latex": r"N = n_1 \times n_2 \times \cdots \times n_k",
        "condition": "任务相互独立",
        "tags": "计数,乘法原理"
    },
    {
        "chapter": "第6章 计数",
        "category": "加法原理",
        "name": "加法原理",
        "formula": "若任务1有 n₁ 种方式，任务2有 n₂ 种方式，且互斥，则共 n₁+n₂ 种方式",
        "description": "互斥任务的组合方式数等于各任务方式数之和",
        "latex": r"N = n_1 + n_2 + \cdots + n_k",
        "condition": "任务两两互斥",
        "tags": "计数,加法原理"
    },
    {
        "chapter": "第6章 计数",
        "category": "排列",
        "name": "排列数",
        "formula": "P(n,r) = n! / (n−r)!",
        "description": "从 n 个不同元素中选 r 个排成一列的方式数",
        "latex": r"P(n, r) = \frac{n!}{(n-r)!}",
        "condition": "0 ≤ r ≤ n",
        "tags": "计数,排列"
    },
    {
        "chapter": "第6章 计数",
        "category": "组合",
        "name": "组合数",
        "formula": "C(n,r) = n! / (r!(n−r)!)",
        "description": "从 n 个不同元素中选 r 个的方式数（不考虑顺序）",
        "latex": r"C(n, r) = \binom{n}{r} = \frac{n!}{r!(n-r)!}",
        "condition": "0 ≤ r ≤ n",
        "tags": "计数,组合,二项式"
    },
    {
        "chapter": "第6章 计数",
        "category": "组合",
        "name": "组合数对称性",
        "formula": "C(n,r) = C(n, n−r)",
        "description": "从 n 中选 r 个与从 n 中选 n−r 个的方式数相等",
        "latex": r"\binom{n}{r} = \binom{n}{n-r}",
        "condition": "0 ≤ r ≤ n",
        "tags": "计数,组合,对称"
    },
    {
        "chapter": "第6章 计数",
        "category": "鸽巢原理",
        "name": "鸽巢原理",
        "formula": "若将 n+1 个物体放入 n 个盒子，则至少有一个盒子含 ≥ 2 个物体",
        "description": "物体数多于盒子数时必有冲突",
        "latex": r"n+1 \text{ objects into } n \text{ boxes} \Rightarrow \exists\, \text{box with } \geq 2 \text{ objects}",
        "condition": "物体数 > 盒子数",
        "tags": "计数,鸽巢原理"
    },
    {
        "chapter": "第6章 计数",
        "category": "鸽巢原理",
        "name": "广义鸽巢原理",
        "formula": "将 N 个物体放入 k 个盒子，则至少有一个盒子含 ⌈N/k⌉ 个物体",
        "description": "鸽巢原理的推广形式",
        "latex": r"\lceil N/k \rceil \text{ objects in some box}",
        "condition": "N 个物体，k 个盒子",
        "tags": "计数,鸽巢原理"
    },
    {
        "chapter": "第6章 计数",
        "category": "二项式定理",
        "name": "二项式定理",
        "formula": "(x + y)^n = Σ_{k=0}^{n} C(n,k) · x^(n−k) · y^k",
        "description": "二项式展开的系数即组合数",
        "latex": r"(x + y)^n = \sum_{k=0}^{n} \binom{n}{k} x^{n-k} y^{k}",
        "condition": "n 为非负整数",
        "tags": "计数,二项式定理"
    },
    {
        "chapter": "第6章 计数",
        "category": "二项式定理",
        "name": "帕斯卡恒等式",
        "formula": "C(n+1, k) = C(n, k−1) + C(n, k)",
        "description": "组合数的递推关系，构成帕斯卡三角",
        "latex": r"\binom{n+1}{k} = \binom{n}{k-1} + \binom{n}{k}",
        "condition": "1 ≤ k ≤ n",
        "tags": "计数,组合,帕斯卡"
    },
    {
        "chapter": "第6章 计数",
        "category": "多项式系数",
        "name": "多项式定理",
        "formula": "(x₁ + ... + x_t)^n = Σ C(n; n₁,...,n_t) · x₁^n₁ · ... · x_t^n_t",
        "description": "二项式定理的多元推广",
        "latex": r"(x_1 + \cdots + x_t)^n = \sum \binom{n}{n_1, \ldots, n_t} x_1^{n_1} \cdots x_t^{n_t}",
        "condition": "n₁ + ... + n_t = n",
        "tags": "计数,多项式定理"
    },

    # ===================== 第7章 离散概率 (8个) =====================
    {
        "chapter": "第7章 离散概率",
        "category": "概率基础",
        "name": "概率公理",
        "formula": "0 ≤ P(E) ≤ 1, P(S) = 1, P(∪ Eᵢ) = Σ P(Eᵢ)（互斥）",
        "description": "概率的三大公理：非负、规范、可列可加",
        "latex": r"0 \leq P(E) \leq 1,\ P(S) = 1,\ P\left(\bigcup E_i\right) = \sum P(E_i)\ \text{(互斥)}",
        "condition": "Eᵢ 两两互斥",
        "tags": "概率,公理"
    },
    {
        "chapter": "第7章 离散概率",
        "category": "概率基础",
        "name": "拉普拉斯概率",
        "formula": "P(E) = |E| / |S|",
        "description": "等可能样本空间中事件概率等于有利情形数除以总情形数",
        "latex": r"P(E) = \frac{|E|}{|S|}",
        "condition": "样本空间等可能",
        "tags": "概率,古典概型"
    },
    {
        "chapter": "第7章 离散概率",
        "category": "条件概率",
        "name": "条件概率",
        "formula": "P(E|F) = P(E ∩ F) / P(F),  P(F) > 0",
        "description": "在 F 发生条件下 E 发生的概率",
        "latex": r"P(E \mid F) = \frac{P(E \cap F)}{P(F)},\quad P(F) > 0",
        "condition": "P(F) > 0",
        "tags": "概率,条件概率"
    },
    {
        "chapter": "第7章 离散概率",
        "category": "独立性",
        "name": "事件独立",
        "formula": "P(E ∩ F) = P(E) · P(F)",
        "description": "两事件独立当且仅当其交的概率等于概率之积",
        "latex": r"P(E \cap F) = P(E) \cdot P(F)",
        "condition": "E 与 F 独立",
        "tags": "概率,独立"
    },
    {
        "chapter": "第7章 离散概率",
        "category": "贝叶斯定理",
        "name": "贝叶斯定理",
        "formula": "P(F|E) = P(E|F) · P(F) / P(E)",
        "description": "由条件概率与边缘概率反推后验概率",
        "latex": r"P(F \mid E) = \frac{P(E \mid F) \cdot P(F)}{P(E)}",
        "condition": "P(E) > 0",
        "tags": "概率,贝叶斯"
    },
    {
        "chapter": "第7章 离散概率",
        "category": "期望",
        "name": "数学期望",
        "formula": "E(X) = Σ x · P(X = x)",
        "description": "随机变量取值按概率加权和",
        "latex": r"E(X) = \sum_x x \cdot P(X = x)",
        "condition": "级数绝对收敛",
        "tags": "概率,期望"
    },
    {
        "chapter": "第7章 离散概率",
        "category": "期望",
        "name": "期望线性性",
        "formula": "E(aX + bY) = a·E(X) + b·E(Y)",
        "description": "期望对线性组合可分配，无需独立",
        "latex": r"E(aX + bY) = a \cdot E(X) + b \cdot E(Y)",
        "condition": "a, b 为常数",
        "tags": "概率,期望,线性"
    },
    {
        "chapter": "第7章 离散概率",
        "category": "方差",
        "name": "方差公式",
        "formula": "Var(X) = E((X − E(X))²) = E(X²) − (E(X))²",
        "description": "随机变量与均值差的平方期望",
        "latex": r"\mathrm{Var}(X) = E\left((X - E(X))^2\right) = E(X^2) - (E(X))^2",
        "condition": "X 的二阶矩存在",
        "tags": "概率,方差"
    },

    # ===================== 第8章 高级计数技术 (7个) =====================
    {
        "chapter": "第8章 高级计数",
        "category": "递推关系",
        "name": "线性齐次递推",
        "formula": "aₙ = c₁·aₙ₋₁ + c₂·aₙ₋₂ + ... + cₖ·aₙ₋ₖ",
        "description": "常系数线性齐次递推关系，可由特征方程求解",
        "latex": r"a_n = c_1 a_{n-1} + c_2 a_{n-2} + \cdots + c_k a_{n-k}",
        "condition": "系数 cᵢ 为常数",
        "tags": "递推,线性齐次"
    },
    {
        "chapter": "第8章 高级计数",
        "category": "递推关系",
        "name": "特征方程",
        "formula": "r^k = c₁·r^(k−1) + c₂·r^(k−2) + ... + cₖ",
        "description": "解线性齐次递推的特征方程，根决定通项形式",
        "latex": r"r^k = c_1 r^{k-1} + c_2 r^{k-2} + \cdots + c_k",
        "condition": "对应 k 阶齐次递推",
        "tags": "递推,特征方程"
    },
    {
        "chapter": "第8章 高级计数",
        "category": "递推关系",
        "name": "单根通项",
        "formula": "aₙ = α₁·r₁ⁿ + α₂·r₂ⁿ + ... + αₖ·rₖⁿ（单根情形）",
        "description": "特征方程有相异根时通项为各根幂的线性组合",
        "latex": r"a_n = \alpha_1 r_1^n + \alpha_2 r_2^n + \cdots + \alpha_k r_k^n",
        "condition": "特征根两两相异",
        "tags": "递推,通项,单根"
    },
    {
        "chapter": "第8章 高级计数",
        "category": "递推关系",
        "name": "重根通项",
        "formula": "若 r 为 m 重根，对应项为 (α₀ + α₁n + ... + αₘ₋₁n^(m−1)) · rⁿ",
        "description": "重根时通项中含 n 的多项式因子",
        "latex": r"a_n = (\alpha_0 + \alpha_1 n + \cdots + \alpha_{m-1} n^{m-1}) r^n",
        "condition": "r 为 m 重特征根",
        "tags": "递推,通项,重根"
    },
    {
        "chapter": "第8章 高级计数",
        "category": "生成函数",
        "name": "生成函数定义",
        "formula": "G(x) = Σ_{n=0}^{∞} aₙ · xⁿ",
        "description": "数列 {aₙ} 的普通生成函数",
        "latex": r"G(x) = \sum_{n=0}^{\infty} a_n x^n",
        "condition": "级数收敛域内成立",
        "tags": "生成函数,普通"
    },
    {
        "chapter": "第8章 高级计数",
        "category": "生成函数",
        "name": "几何级数生成函数",
        "formula": "1 / (1 − x) = Σ_{n=0}^{∞} xⁿ,  |x| < 1",
        "description": "几何级数的生成函数",
        "latex": r"\frac{1}{1-x} = \sum_{n=0}^{\infty} x^n,\quad |x| < 1",
        "condition": "|x| < 1",
        "tags": "生成函数,几何级数"
    },
    {
        "chapter": "第8章 高级计数",
        "category": "生成函数",
        "name": "二项式生成函数",
        "formula": "(1 + x)^n = Σ_{k=0}^{n} C(n,k) · xᵏ",
        "description": "二项式展开作为生成函数",
        "latex": r"(1 + x)^n = \sum_{k=0}^{n} \binom{n}{k} x^k",
        "condition": "n 为非负整数",
        "tags": "生成函数,二项式"
    },

    # ===================== 第9章 关系 (6个) =====================
    {
        "chapter": "第9章 关系",
        "category": "关系性质",
        "name": "自反性",
        "formula": "∀a ∈ A: (a, a) ∈ R",
        "description": "A 中每个元素都与自身有关系 R",
        "latex": r"\forall a \in A: (a, a) \in R",
        "condition": "R 为 A 上二元关系",
        "tags": "关系,自反"
    },
    {
        "chapter": "第9章 关系",
        "category": "关系性质",
        "name": "对称性",
        "formula": "(a, b) ∈ R ⟹ (b, a) ∈ R",
        "description": "若 a 与 b 有关系则 b 与 a 也有关系",
        "latex": r"(a, b) \in R \Longrightarrow (b, a) \in R",
        "condition": "R 为 A 上二元关系",
        "tags": "关系,对称"
    },
    {
        "chapter": "第9章 关系",
        "category": "关系性质",
        "name": "反对称性",
        "formula": "(a, b) ∈ R ∧ a ≠ b ⟹ (b, a) ∉ R",
        "description": "若 a 与 b 有关系且 a ≠ b，则 b 与 a 无关系",
        "latex": r"(a, b) \in R \wedge a \neq b \Longrightarrow (b, a) \notin R",
        "condition": "R 为 A 上二元关系",
        "tags": "关系,反对称"
    },
    {
        "chapter": "第9章 关系",
        "category": "关系性质",
        "name": "传递性",
        "formula": "(a, b) ∈ R ∧ (b, c) ∈ R ⟹ (a, c) ∈ R",
        "description": "若 a 关系 b 且 b 关系 c，则 a 关系 c",
        "latex": r"(a, b) \in R \wedge (b, c) \in R \Longrightarrow (a, c) \in R",
        "condition": "R 为 A 上二元关系",
        "tags": "关系,传递"
    },
    {
        "chapter": "第9章 关系",
        "category": "等价关系",
        "name": "等价类基数",
        "formula": "|A| = Σ |[a]ᵢ|（等价类不交划分）",
        "description": "等价关系将集合划分为不交的等价类，其基数之和等于原集合",
        "latex": r"|A| = \sum_i |[a]_i|",
        "condition": "等价类构成 A 的划分",
        "tags": "关系,等价类,划分"
    },
    {
        "chapter": "第9章 关系",
        "category": "关系复合",
        "name": "关系复合",
        "formula": "R₁ ∘ R₂ = {(a, c) | ∃b: (a,b) ∈ R₂ ∧ (b,c) ∈ R₁}",
        "description": "关系 R₁ 与 R₂ 的复合",
        "latex": r"R_1 \circ R_2 = \{(a, c) \mid \exists b: (a, b) \in R_2 \wedge (b, c) \in R_1\}",
        "condition": "R₂ 的陪域含于 R₁ 的定义域",
        "tags": "关系,复合"
    },

    # ===================== 第10章 图 (6个) =====================
    {
        "chapter": "第10章 图",
        "category": "握手定理",
        "name": "握手定理",
        "formula": "Σ_{v∈V} deg(v) = 2|E|",
        "description": "无向图中所有顶点度数之和等于边数的两倍",
        "latex": r"\sum_{v \in V} \deg(v) = 2|E|",
        "condition": "无向图",
        "tags": "图,握手定理,度数"
    },
    {
        "chapter": "第10章 图",
        "category": "握手定理",
        "name": "有向图握手定理",
        "formula": "Σ_{v∈V} deg⁺(v) = Σ_{v∈V} deg⁻(v) = |E|",
        "description": "有向图中所有入度之和等于出度之和等于边数",
        "latex": r"\sum_{v \in V} \deg^+(v) = \sum_{v \in V} \deg^-(v) = |E|",
        "condition": "有向图",
        "tags": "图,握手定理,有向"
    },
    {
        "chapter": "第10章 图",
        "category": "欧拉回路",
        "name": "欧拉回路判定",
        "formula": "连通图存在欧拉回路 ⟺ 所有顶点度数为偶数",
        "description": "欧拉回路存在当且仅当图连通且所有顶点度数均为偶数",
        "latex": r"\text{欧拉回路} \iff \text{连通} \wedge \forall v,\ \deg(v) \text{ 为偶}",
        "condition": "无向连通图",
        "tags": "图,欧拉回路"
    },
    {
        "chapter": "第10章 图",
        "category": "欧拉回路",
        "name": "欧拉通路判定",
        "formula": "连通图存在欧拉通路 ⟺ 恰有 0 或 2 个奇度顶点",
        "description": "欧拉通路（非回路）存在的条件",
        "latex": r"\text{欧拉通路} \iff \text{连通} \wedge |\{v : \deg(v) \text{ 奇}\}| \in \{0, 2\}",
        "condition": "无向连通图",
        "tags": "图,欧拉通路"
    },
    {
        "chapter": "第10章 图",
        "category": "平面图",
        "name": "欧拉公式",
        "formula": "v − e + f = 2",
        "description": "连通平面图的顶点数减边数加面数等于 2",
        "latex": r"v - e + f = 2",
        "condition": "连通平面图",
        "tags": "图,平面图,欧拉公式"
    },
    {
        "chapter": "第10章 图",
        "category": "平面图",
        "name": "平面图边数上界",
        "formula": "若 v ≥ 3，则 e ≤ 3v − 6",
        "description": "简单连通平面图的边数上界",
        "latex": r"e \leq 3v - 6",
        "condition": "v ≥ 3 的简单平面图",
        "tags": "图,平面图,边数"
    },

    # ===================== 第11章 树 (6个) =====================
    {
        "chapter": "第11章 树",
        "category": "树的基本性质",
        "name": "树的边数",
        "formula": "n 顶点的树恰有 n−1 条边",
        "description": "树是连通无回路图，边数恰为顶点数减一",
        "latex": r"|E| = n - 1",
        "condition": "n 顶点的树",
        "tags": "树,边数"
    },
    {
        "chapter": "第11章 树",
        "category": "树的基本性质",
        "name": "树的等价刻画",
        "formula": "T 为树 ⟺ T 连通且无回路 ⟺ T 连通且 |E|=|V|−1 ⟺ T 无回路且加任一边成回路",
        "description": "树的多种等价定义",
        "latex": r"T \text{ 为树} \iff T \text{ 连通无回路} \iff T \text{ 连通且} |E|=|V|-1",
        "condition": "T 为无向图",
        "tags": "树,等价定义"
    },
    {
        "chapter": "第11章 树",
        "category": "二叉树",
        "name": "二叉树高度上界",
        "formula": "h ≤ n − 1，n 顶点二叉树高度至多 n−1",
        "description": "n 顶点二叉树的最大高度",
        "latex": r"h \leq n - 1",
        "condition": "n 顶点二叉树",
        "tags": "树,二叉树,高度"
    },
    {
        "chapter": "第11章 树",
        "category": "二叉树",
        "name": "满二叉树顶点数",
        "formula": "高度 h 的满二叉树有 2^(h+1) − 1 个顶点",
        "description": "满二叉树的顶点数公式",
        "latex": r"n = 2^{h+1} - 1",
        "condition": "高度 h 的满二叉树",
        "tags": "树,满二叉树"
    },
    {
        "chapter": "第11章 树",
        "category": "二叉树",
        "name": "完全二叉树叶节点数",
        "formula": "n₀ = n₂ + 1（叶节点 = 度2节点 + 1）",
        "description": "任意二叉树叶节点数等于度数为 2 的节点数加 1",
        "latex": r"n_0 = n_2 + 1",
        "condition": "任意二叉树",
        "tags": "树,二叉树,叶节点"
    },
    {
        "chapter": "第11章 树",
        "category": "Huffman编码",
        "name": "Huffman编码性质",
        "formula": "Σ freq(cᵢ) · depth(cᵢ) 最小",
        "description": "Huffman 树使加权路径长度最小，对应最优前缀编码",
        "latex": r"\sum_i \mathrm{freq}(c_i) \cdot \mathrm{depth}(c_i) \text{ 最小}",
        "condition": "字符频率已给",
        "tags": "树,Huffman,编码"
    },

    # ===================== 第12章 布尔代数 (5个) =====================
    {
        "chapter": "第12章 布尔代数",
        "category": "布尔代数",
        "name": "布尔补律",
        "formula": "x ∨ x̄ = 1,  x ∧ x̄ = 0",
        "description": "布尔代数中元素与补的并等于 1，交等于 0",
        "latex": r"x \vee \bar{x} = 1,\quad x \wedge \bar{x} = 0",
        "condition": "布尔代数 B = ({0,1}, ∨, ∧, ¬, 0, 1)",
        "tags": "布尔代数,补律"
    },
    {
        "chapter": "第12章 布尔代数",
        "category": "布尔代数",
        "name": "布尔吸收律",
        "formula": "x ∨ (x ∧ y) = x,  x ∧ (x ∨ y) = x",
        "description": "布尔代数的吸收律",
        "latex": r"x \vee (x \wedge y) = x,\quad x \wedge (x \vee y) = x",
        "condition": "布尔代数",
        "tags": "布尔代数,吸收律"
    },
    {
        "chapter": "第12章 布尔代数",
        "category": "布尔代数",
        "name": "德摩根律（布尔）",
        "formula": "(x ∨ y)̄ = x̄ ∧ ȳ,  (x ∧ y)̄ = x̄ ∨ ȳ",
        "description": "布尔代数中的德摩根律",
        "latex": r"\overline{x \vee y} = \bar{x} \wedge \bar{y},\quad \overline{x \wedge y} = \bar{x} \vee \bar{y}",
        "condition": "布尔代数",
        "tags": "布尔代数,德摩根"
    },
    {
        "chapter": "第12章 布尔代数",
        "category": "逻辑门",
        "name": "与或非门",
        "formula": "AND: xy, OR: x+y, NOT: x̄, NAND: (xy)̄, NOR: (x+y)̄",
        "description": "基本逻辑门的布尔表达式",
        "latex": r"\text{AND}: xy,\ \text{OR}: x+y,\ \text{NOT}: \bar{x},\ \text{NAND}: \overline{xy},\ \text{NOR}: \overline{x+y}",
        "condition": "二元布尔变量 x, y",
        "tags": "布尔,逻辑门"
    },
    {
        "chapter": "第12章 布尔代数",
        "category": "逻辑门",
        "name": "功能完备集",
        "formula": "{NAND} 与 {NOR} 各自为功能完备集",
        "description": "仅用 NAND 或仅用 NOR 即可表达任意布尔函数",
        "latex": r"\{\text{NAND}\},\ \{\text{NOR}\} \text{ 功能完备}",
        "condition": "允许常量 0, 1",
        "tags": "布尔,完备集"
    },

    # ===================== 第13章 建模计算 (6个) =====================
    {
        "chapter": "第13章 建模计算",
        "category": "Dijkstra",
        "name": "Dijkstra算法",
        "formula": "d(v) = min_{u∈S} {d(u) + w(u,v)}",
        "description": "单源最短路径：贪心扩展，每步选最小距离顶点",
        "latex": r"d(v) = \min_{u \in S} \{d(u) + w(u, v)\}",
        "condition": "非负权图",
        "tags": "图,最短路径,Dijkstra"
    },
    {
        "chapter": "第13章 建模计算",
        "category": "MST",
        "name": "Kruskal算法",
        "formula": "T = argmin Σ w(e), 不构成回路",
        "description": "按边权升序加入不构成回路的边构造 MST",
        "latex": r"T = \mathrm{argmin} \sum_{e \in T} w(e),\ \text{不构成回路}",
        "condition": "加权连通无向图",
        "tags": "图,MST,Kruskal"
    },
    {
        "chapter": "第13章 建模计算",
        "category": "MST",
        "name": "Prim算法",
        "formula": "T = T ∪ {argmin_{e∈δ(S)} w(e)}",
        "description": "从一个顶点开始，每次加入与已选集合相连的最小权边",
        "latex": r"T = T \cup \{\mathrm{argmin}_{e \in \delta(S)} w(e)\}",
        "condition": "加权连通无向图",
        "tags": "图,MST,Prim"
    },
    {
        "chapter": "第13章 建模计算",
        "category": "网络流",
        "name": "最大流最小割定理",
        "formula": "max |f| = min c(S, T)",
        "description": "网络中最大流的值等于最小割的容量",
        "latex": r"\max |f| = \min c(S, T)",
        "condition": "带容量的源汇网络",
        "tags": "图,网络流,最大流"
    },
    {
        "chapter": "第13章 建模计算",
        "category": "网络流",
        "name": "流守恒",
        "formula": "Σ_{(u,v)∈E} f(u,v) = Σ_{(v,w)∈E} f(v,w), v ≠ s, t",
        "description": "中间顶点流入等于流出",
        "latex": r"\sum_{(u,v) \in E} f(u, v) = \sum_{(v,w) \in E} f(v, w),\quad v \neq s, t",
        "condition": "中间顶点 v",
        "tags": "图,网络流,守恒"
    },
    {
        "chapter": "第13章 建模计算",
        "category": "TSP",
        "name": "旅行商问题",
        "formula": "min Σ_{i=1}^{n} w(v_{πᵢ}, v_{πᵢ₊₁}), πₙ₊₁ = π₁",
        "description": "求访问所有顶点恰一次并返回起点的最短回路",
        "latex": r"\min \sum_{i=1}^{n} w(v_{\pi_i}, v_{\pi_{i+1}}),\quad \pi_{n+1} = \pi_1",
        "condition": "完全加权图",
        "tags": "图,TSP,优化"
    },
]
