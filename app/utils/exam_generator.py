"""
组卷引擎模块：根据参数从题库中抽取题目组成试卷。

核心算法：
1. 根据章节和题型筛选可用题目
2. 按难度分布随机抽取题目
3. 确保不重复抽题
4. 题目按章节→题型→难度排序
5. 如果某类题目不足，从其他难度补充并提示
"""
import random
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# 题型中文名称映射
QUESTION_TYPE_NAMES = {
    'choice': '选择题',
    'fill': '填空题',
    'true_false': '判断题',
    'proof': '证明题',
    'calc': '计算题',
    'short_answer': '简答题',
}

# 题型排序顺序
QUESTION_TYPE_ORDER = ['choice', 'true_false', 'fill', 'calc', 'proof', 'short_answer']

# 难度中文名称映射
DIFFICULTY_NAMES = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难',
}

# 难度排序顺序
DIFFICULTY_ORDER = ['easy', 'medium', 'hard']

# 各题型默认分值
DEFAULT_SCORES = {
    'choice': 3,
    'true_false': 2,
    'fill': 3,
    'calc': 8,
    'proof': 10,
    'short_answer': 6,
}


def generate_exam(title, chapters, question_types, difficulty_distribution,
                  total_count, include_answers=True, answer_language='cn'):
    """
    生成试卷。

    参数:
        title: 试卷标题
        chapters: 章节列表（如 [1, 2, 5]），空列表表示全部章节
        question_types: 题型列表（如 ['choice', 'fill']）
        difficulty_distribution: 难度分布字典，如 {'easy': 3, 'medium': 5, 'hard': 2}
                                 表示简单:中等:困难的比例
        total_count: 总题数
        include_answers: 是否包含答案
        answer_language: 答案语言（cn/en/both）

    返回: {
        'title': 标题,
        'questions': 按题型分组的题目列表,
        'warnings': 警告信息列表,
        'stats': 统计信息,
    }
    """
    from app.models import Quiz
    from app import db

    warnings = []

    # Step 1: 筛选可用题目
    query = Quiz.query
    if chapters:
        # 章节可能是 "第1章" 或 "1" 等格式，需要灵活匹配
        chapter_filters = []
        for ch in chapters:
            chapter_filters.append(Quiz.chapter == str(ch))
            chapter_filters.append(Quiz.chapter == f'第{ch}章')
            chapter_filters.append(Quiz.chapter.like(f'%{ch}%'))
        if chapter_filters:
            query = query.filter(db.or_(*chapter_filters))

    if question_types:
        query = query.filter(Quiz.question_type.in_(question_types))

    available_questions = query.all()

    if not available_questions:
        return {
            'title': title,
            'questions': [],
            'warnings': ['没有找到符合条件的题目，请调整筛选条件'],
            'stats': {'total': 0, 'by_type': {}, 'by_difficulty': {}},
        }

    # Step 2: 按难度分组
    questions_by_difficulty = defaultdict(list)
    for q in available_questions:
        diff = q.difficulty or 'medium'
        questions_by_difficulty[diff].append(q)

    # Step 3: 计算各难度应抽题数
    total_weight = sum(difficulty_distribution.values())
    if total_weight == 0:
        total_weight = 1
        difficulty_distribution = {'easy': 3, 'medium': 5, 'hard': 2}

    target_counts = {}
    for diff in DIFFICULTY_ORDER:
        weight = difficulty_distribution.get(diff, 0)
        target_counts[diff] = round(total_count * weight / total_weight)

    # 修正舍入误差
    diff = total_count - sum(target_counts.values())
    if diff != 0:
        # 将差值加到中等难度
        target_counts['medium'] = target_counts.get('medium', 0) + diff

    # Step 4: 按难度抽取题目
    selected = []
    used_ids = set()

    for diff_key in DIFFICULTY_ORDER:
        target = target_counts.get(diff_key, 0)
        pool = [q for q in questions_by_difficulty.get(diff_key, []) if q.id not in used_ids]

        if len(pool) >= target:
            sampled = random.sample(pool, target)
        else:
            # 题目不足，全部抽取
            sampled = pool[:]
            deficit = target - len(sampled)
            if deficit > 0:
                warnings.append(
                    f'{DIFFICULTY_NAMES.get(diff_key, diff_key)}题目不足：'
                    f'需要{target}题，仅有{len(pool)}题，缺少{deficit}题'
                )
                # 从其他难度补充
                other_pool = [q for q in available_questions if q.id not in used_ids
                              and q.id not in {s.id for s in sampled}]
                if other_pool:
                    supplement_count = min(deficit, len(other_pool))
                    supplement = random.sample(other_pool, supplement_count)
                    sampled.extend(supplement)
                    if supplement_count < deficit:
                        warnings.append(
                            f'补充不足：仅补充了{supplement_count}题，仍缺{deficit - supplement_count}题'
                        )

        for q in sampled:
            used_ids.add(q.id)
        selected.extend(sampled)

    # Step 5: 按章节→题型→难度排序
    def sort_key(q):
        ch_num = _extract_chapter_num(q.chapter) or 999
        type_idx = QUESTION_TYPE_ORDER.index(q.question_type) if q.question_type in QUESTION_TYPE_ORDER else 99
        diff_idx = DIFFICULTY_ORDER.index(q.difficulty) if q.difficulty in DIFFICULTY_ORDER else 1
        return (ch_num, type_idx, diff_idx, q.question_number or 0)

    selected.sort(key=sort_key)

    # Step 6: 按题型分组
    grouped = defaultdict(list)
    for q in selected:
        grouped[q.question_type].append(q)

    # 按预定义顺序排列题型分组
    ordered_groups = []
    for qt in QUESTION_TYPE_ORDER:
        if qt in grouped and grouped[qt]:
            ordered_groups.append({
                'type': qt,
                'type_name': QUESTION_TYPE_NAMES.get(qt, qt),
                'questions': grouped[qt],
                'score_per': DEFAULT_SCORES.get(qt, 5),
            })

    # 处理不在预定义顺序中的题型
    for qt in grouped:
        if qt not in QUESTION_TYPE_ORDER:
            ordered_groups.append({
                'type': qt,
                'type_name': QUESTION_TYPE_NAMES.get(qt, qt),
                'questions': grouped[qt],
                'score_per': DEFAULT_SCORES.get(qt, 5),
            })

    # 统计信息
    stats = {
        'total': len(selected),
        'by_type': {qt: len(qs) for qt, qs in grouped.items()},
        'by_difficulty': {},
    }
    for q in selected:
        d = q.difficulty or 'medium'
        stats['by_difficulty'][d] = stats['by_difficulty'].get(d, 0) + 1

    return {
        'title': title,
        'questions': ordered_groups,
        'warnings': warnings,
        'stats': stats,
    }


