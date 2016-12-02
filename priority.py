from datetime import datetime, timedelta
import random
import pytz
from config import LAMBDA, REFRESH_TIME

def prioritize(tasks):
    random.seed(2016)
    for task in tasks:
        task.priority = 0

        task.estimated_time = task.required_time if task.required_time != 0 else 1/10
        
        task.priority += 1 / (task.estimated_time + 1)

        if task.due:
            time_necessary = 5 * task.estimated_time * timedelta(minutes=30)
            time_remaining = task.due.replace(tzinfo=pytz.utc) - datetime.now(pytz.utc)
            if time_remaining < time_necessary:
                task.priority += 1
            else:
                task.priority += time_necessary / time_remaining

        #randomize
        task.priority += random.random()/100

        if datetime.now(pytz.utc) - task.last_notnow.replace(tzinfo=pytz.utc) < REFRESH_TIME:
            task.priority *= LAMBDA ** task.num_notnow

    return sorted(tasks, key = lambda p: p.priority, reverse = True)

def pick_one(tasks):
    if not tasks:
        return None
    prioritized = prioritize(tasks)
    return prioritized[0]