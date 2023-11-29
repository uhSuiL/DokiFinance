import abc
import time
import logging

from multiprocessing import Queue, Value, Lock
from typing import Callable


class Register(dict):
	def __init__(self, *args, **kwargs):
		super(Register, self).__init__(*args, **kwargs)
		self.__name = None

	def register(self, func: Callable):
		if not callable(func):
			raise Exception(f"`{func}: {type(func)}` is not callable.")

		name = self.__name if self.__name is not None else func.__name__
		if name in self.keys():
			raise Exception(f"function `{name}` has been registered.")

		self[name] = func
		self.__name = None
		return func

	# def wrapper(self, *args, **kwargs):
	# 	return self.__func(*args, **kwargs)

	def __call__(self, target: str = None):
		if type(target) is str:
			self.__name = target
			return self.register
		elif target is None:
			return self.register
		else:
			raise Exception("Undefined Behavior on register")


class Task(abc.ABC):

	instance_count = Value('i', 0)
	instance_count_lock = Lock()

	@classmethod
	def count_instance(cls):
		with cls.instance_count_lock:
			return cls.instance_count.value

	def __init__(self, msg_queue: Queue, callbacks: list[Callable] = None):
		"""Task (Function)

			We recommend using callable object to replace pure function for long-time task.
			Task can auto record the start, end, error of a task, and put it to Manager for log
		"""
		self.queue = msg_queue
		with Task.instance_count_lock:
			self._id = self.__class__.__name__ + '_' + str(Task.instance_count.value)
			Task.instance_count.value += 1

		if callbacks is not None:
			i = 0
			for func in callbacks:
				if not callable(func):
					raise Exception(f"{i}th callback for {self._id} is not callable")
				i += 1

		self.callbacks: list[Callable] = callbacks

	def __call__(self, *args, **kwargs):
		self.queue.put((logging.INFO, f"Start Task {self._id}"))
		start = time.time()
		try:
			result = self.run(*args, **kwargs)
			end = time.time()
			self.queue.put((logging.INFO, f"Finish Task {self._id} in {end - start: .3f}s"))
		except Exception as e:
			end = time.time()
			self.queue.put((logging.ERROR,
			f"""ERROR happens in Task {self._id} after {end - start: .3f}s
				{e}
			""", e))
			raise e

		if self.callbacks is not None:
			for func in self.callbacks:
				func(result)

		return result

	def run(self, *args, **kwargs):
		raise NotImplementedError


class Worker(abc.ABC):

	instance_count = Value('i', 0)
	instance_count_lock = Lock()

	@classmethod
	def count_instance(cls):
		with cls.instance_count_lock:
			return cls.instance_count.value

	task_list: list

	def __init__(self, queue: Queue, config: dict):
		self.queue = queue
		self.config = config

		with Worker.instance_count_lock:
			self._id = self.__class__.__name__ + '_' + Worker.instance_count.value
			Worker.instance_count.value += 1

	def __call__(self, *args, **kwargs):
		...

	def start(self):
		raise NotImplementedError


class Manager:
	def __init__(self):
		...
