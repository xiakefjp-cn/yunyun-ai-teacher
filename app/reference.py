"""Read pasted text / DOCX without opening Word or interpreting instructions."""
import base64
import io
import re
import zipfile
import xml.etree.ElementTree as ET


def import_reference(name, data):
    if not isinstance(name,str) or not isinstance(data,str) or len(data)>2800000:
        raise ValueError('文件过大，请使用2MB以内的教案')
    raw=base64.b64decode(data,validate=True)
    if len(raw)>2000000: raise ValueError('文件超过2MB')
    if name.lower().endswith('.docx'):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            entry=z.getinfo('word/document.xml')
            if entry.file_size>2000000: raise ValueError('Word正文过大')
            xml=z.read(entry)
            if b'<!DOCTYPE' in xml or b'<!ENTITY' in xml: raise ValueError('不支持此XML内容')
            root=ET.fromstring(xml)
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text='\n'.join(''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in root.findall('.//w:p',ns))
        note='仅提取Word文字；图片、口型、四线三格和版式没有读取，请老师另行检查。'
    elif name.lower().endswith(('.txt','.md')):
        text=raw.decode('utf-8-sig');note='请检查文字并去掉个人信息，再生成。'
    else: raise ValueError('请选择docx、UTF-8文本或Markdown文件')
    text=re.sub(r'(?m)^\s*(?:执教人|授课人|姓名|学校|联系电话|手机)[：:].*$', '[个人信息行已隐藏]',text)
    if not text.strip() or len(text)>20000: raise ValueError('参考文字需为1至20000字，请精简后重试')
    return dict(text=text,note=note+' 文中其他个人信息仍需自行删去。')
