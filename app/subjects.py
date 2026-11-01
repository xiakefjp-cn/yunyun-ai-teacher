"""Subject-specific examples and explicit limits on automatic checks."""
import ast
import operator
from fractions import Fraction

SUBJECTS = ('信息科技', '语文', '数学')
STAGES = ('小学', '初中', '大学')


def stat_text(value):
    return '未提供' if value is None else str(value)+'人'


def general_stats():
    return dict(total=40, missing=5, needs_support=3, confusion=6)


def evaluate(expression):
    """Exact, bounded arithmetic. No eval, names, calls, powers or code execution."""
    if not isinstance(expression, str) or len(expression) > 160:
        raise ValueError('算式过长')
    tree = ast.parse(expression, mode='eval')
    if len(list(ast.walk(tree))) > 50:
        raise ValueError('算式过于复杂')
    operations = {ast.Add: operator.add, ast.Sub: operator.sub,
                  ast.Mult: operator.mul, ast.Div: operator.truediv}

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 1000000:
            value = Fraction(node.value)
        elif isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
            value = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](visit(node.left), visit(node.right))
        else:
            raise ValueError('只支持整数、括号和 + - * /，不支持变量、函数或幂')
        if abs(value.numerator) > 10**12 or value.denominator > 10**12:
            raise ValueError('计算结果超出范围')
        return value
    return visit(tree.body)


def arithmetic_case(case):
    try:
        actual = evaluate(case['expression'])
        expected = evaluate(case['expected'])
        return dict(**case, stdout=str(actual), error=None, passed=actual == expected)
    except (ValueError, TypeError, SyntaxError, ZeroDivisionError, RecursionError) as exc:
        return dict(**case, stdout='', error=str(exc), passed=False)


def verify_material(bundle):
    math = bundle['subject'] == '数学'
    reports = []
    for item in bundle['items'][1:]:
        if math:
            cases = [arithmetic_case(c) for c in item['calculations']]
            note = '只核对列出的算式，不判断题意、推理或教学讲解是否正确。'
        else:
            cases = [dict(label='示范或参考答案已填写', expected='已填写', stdout='已填写', error=None, passed=True),
                     dict(label='教师检查点已填写', expected='已填写', stdout='已填写', error=None, passed=True)]
            note = '仅检查材料是否填写齐全；未自动判断拼音、发音、书写或作文质量。'
        reports.append(dict(id=item['id'], title=item['title'], cases=cases,
                            kind='arithmetic' if math else 'completeness', note=note))
    return reports


