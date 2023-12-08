from util.crawl import is_empty


def test_is_empty():
	assert is_empty({'a': {}, 'b': [], 'c': (()), 'd': None})
