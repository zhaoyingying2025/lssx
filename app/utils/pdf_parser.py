"""
Rosen《离散数学及其应用》第8版 目录结构定义。
仅保留章节结构数据供课件生成等模块使用。
"""

# Rosen 第8版目录结构定义
CHAPTER_STRUCTURE = {
    1: {
        'title_en': 'The Foundations: Logic and Proofs',
        'title_cn': '基础：逻辑与证明',
        'sections': [
            ('1.1', 'Propositional Logic', '命题逻辑'),
            ('1.2', 'Applications of Propositional Logic', '命题逻辑的应用'),
            ('1.3', 'Propositional Equivalences', '命题等价'),
            ('1.4', 'Predicates and Quantifiers', '谓词与量词'),
            ('1.5', 'Nested Quantifiers', '嵌套量词'),
            ('1.6', 'Rules of Inference', '推理规则'),
            ('1.7', 'Introduction to Proofs', '证明导论'),
            ('1.8', 'Proof Methods and Strategy', '证明方法与策略'),
        ],
        'key_concepts': ['proposition', 'logical operator', 'conditional statement', 'quantifier', 'proof']
    },
    2: {
        'title_en': 'Basic Structures: Sets, Functions, Sequences, Sums, and Matrices',
        'title_cn': '基本结构：集合、函数、序列、求和与矩阵',
        'sections': [
            ('2.1', 'Sets', '集合'),
            ('2.2', 'Set Operations', '集合运算'),
            ('2.3', 'Functions', '函数'),
            ('2.4', 'Sequences and Summations', '序列与求和'),
            ('2.5', 'Cardinality of Sets', '集合的基数'),
            ('2.6', 'Matrices', '矩阵'),
        ],
        'key_concepts': ['set', 'function', 'sequence', 'summation', 'matrix', 'cardinality']
    },
    3: {
        'title_en': 'Algorithms',
        'title_cn': '算法',
        'sections': [
            ('3.1', 'Algorithms', '算法'),
            ('3.2', 'The Growth of Functions', '函数的增长'),
            ('3.3', 'Complexity of Algorithms', '算法复杂度'),
        ],
        'key_concepts': ['algorithm', 'pseudocode', 'complexity', 'big-O', 'big-Theta']
    },
    4: {
        'title_en': 'Number Theory and Cryptography',
        'title_cn': '数论与密码学',
        'sections': [
            ('4.1', 'Divisibility and Modular Arithmetic', '整除性与模运算'),
            ('4.2', 'Integer Representations and Algorithms', '整数表示与算法'),
            ('4.3', 'Primes and Greatest Common Divisors', '素数与最大公约数'),
            ('4.4', 'Solving Congruences', '求解同余式'),
            ('4.5', 'Applications of Congruences', '同余的应用'),
            ('4.6', 'Cryptography', '密码学'),
        ],
        'key_concepts': ['divisibility', 'prime', 'modular arithmetic', 'gcd', 'congruence', 'cryptography']
    },
    5: {
        'title_en': 'Induction and Recursion',
        'title_cn': '归纳与递归',
        'sections': [
            ('5.1', 'Mathematical Induction', '数学归纳法'),
            ('5.2', 'Strong Induction and Well-Ordering', '强归纳与良序'),
            ('5.3', 'Recursive Definitions and Structural Induction', '递归定义与结构归纳'),
            ('5.4', 'Recursive Algorithms', '递归算法'),
            ('5.5', 'Program Correctness', '程序正确性'),
        ],
        'key_concepts': ['mathematical induction', 'strong induction', 'recursion', 'recursive algorithm']
    },
    6: {
        'title_en': 'Counting',
        'title_cn': '计数',
        'sections': [
            ('6.1', 'The Basics of Counting', '计数基础'),
            ('6.2', 'The Pigeonhole Principle', '鸽巢原理'),
            ('6.3', 'Permutations and Combinations', '排列与组合'),
            ('6.4', 'Binomial Coefficients and Identities', '二项式系数与恒等式'),
            ('6.5', 'Generalized Permutations and Combinations', '广义排列与组合'),
        ],
        'key_concepts': ['counting', 'pigeonhole principle', 'permutation', 'combination', 'binomial coefficient']
    },
    7: {
        'title_en': 'Discrete Probability',
        'title_cn': '离散概率',
        'sections': [
            ('7.1', 'An Introduction to Discrete Probability', '离散概率导论'),
            ('7.2', 'Probability Theory', '概率论'),
            ('7.3', 'Bayes\' Theorem', '贝叶斯定理'),
            ('7.4', 'Expected Value and Variance', '期望值与方差'),
        ],
        'key_concepts': ['probability', 'Bayes theorem', 'expected value', 'variance', 'conditional probability']
    },
    8: {
        'title_en': 'Advanced Counting Techniques',
        'title_cn': '高级计数技术',
        'sections': [
            ('8.1', 'Applications of Recurrence Relations', '递推关系的应用'),
            ('8.2', 'Solving Linear Recurrence Relations', '求解线性递推关系'),
            ('8.3', 'Divide-and-Conquer Algorithms and Recurrence Relations', '分治算法与递推关系'),
            ('8.4', 'Generating Functions', '生成函数'),
            ('8.5', 'Inclusion-Exclusion', '容斥原理'),
            ('8.6', 'Applications of Inclusion-Exclusion', '容斥原理的应用'),
        ],
        'key_concepts': ['recurrence relation', 'generating function', 'inclusion-exclusion', 'divide-and-conquer']
    },
    9: {
        'title_en': 'Relations',
        'title_cn': '关系',
        'sections': [
            ('9.1', 'Relations and Their Properties', '关系及其性质'),
            ('9.2', 'n-ary Relations and Their Applications', 'n元关系及其应用'),
            ('9.3', 'Representing Relations', '关系的表示'),
            ('9.4', 'Closures of Relations', '关系的闭包'),
            ('9.5', 'Equivalence Relations', '等价关系'),
            ('9.6', 'Partial Orderings', '偏序'),
        ],
        'key_concepts': ['relation', 'equivalence relation', 'partial order', 'closure', 'n-ary relation']
    },
    10: {
        'title_en': 'Graphs',
        'title_cn': '图',
        'sections': [
            ('10.1', 'Graphs and Graph Models', '图与图模型'),
            ('10.2', 'Graph Terminology and Special Types of Graphs', '图术语与特殊图类型'),
            ('10.3', 'Representing Graphs and Graph Isomorphism', '图的表示与图同构'),
            ('10.4', 'Connectivity', '连通性'),
            ('10.5', 'Euler and Hamilton Paths', '欧拉与哈密顿路径'),
            ('10.6', 'Shortest-Path Problems', '最短路径问题'),
            ('10.7', 'Planar Graphs', '平面图'),
            ('10.8', 'Graph Coloring', '图着色'),
        ],
        'key_concepts': ['graph', 'Euler path', 'Hamilton path', 'connectivity', 'planar graph', 'graph coloring']
    },
    11: {
        'title_en': 'Trees',
        'title_cn': '树',
        'sections': [
            ('11.1', 'Introduction to Trees', '树导论'),
            ('11.2', 'Applications of Trees', '树的应用'),
            ('11.3', 'Tree Traversal', '树的遍历'),
            ('11.4', 'Spanning Trees', '生成树'),
            ('11.5', 'Minimum Spanning Trees', '最小生成树'),
        ],
        'key_concepts': ['tree', 'spanning tree', 'tree traversal', 'minimum spanning tree', 'binary tree']
    },
    12: {
        'title_en': 'Boolean Algebra',
        'title_cn': '布尔代数',
        'sections': [
            ('12.1', 'Boolean Functions', '布尔函数'),
            ('12.2', 'Representing Boolean Functions', '布尔函数的表示'),
            ('12.3', 'Logic Gates', '逻辑门'),
            ('12.4', 'Minimization of Circuits', '电路的最小化'),
        ],
        'key_concepts': ['Boolean function', 'logic gate', 'Boolean algebra', 'minimization', 'Karnaugh map']
    },
    13: {
        'title_en': 'Modeling Computation',
        'title_cn': '计算建模',
        'sections': [
            ('13.1', 'Languages and Grammars', '语言与文法'),
            ('13.2', 'Finite-State Machines with Output', '带输出的有限状态机'),
            ('13.3', 'Finite-State Machines with No Output', '无输出的有限状态机'),
            ('13.4', 'Language Recognition', '语言识别'),
            ('13.5', 'Turing Machines', '图灵机'),
        ],
        'key_concepts': ['grammar', 'finite-state machine', 'Turing machine', 'language recognition', 'formal language']
    },
}
