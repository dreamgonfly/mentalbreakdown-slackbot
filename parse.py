from dateutil.parser import parse
from datetime import datetime, timedelta
import re
import pytz
from config import TIMEZONE

# im_list = [im['id'] for im in slack_client.api_call('im.list')['ims']]
BOT_ID = 'U37V4BCBB'
def filter_message(message):
#     if 'text' in message and message['type'] == 'message' and message['channel'] in im_list:
    if 'type' in message and message['type'] == 'message' and message['user'] != BOT_ID:
        return True

def matching(task):
    datetime_format = r'(\d+-)?\d+-\d+ \d+:\d+(:\d+)?|(\d+-)?\d+-\d+|\d+:\d+(:\d+)?|\d+h|\d+d|\d+m|today|tomorrow|tdy|tmr|x'
    start_datetime = r' ?(?P<scheduled>{dt})? ?~ ?(?P<due>{dt})?'.format(dt=datetime_format)
    start_required_time = r'(?P<required_time>\d+)?( (?P<scheduled>{dt})? ?~ ?(?P<due>{dt})?)?$'.format(dt=datetime_format)
    start_content = r'^(?P<content>.*?)( (?P<required_time>\d+))?(( (?P<scheduled>{dt}))? ?~ ?(?P<due>{dt})?)?$'.format(dt=datetime_format)
    
    match_datetime = re.match(start_datetime, task)
    if match_datetime:
        return match_datetime.groupdict()
    
    match_required_time = re.match(start_required_time, task)
    if match_required_time:
        return match_required_time.groupdict()
    
    match_content = re.match(start_content, task)
    return match_content.groupdict()

n = re.compile(r'^n$', re.I)
d = re.compile(r'^d$', re.I)
d_id = re.compile(r'^d\s+(?P<id>\d{1,3})$', re.I)
c = re.compile(r'^c$', re.I)
c_id = re.compile(r'^c\s+(?P<id>\d{1,3})$', re.I)
pp = re.compile(r'^pp$', re.I)
pp_id = re.compile(r'^pp\s+(?P<id>\d{1,3})$', re.I)
l = re.compile(r'^l$', re.I)
l_size = re.compile(r'^l\s+-(?P<size>\d+)$', re.I)
z = re.compile(r'^z$', re.I)
bs = re.compile(r'^bs *(\n.*?)+$', re.I)
bs_id = re.compile(r'^bs +(?P<id>\d{1,3}) *(\n.*?)+$', re.I)
bp = re.compile(r'^bp *(\n.*?)+$', re.I)
bp_id = re.compile(r'^bp +(?P<id>\d{1,3}) *(\n.*?)+$', re.I)
p = re.compile(r'^p (?P<task>.*)$', re.I)
p_target = re.compile(r'^p +(?P<target>\d{1,3}) +(?P<task>.*)$', re.I)
p_target_source = re.compile(r'^p +(?P<target>\d{1,3}) +(?P<source>\d{1,3})$', re.I)
a = re.compile(r'^a (?P<task>.*)$', re.I)
a_source = re.compile(r'^a +(?P<source>\d{1,3}) +(?P<task>.*)$', re.I)
a_source_target = re.compile(r'^a +(?P<source>\d{1,3}) +(?P<target>\d{1,3})$', re.I)
top = re.compile(r'top|top hour', re.I)
u = re.compile(r'^u +(?P<task>.*)$', re.I)
u_id = re.compile(r'^u +(?P<id>\d{1,3}) +(?P<task>.*)$', re.I)

def parse_task(task):
    parsed = {}
    match_dict = matching(task)
    if 'content' in match_dict and match_dict['content']:
        parsed['content'] = match_dict['content']
    if 'required_time' in match_dict and match_dict['required_time']:
        parsed['required_time'] = int(match_dict['required_time'])
    if match_dict['scheduled']:
        scheduled_raw = match_dict['scheduled']
        if scheduled_raw.endswith('d'):
            day = int(scheduled_raw[:-1])
            scheduled = datetime.now(TIMEZONE) + timedelta(day)
            scheduled = scheduled.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        elif scheduled_raw.endswith('h'):
            hour = int(scheduled_raw[:-1])
            scheduled = datetime.now(pytz.utc) + timedelta(hours = hour)
        elif scheduled_raw.endswith('m'):
            minute = int(scheduled_raw[:-1])
            scheduled = datetime.now(pytz.utc) + timedelta(minutes = minute)
        elif scheduled_raw in ['today', 'tdy']:
            scheduled = datetime.now(TIMEZONE)
            scheduled = scheduled.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        elif scheduled_raw in ['tomorrow', 'tmr']:
            scheduled = datetime.now(TIMEZONE) + timedelta(1)
            scheduled = scheduled.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        elif scheduled_raw == 'x':
            scheduled = None
        else:
            scheduled = TIMEZONE.localize(parse(scheduled_raw)).astimezone(pytz.utc)
        parsed['scheduled'] = scheduled
    if match_dict['due']:
        due_raw = match_dict['due']
        if due_raw.endswith('d'):
            day = int(due_raw[:-1])
            due = datetime.now(TIMEZONE) + timedelta(day)
            due = due.replace(hour=23, minute=59, second=0, microsecond=0).astimezone(pytz.utc)
        elif due_raw.endswith('h'):
            hour = int(due_raw[:-1])
            due = datetime.now(pytz.utc) + timedelta(hours = hour)
        elif due_raw.endswith('m'):
            minute = int(due_raw[:-1])
            due = datetime.now(pytz.utc) + timedelta(minutes = minute)
        elif due_raw in ['today', 'tdy']:
            due = datetime.now(TIMEZONE).replace(hour=23, minute=59, second=0, microsecond=0).astimezone(pytz.utc)
        elif due_raw in ['tomorrow', 'tmr']:
            due = datetime.now(TIMEZONE) + timedelta(1)
            due = due.replace(hour=23, minute=59, second=0, microsecond=0).astimezone(pytz.utc)
        elif due_raw == 'x':
            due = None
        else:
            due = TIMEZONE.localize(parse(due_raw))
            if due.hour == 0 and due.minute == 0:
                due = due + timedelta(1) - timedelta(minutes = 1)
                due = due.astimezone(pytz.utc)
        parsed['due'] = due
    return parsed

