from entity.service import Task, Register
from util.service import get_config, Log
from multiprocessing import Queue


class Foo(Task):
	def run(self, test_info):
		for i in range(1000):
			print("Hello")
		return test_info


def test_config():
	config = get_config('../config')
	assert len(config.keys()) == 3
	print(config)


def test_task1():
	config = get_config('../config')
	logger = Log.get_logger(config['service']['logger'])
	queue = Queue()
	foo = Foo(queue)
	assert 'aaa' == foo('aaa')
