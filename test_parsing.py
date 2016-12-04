from parse import parse_message, parse_task, matching

assert matching('sample task 1d~6d') == {'content': 'sample task', 'due': '6d', 'required_time': None, 'scheduled': '1d'}, matching('sample task 1d~6d')

assert matching('task ~ 6d') == {'content': 'task', 'due': '6d', 'required_time': None, 'scheduled': None}

assert matching('sample task today ~ tmr') == {'content': 'sample task',
 'due': 'tmr',
 'required_time': None,
 'scheduled': 'today'}

assert matching('task tdy ~') == {'content': 'task', 'due': None, 'required_time': None, 'scheduled': 'tdy'}

assert matching('task 3 ~ x') == {'content': 'task', 'due': 'x', 'required_time': '3', 'scheduled': None}, matching('task 3 ~ x')

assert matching('task 3 ~ 1d') == {'content': 'task', 'due': '1d', 'required_time': '3', 'scheduled': None}

assert matching('task2 ~ 2d') == {'content': 'task2', 'due': '2d', 'required_time': None, 'scheduled': None}

assert matching('task') == {'content': 'task', 'due': None, 'required_time': None, 'scheduled': None}, matching('task')

assert matching('task2 3') == {'content': 'task2', 'due': None, 'required_time': '3', 'scheduled': None}

assert matching('3') == {'scheduled': None, 'due': None, 'required_time': '3'}, matching('3')

assert matching('2 ~ 2d') == {'due': '2d', 'required_time': '2', 'scheduled': None}