def material_template(subject, stage, stats, topic='', minutes=40):
    """Offline examples are explicit samples, not arbitrary-topic generation."""
    writing = subject == '语文' and (stage!='小学' or any(w in topic for w in ('漫画', '习作', '写作', '作文')))
    if subject == '语文':
        title = '习作 漫画老师' if writing else '汉语拼音 j q x'
        objectives = (['找出人物一个鲜明特点', '用具体事例和细节表现特点', '按同伴建议修改一段习作'] if writing else
                      ['认读并区分j、q、x', '观察字形和四线三格位置，模仿书写', '通过卡牌练习两拼与三拼，区别音节和声母'])
        examples = ([
            ('从评价到事例', '“老师很幽默”只是评价。虚构示范：老师把漏掉标点的句子读成一口气，让大家笑着发现停顿的重要。让学生找出语言和动作，说明它们如何表现幽默。'),
            ('修改空泛的一段', '原句：“老师很负责，天天很辛苦。”修改任务：补一件自己观察到的小事，写清场景、动作或一句话。示范不是学生亲历，不能照搬成自己的经历。')
        ] if writing else [
            ('听音看形认识j、q、x', '教师出示自制字母卡并范读，学生指认j、q、x；再比较q与p的圆圈、竖线位置。声音由老师现场判断，文字页面不能判断孩子是否读准。'),
            ('卡牌拼读和观察书写', '用j和ī组成jī，用x、i、ā练习xiā；分清两张和三张卡牌的作用。老师用四线三格示范j、q、x，学生边观察边写，字形占格由老师核对。')
        ])
        exercises = ([
            ('圈出特点', '写出想描写的老师的一个特点，再列一件能表现它的小事。', '答案开放。特点与事例应对应，例如“有耐心”对应反复换方法解释问题。', ['特点明确', '事例具体', '不编造为亲身经历']),
            ('把事情写具体', '从提纲中选一件事，写出一个动作和一句话，请同伴指出哪里能看出特点。', '答案开放。参考标准：细节服务人物特点，事件经过让读者看得懂。', ['动作或语言具体', '能表现特点', '表达清楚']),
            ('修改并解释', '根据同伴的一条意见修改原段，标出改动，并说清为什么改。', '答案开放。能比较改前改后的具体变化，并解释它如何帮助突出特点。', ['有实际修改', '理由与文本对应', '尊重人物'])
        ] if writing else [
            ('指认和辨形', '在j、q、x、p四张卡中找出今天学的三个声母，说说q和p哪里不同。', '今天学习j、q、x。比较q和p时要指出竖线与圆圈的相对位置，老师用标准字形示范。', ['指认正确', '能比较字形']),
            ('两拼和三拼', '用卡牌拼读jī与xiā，说说第二个音节比第一个多了哪张卡。', 'jī练习两拼，xiā练习三拼；xiā中有介母i。读音是否准确由老师听辨。', ['能操作卡牌', '能区分两拼三拼', '读音由老师确认']),
            ('卡牌迁移与解释', '分别用j、q、x与ī卡相碰，拼读jī、qī、xī；说说换了哪张卡，哪些没有变。', '声母卡依次换成j、q、x，带调韵母ī卡不变。学生演示并解释，读音由老师听辨。', ['能准确换卡','能说清声母变而韵母不变','老师逐个听辨'])
        ])
        review = ['教师检查字形、音节、讲解和参考答案；开放题不设唯一答案',
                  '发音、口型、笔顺、四线三格位置需要现场示范，程序没有听读或识字评分能力',
                  '核对教材版本和本课时进度；第二课时的内容不能提前作为第一课时必会要求']
        activities = (['用一个动作或一句话猜人物特点，提醒不能嘲笑外貌', '比较空泛评价与具体事例，教师示范细节怎样表现特点',
                       '基础列提纲，进阶写片段，挑战修改；同伴指出一处能看出特点的文字', '展示修改前后的一句话，说清修改理由'] if writing else
                      ['翻字母卡复习旧知，先听几个孩子读，了解实际起点', '老师范读，学生指卡；比较q与p，用自制情境图帮助记形',
                       '观察四线三格并写卡；用jī、xiā两组卡练两拼和三拼，逐个听辨', '学生指出最易混的字母，教师检查；ü省点规则按课时进度预告或练习'])
        warning = ('写得空泛', '只写“负责、幽默”等评价，没有一件具体事', '追问“哪一次、做了什么、说了什么”，再修改一句话') if writing else (
            '音形易混', 'q和p混淆，或把声母读成完整音节', '摆卡比较字形，教师范读后逐个听，不能只看全班齐读')
    else:
        primary = stage == '小学'
        title = '乘法的初步认识' if primary else '一元一次方程入门'
        objectives = (['把几个相同加数相加写成乘法', '说清算式对应几组、每组几个', '用图或实物检查答案'] if primary else
                      ['理解等式两边做同样运算', '写出一元一次方程的求解过程', '把解代回原方程检验'])
        examples = ([
            ('从摆小棒到乘法', '摆3组小棒，每组4根：4+4+4=12，也可以写3×4=12。解释每个数在图中的意思。', [('4+4+4','12'),('3*4','12')]),
            ('比较相同加数', '2+2+2+2是4个2相加，可以用4×2表示；2+3+2不是相同加数，不能直接数成3个2。', [('2+2+2+2','8'),('4*2','8')])
        ] if primary else [
            ('等式两边一起减', 'x+3=8，两边同时减3，得x=5；代回原式5+3=8。', [('8-3','5'),('5+3','8')]),
            ('两步解方程', '2x+3=11，两边先减3，再同时除以2，得x=4；代回2×4+3=11。', [('(11-3)/2','4'),('2*4+3','11')])
        ])
        exercises = ([
            ('把加法改写成乘法', '把3+3+3+3改写成乘法，算出结果，并说出有几个3。', '4个3，4×3=12。', ['能找相同加数','能解释组数和每组数量'], [('3+3+3+3','12'),('4*3','12')]),
            ('用图解释', '每盘5个苹果，3盘共多少个？先画图再列式。', '5+5+5=15，3×5=15（个）。图应表示3组、每组5个。', ['图与数量对应','算式和单位正确'], [('5+5+5','15'),('3*5','15')]),
            ('判断能否直接用乘法', '3个盒子分别有4、4、5支笔，能直接用3×4算总数吗？请解释并修改。', '不能把不同数量当成3个4。可算4+4+5=13，或3×4+1=13。', ['识别不同加数','能解释修正'], [('4+4+5','13'),('3*4+1','13')])
        ] if primary else [
            ('一步方程', '解x+7=12，并代回检验。', 'x=5，检验5+7=12。', ['两边同时减7','代回检验'], [('12-7','5'),('5+7','12')]),
            ('两步方程', '解3x-2=10，写出两步运算。', '两边加2得3x=12，再除以3得x=4，代回3×4-2=10。', ['运算对等','结果与检验正确'], [('(10+2)/3','4'),('3*4-2','10')]),
            ('纠正错误过程', '有人解2x+4=10，直接写x=10-4=6。指出漏了什么并修正。', '漏掉两边除以2，x=(10-4)/2=3，代回2×3+4=10。', ['指出漏步','解释等式两边相同运算'], [('(10-4)/2','3'),('2*3+4','10')])
        ])
        review = ['算式检查只算列出的表达式，不判断应用题建模、图示或推理是否正确',
                  '教师逐项核对题意、参考答案、单位和解题步骤；不能只看计算结果']
        activities = ['用实物或短题了解学生已有认识', '教师示范两例，学生先预测再解释每一步',
                      '基础说算式，进阶写过程，挑战找错；教师抽查解释而非只看答案', '给一道换情境的题，请学生说出理由并检查结果']
        warning = ('只看答案', '会写结果但不能解释算式或等式变形', '让学生摆图、复述每一步，再给一道变化题')
    items = [dict(id='lesson', kind='lesson', title=title, stage=stage,
                  objectives=objectives, prerequisites=['由老师结合教材确认已有知识'],
                  segments=[dict(title=t, minutes=n, activity=a) for t,n,a in zip(
                      ['了解起点','示范与讨论','分层练习','回顾检查'], [5,12,18,minutes-35], activities)],
                  teacher_review=review)]
    # Scale time to 20–120 minutes without inventing a two-period schedule.
    weights=[.125,.3,.45]
    for s,w in zip(items[0]['segments'][:3],weights): s['minutes']=max(1,int(minutes*w))
    items[0]['segments'][3]['minutes']=minutes-sum(s['minutes'] for s in items[0]['segments'][:3])
    checks = ['教师核对内容与本课目标一致', '观察学生能否解释，不能只看抄出的答案']
    for i, data in enumerate(examples,1):
        x=dict(id=f'example_{i}',kind='example',title=data[0],content=data[1],checks=checks[:])
        if subject=='数学': x['calculations']=[dict(expression=a,expected=b) for a,b in data[2]]
        items.append(x)
    for id,level,data in zip(('basic','advanced','challenge'),('基础','进阶','挑战'),exercises):
        x=dict(id=id,kind='exercise',level=level,title=data[0],prompt=data[1],answer=data[2],rubric=data[3],checks=checks[:])
        if subject=='数学': x['calculations']=[dict(expression=a,expected=b) for a,b in data[4]]
        items.append(x)
    warnings=[dict(category=warning[0],evidence='教学中可能出现的问题，尚无本班实测结论',trigger=warning[1],intervention=warning[2]),
              dict(category='需要辅导',evidence=f"老师填写需辅导：{stat_text(stats['needs_support'])}，易混淆：{stat_text(stats['confusion'])}",trigger='全班齐答可能掩盖个体困难',intervention='抽查几位学生，让他们指认、解释或演示，再安排同伴帮助'),
              dict(category='缺少作业信息',evidence=f"未交练习：{stat_text(stats['missing'])}，原因待了解",trigger='未交不等于不会',intervention='先做简短课堂检查，了解后再补练')]
    return dict(title=title+'备课包',subject=subject,stage=stage,topic=title,minutes=minutes,stats=stats,items=items,warnings=warnings)
