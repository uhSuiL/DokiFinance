from entity.service import Register

foo_register = Register()


@foo_register()
def foo1(aaa):
	print("foo1")
	return aaa


@foo_register("foo2")
def foo2(aaa):
	print("foo2")
	return aaa


def test_register():
	print(foo_register)
	assert foo_register['foo1'] == foo1
	aaa = "aaa"
	assert aaa == foo_register['foo1'](aaa)