def parse_message(message):
    cleaned = message['text'].strip()
    parsed = {}
    if n.match(cleaned): parsed['command'] = 'next'
    elif d.match(cleaned): parsed['command'] = 'delete'
    elif d_id.match(cleaned): parsed['command'] = 'delete'; parsed['id'] = int(d_id.match(cleaned).group('id'))
    elif c.match(cleaned): parsed['command'] = 'complete'
    elif c_id.match(cleaned): parsed['command'] = 'complete'; parsed['id'] = int(c_id.match(cleaned).group('id'))
    elif pp.match(cleaned): parsed['command'] = 'postpone'
    elif pp_id.match(cleaned): parsed['command'] = 'postpone'; parsed['id'] = int(pp_id.match(cleaned).group('id'))
    elif l.match(cleaned): parsed['command'] = 'list'
    elif l_size.match(cleaned): parsed['command'] = 'list'; parsed['size'] = int(l_size.match(cleaned).group('size'))
    elif z.match(cleaned): parsed['command'] = 'cancel'
    elif bs.match(cleaned): 
        parsed['command'] = 'breakdown sequential'
        parsed['tasks'] = [parse_task(task) for task in cleaned.split('\n')[1:]]
    elif bs_id.match(cleaned): 
        parsed['command'] = 'breakdown sequential'
        parsed['id'] = int(bs_id.match(cleaned).group('id'))
        parsed['tasks'] = [parse_task(task) for task in cleaned.split('\n')[1:]]
    elif bp.match(cleaned): 
        parsed['command'] = 'breakdown parallel'
        parsed['tasks'] = [parse_task(task) for task in cleaned.split('\n')[1:]]
    elif bp_id.match(cleaned): 
        parsed['command'] = 'breakdown parallel'
        parsed['id'] = int(bp_id.match(cleaned).group('id'))
        parsed['tasks'] = [parse_task(task) for task in cleaned.split('\n')[1:]]
    elif p_target_source.match(cleaned):
        parsed['command'] = 'prepend'
        parsed['target'] = int(p_target_source.match(cleaned).group('target'))
        parsed['source'] = int(p_target_source.match(cleaned).group('source'))
    elif p_target.match(cleaned):
        parsed['command'] = 'prepend'; parsed['target'] = int(p_target.match(cleaned).group('target'))
        parsed['task'] = parse_task(p_target.match(cleaned).group('task'))        
    elif p.match(cleaned): 
        parsed['command'] = 'prepend'; parsed['task'] = parse_task(p.match(cleaned).group('task'))
    elif a_source_target.match(cleaned):
        parsed['command'] = 'append'
        parsed['target'] = int(a_source_target.match(cleaned).group('target'))
        parsed['source'] = int(a_source_target.match(cleaned).group('source'))
    elif a_source.match(cleaned):
        parsed['command'] = 'append'; parsed['source'] = int(a_source.match(cleaned).group('source'))
        parsed['task'] = parse_task(a_source.match(cleaned).group('task'))        
    elif a.match(cleaned): 
        parsed['command'] = 'append'; parsed['task'] = parse_task(a.match(cleaned).group('task'))
    elif u_id.match(cleaned): 
        parsed['command'] = 'update'; parsed['id'] = int(u_id.match(cleaned).group('id'))
        parsed['task'] = parse_task(u_id.match(cleaned).group('task'))
    elif u.match(cleaned): parsed['command'] = 'update'; parsed['task'] = parse_task(u.match(cleaned).group('task'))
    elif top.match(cleaned): parsed['command'] = 'top hour'
    else: parsed['command'] = 'create'; parsed['task'] = parse_task(cleaned)
        
    message['parsed'] = parsed
    return message

def preprocess(parsed_message, last_task):
    if last_task:
        parsed_message['last_task_id'] = last_task.task_id
    else:
        parsed_message['last_task_id'] = None
    return parsed_message