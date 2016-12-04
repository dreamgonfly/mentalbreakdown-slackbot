from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import pytz
from config import DB, TIMEZONE

Base = declarative_base()

class Task(Base):
	__tablename__ = 'Task'
	task_id = Column(Integer, primary_key=True)
	team_id = Column(String(9))
	channel_id = Column(String(9))
	user_id = Column(String(9))
	interface_id = Column(Integer)
	content = Column(String(150))
	required_time = Column(Integer, default=1)
	scheduled = Column(DateTime)
	due = Column(DateTime)
	active = Column(Boolean, default=True)
	doable = Column(Boolean, default=True)
	completed = Column(Boolean, default=False)
	completed_time = Column(DateTime)
	completed_ts = Column(String(20))
	deleted = Column(Boolean, default=False)
	deleted_time = Column(DateTime)
	deleted_ts = Column(String(20))
	last_notnow = Column(DateTime)
	num_notnow = Column(Integer, default=0)
	created_time = Column(DateTime)
	created_ts = Column(String(20))
	last_updated_time = Column(DateTime)
	last_updated_ts = Column(String(20))
	raw_text = Column(String(200))

	def __init__(self, *args, **kwargs):
		Base.__init__(self, *args, **kwargs)
		self.last_notnow = datetime.min
		self.created_time = datetime.now(pytz.utc)
		self.last_updated_time = datetime.now(pytz.utc)

	def __repr__(self):
		def time_repr(t_utc):
			print(t_utc)
			if not t_utc:
				return ''
			t = pytz.utc.localize(t_utc).astimezone(TIMEZONE)
			now = datetime.now(TIMEZONE)
			tomorrow = now + timedelta(1)
			if t.date() == now.date(): day = 'today'
			elif t.date() == tomorrow.date(): day = 'tomorrow'
			else: day = t.strftime('%b %d %A')

			if t.strftime('%H:%M') == '23:59': time = None
			else: time = t.strftime('%H:%M')
			return day + ' ' + time if time else day

		def time_padding(t_utc):
			timestring = time_repr(t_utc)
			if timestring:
				return ' ' + timestring
			else: return timestring

		if not self.scheduled and not self.due:
			return '({self.task_id}) {self.content} *{self.required_time}*'.format(self=self)
		else:
			return '({self.task_id}) {self.content} *{self.required_time}*{scheduled} ~{due}'.format(self=self, 
				scheduled=time_padding(self.scheduled),
				due=time_padding(self.due))
			
	# @staticmethod
	# def active_tasks():
	# 	return Task.query.filter_by(active=True).filter(or_(Task.scheduled == None, Task.scheduled < datetime.now()))

#     @staticmethod
#     def pick_one():
#     	return pick_one(Task.active_tasks().all())

class Arrow(Base):
	__tablename__ = 'Arrow'
	arrow_id = Column(Integer, primary_key=True)
	source_id = Column(Integer)
	target_id = Column(Integer)
	created_time = Column(DateTime)
	created_ts = Column(String(20))

	def __init__(self, *args, **kwargs):
		Base.__init__(self, *args, **kwargs)
		self.created_time = datetime.now()

engine = create_engine(DB, echo=False)
Base.metadata.create_all(engine)
