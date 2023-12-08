import typing


def is_empty(obj):
	if obj is None:
		return True
	elif type(obj) is str:
		return obj.isspace() or obj == ""
	elif isinstance(obj, typing.Sequence):
		return len(obj) == 0
	elif type(obj) is dict:
		if obj == {}:
			return True
		else:
			for value in obj.values():
				if not is_empty(value):
					return False
			return True
	else:
		return False
