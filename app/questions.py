"""Question selection, empty model contracts and application-owned provenance."""
import copy
import hashlib
import json
import re
from pathlib import Path

MODES = ('model', 'bank', 'mixed')
LEVELS = ('基础', '进阶', '挑战')
BANK_PATH = Path(__file__).resolve().parent / 'question_bank.json'


def builtin_questions():
    return json.loads(BANK_PATH.read_text('utf-8'))['questions']


def validate_record(record):
    if not isinstance(record, dict) or not re.fullmatch('[a-z][a-z0-9_-]{0,59}', record.get('id','')):
        raise ValueError('题库ID需以小写字母开头，只用字母、数字、下划线或短横线')
    if record.get('subject') not in ('语文','数学','信息科技'):
        raise ValueError('题库学科无效')
    if not isinstance(record.get('stages'),list) or not record['stages'] or any(s not in ('小学','初中','大学') for s in record['stages']):
        raise ValueError('题库需填写适用学段stages')
    if not all(isinstance(record.get(k),str) and record[k].strip() for k in ('topic','source_label')):
        raise ValueError('题库需课题topic和来源source_label')
    if not isinstance(record.get('tags'),list) or not all(isinstance(t,str) for t in record['tags']):
        raise ValueError('题库tags需为文字数组')
    if record.get('level') not in LEVELS or not isinstance(record.get('item'),dict):
        raise ValueError('题库需基础/进阶/挑战级别和完整item')
    if record['item'].get('kind')!='exercise' or record['item'].get('level')!=record['level']:
        raise ValueError('题库item必须是对应级别的练习')
    if len(json.dumps(record,ensure_ascii=False))>25000: raise ValueError('单道题过长')
    return record


def search_questions(records, subject, stage, topic='', query=''):
    candidates=[]
    needle=(topic+' '+query).lower()
    for record in records:
        if record['subject']!=subject or stage not in record['stages']: continue
        tags=[record['topic'],*record['tags']]
        score=sum(len(t) for t in tags if t.lower() in needle)
        # Topic matching is explicit; do not silently return a different course.
        if topic and not any(t.lower() in topic.lower() or topic.lower() in t.lower() for t in tags): continue
        candidates.append((score,record))
    return [copy.deepcopy(r) for _,r in sorted(candidates,key=lambda p:(-p[0],p[1]['id']))]


def select_questions(records, subject, stage, topic, ids=None):
    candidates=search_questions(records,subject,stage,topic)
    if ids is not None:
        if not isinstance(ids,list) or len(ids)>3 or any(not isinstance(i,str) for i in ids) or len(set(ids))!=len(ids):
            raise ValueError('最多选择三道不同题库题，每个级别一题')
        allowed={r['id']:r for r in candidates}
        if any(i not in allowed for i in ids): raise ValueError('所选题目与学科、学段或课题不匹配，请重新选题')
        candidates=[allowed[i] for i in ids]
    selected={}
    for record in candidates:
        if record['level'] in selected:
            if ids is not None: raise ValueError('同一级别只能选一道题')
            continue
        selected[record['level']]=record
    return selected


def empty_contract(bundle):
    """Only shape, metadata and stable IDs. No worked questions or answers."""
    b=copy.deepcopy(bundle)
    b['title']=''
    for item in b['items']:
        item['title']=''
        if item['kind']=='lesson':
            item['objectives']=[''];item['prerequisites']=[''];item['teacher_review']=['']
            item['segments']=[dict(title='',minutes=s['minutes'],activity='') for s in item['segments']]
        else:
            for key in ('prompt','answer','solution','explanation','content','code'):
                if key in item:item[key]=''
            for key in ('rubric','checks'):
                if key in item:item[key]=['']
            if 'tests' in item:item['tests']=[dict(stdin='',expected='') for _ in range(3)]
            if 'calculations' in item:item['calculations']=[dict(expression='',expected='')]
            if item['kind']=='exercise':
                item['estimated_minutes']=0;item['participation']='必做' if item['level']!='挑战' else '选做'
    b['warnings']=[dict(category='',evidence='',trigger='',intervention='')]
    return b


def apply_bank(bundle, selected):
    if not isinstance(bundle,dict) or not isinstance(bundle.get('items'),list):
        raise ValueError('最外层需直接提供items数组，不能将items写成对象或包裹bundle/result')
    for i,item in enumerate(bundle['items']):
        if not isinstance(item,dict): raise ValueError('items数组中每项必须是对象')
        if item.get('kind')=='exercise' and item.get('level') in selected:
            replacement=copy.deepcopy(selected[item['level']]['item'])
            replacement['id']=item['id']
            bundle['items'][i]=replacement
    return bundle


def require_answers(bundle):
    for item in bundle['items']:
        if item['kind']!='exercise':continue
        if bundle.get('subject','信息科技')=='信息科技' and not (isinstance(item.get('solution'),str) and item['solution'].strip()):
            raise ValueError('每道编程题除了代码，还需要solution解题思路')
        if type(item.get('estimated_minutes')) is not int or not 1<=item['estimated_minutes']<=120:
            raise ValueError('每道练习需estimated_minutes预计用时（1到120分钟）')
        if item.get('participation') not in ('必做','选做'):raise ValueError('练习participation需为必做或选做')


def content_signature(item):
    fields={k:item.get(k) for k in ('title','prompt','code','answer')}
    return hashlib.sha256(json.dumps(fields,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def provenance(bundle, selected, records):
    sources={}
    for item in bundle['items']:
        if item['kind']!='exercise':continue
        record=selected.get(item['level'])
        if record:
            sources[item['id']]=dict(kind='question_bank',bank_id=record['id'],source_label=record['source_label'],
                catalog=record.get('catalog','built_in'),fingerprint=content_signature(item),teacher_reviewed=False)
        else:
            matched=next((r for r in records if content_signature(r['item'])==content_signature(item)),None)
            sources[item['id']]=dict(kind='model_generated',source_label='大模型根据本轮需求返回；不保证独创性',
                exact_bank_match=matched['id'] if matched else None,teacher_reviewed=False)
    bundle['question_sources']=sources
    return sources
