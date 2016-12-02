from db import Task, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from datetime import datetime, timedelta
from priority import prioritize, pick_one
from config import REFRESH_TIME
Session = sessionmaker(bind=engine)
session = Session()

def active_tasks():
    result = session.query(Task).filter_by(active=True).filter(or_(Task.scheduled == None, Task.scheduled < datetime.now())).all()
    return result

def get_one(parsed_message):
    if 'id' in parsed_message['parsed']:
        return session.query(Task).get(parsed_message['parsed']['id'])
    else: return pick_one(active_tasks())

def execute_command(parsed_message):
    executions = {'next': next_task,
    'create': create, 
    'complete': complete, 
    'list': listing,
    'delete': delete,
    'postpone': postpone,
    'top hour': top_hour,
    'update': update
    }
    return executions[parsed_message['parsed']['command']](parsed_message)

def next_task(parsed_message):
    return str(pick_one(active_tasks()))

def create(parsed_message):
    task = Task(**parsed_message['parsed']['task'])
    task.raw_text = parsed_message['text']
    task.team_id = parsed_message['team']
    task.channel_id = parsed_message['channel']
    task.user_id = parsed_message['user']
    task.created_ts = parsed_message['ts']
    session.add(task)
    session.commit()
    return "New task : {task}".format(task=str(task))

def complete(parsed_message):
    task = get_one(parsed_message)
    task.completed = True
    task.completed_time = datetime.now()
    task.completed_ts = parsed_message['ts']
    task.active = False
    session.commit()
    return "Completed : {task}".format(task=str(task))

def listing(parsed_message):
    size = parsed_message['parsed']['size'] if 'size' in parsed_message['parsed'] else 5
    tasks = active_tasks()[:size]
    return '\n'.join([str(task) for task in tasks])

def delete(parsed_message):
    task = get_one(parsed_message)
    task.deleted = True
    task.deleted_time = datetime.now()
    task.deleted_ts = parsed_message['ts']
    task.active = False
    session.commit()
    return "Deleted : {task}".format(task=str(task))

def postpone(parsed_message):
    task = get_one(parsed_message)
    if datetime.now() > REFRESH_TIME + task.last_notnow:
        task.num_notnow = 0
    task.num_notnow +=1
    task.last_notnow = datetime.now()
    session.commit()
    return "Postponed : {task}".format(task=str(task))

def top_hour(parsed_message):
    now = datetime.now()
    next_hour = now + timedelta(hours=1)
    next_top_hour = datetime(next_hour.year, next_hour.month, next_hour.day, next_hour.hour)
    time_remaining = next_top_hour - now
    tasks_to_do = []; total_required_time = 0
    for task in prioritize(active_tasks()):
        total_required_time += task.required_time
        if total_required_time * timedelta(minutes=30) > time_remaining:
            break
        tasks_to_do.append(task)
    return '{} minutes remaining\n'.format(time_remaining.seconds//60) + '\n'.join([str(task) for task in tasks_to_do])

from operator import attrgetter
def update(parsed_message):
    task = get_one(parsed_message)
    update_task = parsed_message['parsed']['task']
    if 'content' in update_task and update_task['content'] != '.':
        task.content = update_task['content']
    if 'required_time' in update_task: task.required_time = update_task['required_time']
    if 'scheduled' in update_task: task.scheduled = update_task['scheduled']
    if 'due' in update_task: task.due = update_task['due']
    task.last_updated_time = datetime.now()
    task.last_updated_ts = parsed_message['ts']
    task.raw_text = parsed_message['text']
    session.commit()
    return "Updated : {task}".format(task=str(task))