def get_available_chapters():
    """获取题库中所有可用章节"""
    from app.models import Quiz
    chapters = Quiz.query.with_entities(Quiz.chapter).distinct().all()
    result = []
    for (ch,) in chapters:
        if ch:
            result.append(ch)
    return sorted(result, key=_extract_chapter_num)


def get_available_question_types():
    """获取题库中所有可用题型"""
    from app.models import Quiz
    types = Quiz.query.with_entities(Quiz.question_type).distinct().all()
    result = []
    for (qt,) in types:
        if qt:
            result.append(qt)
    return sorted(result, key=lambda x: QUESTION_TYPE_ORDER.index(x) if x in QUESTION_TYPE_ORDER else 99)


def get_question_counts_by_chapter_and_type():
    """获取各章节各题型的题目数量"""
    from app.models import Quiz
    from app import db

    results = db.session.query(
        Quiz.chapter, Quiz.question_type, db.func.count(Quiz.id)
    ).group_by(Quiz.chapter, Quiz.question_type).all()

    counts = {}
    for ch, qt, cnt in results:
        if ch not in counts:
            counts[ch] = {}
        counts[ch][qt] = cnt
    return counts


def _extract_chapter_num(chapter_str):
    """从章节字符串中提取章号数字"""
    if not chapter_str:
        return 9999
    import re
    m = re.search(r'(\d+)', str(chapter_str))
    return int(m.group(1)) if m else 9999
