"""
试卷PDF生成模块：使用reportlab生成格式化的PDF试卷。

功能：
- 中文字体支持（SimSun/Microsoft YaHei/STSong-Light回退）
- 试卷标题居中、加粗、大字号
- 题号加粗
- 选项缩进对齐
- 分隔线装饰
- 页码（底部居中）
- 参考答案另起一页
"""
import os
import json
import logging

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Flowable
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# 尝试注册中文字体
_FONT_NAME = None
_FONT_NAME_BOLD = None
_FONT_REGISTERED = False

# Windows 系统常见中文字体路径
_WINDOWS_FONTS_DIR = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')

_FONT_CANDIDATES = [
    # (字体名称, 字体文件名, 粗体文件名)
    ('MSYaHei', 'msyh.ttc', 'msyhbd.ttc'),
    ('SimSun', 'simsun.ttc', None),
    ('SimHei', 'simhei.ttf', None),
    ('FangSong', 'simfang.ttf', None),
    ('KaiTi', 'simkai.ttf', None),
]

# CID 内置字体（回退方案）
_CID_FONT = 'STSong-Light'


def _register_chinese_fonts():
    """注册中文字体，优先使用系统字体，回退到CID字体"""
    global _FONT_NAME, _FONT_NAME_BOLD, _FONT_REGISTERED

    if _FONT_REGISTERED:
        return

    _FONT_REGISTERED = True

    # 尝试注册Windows系统字体
    for font_name, font_file, bold_file in _FONT_CANDIDATES:
        font_path = os.path.join(_WINDOWS_FONTS_DIR, font_file)
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                _FONT_NAME = font_name
                logger.info(f"注册中文字体: {font_name} ({font_path})")

                # 尝试注册粗体
                if bold_file:
                    bold_path = os.path.join(_WINDOWS_FONTS_DIR, bold_file)
                    if os.path.exists(bold_path):
                        try:
                            pdfmetrics.registerFont(TTFont(font_name + 'Bold', bold_path))
                            _FONT_NAME_BOLD = font_name + 'Bold'
                            logger.info(f"注册粗体字体: {_FONT_NAME_BOLD}")
                        except Exception:
                            _FONT_NAME_BOLD = font_name
                else:
                    _FONT_NAME_BOLD = font_name

                return  # 成功注册，直接返回
            except Exception as e:
                logger.warning(f"注册字体 {font_name} 失败: {e}")
                continue

    # 回退：使用reportlab内置CID字体
    try:
        pdfmetrics.registerFont(UnicodeCIDFont(_CID_FONT))
        _FONT_NAME = _CID_FONT
        _FONT_NAME_BOLD = _CID_FONT
        logger.info(f"使用CID回退字体: {_CID_FONT}")
    except Exception as e:
        logger.error(f"CID字体注册失败: {e}")
        _FONT_NAME = 'Helvetica'
        _FONT_NAME_BOLD = 'Helvetica-Bold'


class HLineFlowable(Flowable):
    """水平分隔线"""
    def __init__(self, width, thickness=1, color=colors.black, dash=None):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.dash = dash
        self.height = thickness + 4

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        if self.dash:
            self.canv.setDash(*self.dash)
        self.canv.line(0, 2, self.width, 2)


class DoubleLineFlowable(Flowable):
    """双线分隔线"""
    def __init__(self, width, color=colors.black):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.height = 10

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(1.5)
        self.canv.line(0, 8, self.width, 8)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 3, self.width, 3)


def _create_styles():
    """创建PDF样式"""
    _register_chinese_fonts()

    font = _FONT_NAME or 'Helvetica'
    font_bold = _FONT_NAME_BOLD or 'Helvetica-Bold'

    styles = {}

    # 试卷标题
    styles['exam_title'] = ParagraphStyle(
        'ExamTitle',
        fontName=font_bold,
        fontSize=22,
        leading=30,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    # 试卷副标题
    styles['exam_subtitle'] = ParagraphStyle(
        'ExamSubtitle',
        fontName=font_bold,
        fontSize=16,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    # 考试信息
    styles['exam_info'] = ParagraphStyle(
        'ExamInfo',
        fontName=font,
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    # 学生信息行
    styles['student_info'] = ParagraphStyle(
        'StudentInfo',
        fontName=font,
        fontSize=12,
        leading=20,
        alignment=TA_LEFT,
        spaceAfter=8,
    )

    # 大题标题
    styles['section_title'] = ParagraphStyle(
        'SectionTitle',
        fontName=font_bold,
        fontSize=14,
        leading=22,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
    )

    # 题目内容
    styles['question'] = ParagraphStyle(
        'Question',
        fontName=font,
        fontSize=11,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=2,
        leftIndent=0,
    )

    # 题号（加粗）
    styles['question_num'] = ParagraphStyle(
        'QuestionNum',
        fontName=font_bold,
        fontSize=11,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=2,
    )

    # 选项（缩进）
    styles['option'] = ParagraphStyle(
        'Option',
        fontName=font,
        fontSize=10.5,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=1,
        spaceAfter=1,
        leftIndent=24,
    )

    # 答案标题
    styles['answer_title'] = ParagraphStyle(
        'AnswerTitle',
        fontName=font_bold,
        fontSize=18,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    # 答案内容
    styles['answer'] = ParagraphStyle(
        'Answer',
        fontName=font,
        fontSize=10.5,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=2,
    )

    # 答案大题标题
    styles['answer_section'] = ParagraphStyle(
        'AnswerSection',
        fontName=font_bold,
        fontSize=12,
        leading=20,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=4,
    )

    return styles


def _escape_html(text):
    """转义XML/HTML特殊字符"""
    if not text:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('\n', '<br/>')
    return text


def _get_answer_text(question, answer_language):
    """根据答案语言设置获取答案文本"""
    answer_en = question.answer or ''
    answer_cn = question.answer_cn or ''

    if answer_language == 'cn':
        # 优先中文，无中文则用英文
        if answer_cn and answer_cn not in ('', '[待翻译]'):
            return answer_cn
        return answer_en
    elif answer_language == 'en':
        return answer_en
    else:  # both
        parts = []
        if answer_en:
            parts.append(answer_en)
        if answer_cn and answer_cn not in ('', '[待翻译]'):
            parts.append(f'（{answer_cn}）')
        return ''.join(parts) if parts else answer_en


def _parse_options(options_str):
    """解析选项JSON字符串"""
    if not options_str:
        return []
    try:
        options = json.loads(options_str)
        if isinstance(options, list):
            return options
        if isinstance(options, dict):
            return [f"{k}. {v}" for k, v in options.items()]
    except (json.JSONDecodeError, TypeError):
        # 尝试按行分割
        lines = options_str.strip().split('\n')
        return [line.strip() for line in lines if line.strip()]
    return []


def generate_exam_pdf(exam_data, output_path, include_answers=True, answer_language='cn'):
    """
    生成试卷PDF文件。

    参数:
        exam_data: generate_exam() 返回的试卷数据
        output_path: PDF输出路径
        include_answers: 是否包含答案
        answer_language: 答案语言（cn/en/both）

    返回: PDF文件路径
    """
    _register_chinese_fonts()
    styles = _create_styles()

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    page_width, page_height = A4
    content_width = page_width - 2 * 2 * cm  # 左右各2cm边距

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []

    # ===== 封面部分 =====
    # 双线装饰
    story.append(DoubleLineFlowable(content_width, colors.black))
    story.append(Spacer(1, 8))

    # 试卷标题
    story.append(Paragraph('离散数学试卷', styles['exam_title']))
    if exam_data.get('title'):
        story.append(Paragraph(_escape_html(exam_data['title']), styles['exam_subtitle']))

    # 考试信息
    story.append(Paragraph('考试时间：120分钟　　总分：100分', styles['exam_info']))
    story.append(Spacer(1, 4))
    story.append(DoubleLineFlowable(content_width, colors.black))
    story.append(Spacer(1, 16))

    # 学生信息行
    story.append(Paragraph('姓名：________________　　学号：________________　　班级：________________', styles['student_info']))
    story.append(Spacer(1, 12))

    # ===== 题目部分 =====
    question_num = 0  # 全局题号

    # 存储答案信息
    answer_data = []

    for group in exam_data.get('questions', []):
        type_name = group['type_name']
        questions = group['questions']
        score_per = group['score_per']
        total_score = len(questions) * score_per

        # 大题标题
        section_title = f'{"一二三四五六七八九十"[len(answer_data)]}、{type_name}（共{len(questions)}题，每题{score_per}分，共{total_score}分）'
        story.append(Paragraph(_escape_html(section_title), styles['section_title']))
        story.append(Spacer(1, 4))

        # 答案大题标题
        answer_items = []
        answer_section_title = f'{"一二三四五六七八九十"[len(answer_data)]}、{type_name}'

        for q in questions:
            question_num += 1

            # 题目内容
            q_text = _escape_html(q.question_text or '')
            story.append(Paragraph(f'<b>{question_num}.</b> {q_text}', styles['question']))

            # 如果是选择题，显示选项
            if q.question_type == 'choice' and q.options:
                options = _parse_options(q.options)
                if options:
                    for opt in options:
                        opt_text = _escape_html(opt)
                        story.append(Paragraph(opt_text, styles['option']))

            story.append(Spacer(1, 4))

            # 收集答案
            ans_text = _get_answer_text(q, answer_language)
            answer_items.append(f'{question_num}. {ans_text}')

        answer_data.append({
            'section_title': answer_section_title,
            'items': answer_items,
        })

    # ===== 参考答案部分 =====
    if include_answers and answer_data:
        story.append(PageBreak())
        story.append(DoubleLineFlowable(content_width, colors.black))
        story.append(Spacer(1, 4))
        story.append(Paragraph('参考答案', styles['answer_title']))
        story.append(DoubleLineFlowable(content_width, colors.black))
        story.append(Spacer(1, 12))

        for section in answer_data:
            story.append(Paragraph(_escape_html(section['section_title']), styles['answer_section']))
            # 答案以紧凑格式排列
            ans_text = '　'.join(_escape_html(item) for item in section['items'])
            story.append(Paragraph(ans_text, styles['answer']))
            story.append(Spacer(1, 8))

    # ===== 页码 =====
    def add_page_number(canvas, doc):
        canvas.saveState()
        page_num = canvas.getPageNumber()
        text = f"— {page_num} —"
        canvas.setFont(_FONT_NAME or 'Helvetica', 9)
        canvas.drawCentredString(page_width / 2, 1.2 * cm, text)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    return output_path


def generate_exam_html(exam_data, include_answers=True, answer_language='cn'):
    """
    生成试卷HTML预览。

    参数:
        exam_data: generate_exam() 返回的试卷数据
        include_answers: 是否包含答案
        answer_language: 答案语言（cn/en/both）

    返回: HTML字符串
    """
    question_num = 0
    section_idx = 0
    cn_nums = '一二三四五六七八九十'

    html_parts = []

    # 封面
    html_parts.append('<div class="exam-paper">')
    html_parts.append('<div class="exam-header">')
    html_parts.append('<div class="exam-double-line"></div>')
    html_parts.append(f'<h1 class="exam-main-title">离散数学试卷</h1>')
    if exam_data.get('title'):
        html_parts.append(f'<h2 class="exam-sub-title">{_escape_html(exam_data["title"])}</h2>')
    html_parts.append('<p class="exam-info">考试时间：120分钟　　总分：100分</p>')
    html_parts.append('<div class="exam-double-line"></div>')
    html_parts.append('</div>')

    # 学生信息
    html_parts.append('<div class="exam-student-info">')
    html_parts.append('姓名：________________　　学号：________________　　班级：________________')
    html_parts.append('</div>')

    # 题目
    for group in exam_data.get('questions', []):
        type_name = group['type_name']
        questions = group['questions']
        score_per = group['score_per']
        total_score = len(questions) * score_per

        section_title = f'{cn_nums[section_idx]}、{type_name}（共{len(questions)}题，每题{score_per}分，共{total_score}分）'
        html_parts.append(f'<div class="exam-section"><h3>{_escape_html(section_title)}</h3>')

        for q in questions:
            question_num += 1
            q_text = _escape_html(q.question_text or '')
            html_parts.append(f'<div class="exam-question"><b>{question_num}.</b> {q_text}')

            if q.question_type == 'choice' and q.options:
                options = _parse_options(q.options)
                if options:
                    html_parts.append('<div class="exam-options">')
                    for opt in options:
                        html_parts.append(f'<div class="exam-option">{_escape_html(opt)}</div>')
                    html_parts.append('</div>')

            html_parts.append('</div>')

        html_parts.append('</div>')
        section_idx += 1

    # 答案
    if include_answers:
        html_parts.append('<div class="exam-answers">')
        html_parts.append('<div class="exam-double-line"></div>')
        html_parts.append('<h2 class="exam-answer-title">参考答案</h2>')
        html_parts.append('<div class="exam-double-line"></div>')

        question_num = 0
        section_idx = 0
        for group in exam_data.get('questions', []):
            type_name = group['type_name']
            html_parts.append(f'<div class="exam-answer-section"><h4>{cn_nums[section_idx]}、{type_name}</h4>')
            html_parts.append('<div class="exam-answer-items">')
            for q in group['questions']:
                question_num += 1
                ans_text = _escape_html(_get_answer_text(q, answer_language))
                html_parts.append(f'<span class="exam-answer-item"><b>{question_num}.</b> {ans_text}</span>')
            html_parts.append('</div></div>')
            section_idx += 1

        html_parts.append('</div>')

    html_parts.append('</div>')

    return '\n'.join(html_parts)
