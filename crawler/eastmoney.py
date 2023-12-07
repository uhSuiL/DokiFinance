import re
import time
import json
import random
import requests
import numpy as np

from requests import HTTPError
from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from multiprocessing import Queue
from entity.service import Task

field = {
	'时间戳': 'f1',
	'最新价': 'f2',
	'涨跌幅': 'f3',
	'涨跌额': 'f4',
	'总手': 'f5',
	'成交额': 'f6',
	'振幅': 'f7',
	'换手率': 'f8',
	'市盈率': 'f9',
	'量比': 'f10',
	'5分钟涨跌幅': 'f11',
	'股票代码': 'f12',
	'市场': 'f13',
	'股票名称': 'f14',
	'最高价': 'f15',
	'最低价': 'f16',
	'开盘价': 'f17',
	'昨收': 'f18',
	'总市值': 'f20',
	'流通市值': 'f21',
	'涨速': 'f22',
	'市净率': 'f23',
	'60日涨跌幅': 'f24',
	'年初至今涨跌幅': 'f25',
	'上市日期': 'f26',
	'昨日结算价': 'f28',
	'现手': 'f30',
	'买入价': 'f31',
	'卖出价': 'f32',
	'委比': 'f33',
	'外盘': 'f34',
	'内盘': 'f35',
	'人均持股数': 'f36',
	'净资产收益率(加权)': 'f37',
	'总股本': 'f38',
	'流通股': 'f39',
	'营业收入': 'f40',
	'营业收入同比': 'f41',
	'营业利润': 'f42',
	'投资收益': 'f43',
	'利润总额': 'f44',
	'净利润': 'f129',
	'净利润同比': 'f46',
	'未分配利润': 'f47',
	'每股未分配利润': 'f48',
	'毛利率': 'f49',
	'总资产': 'f50',
	'流动资产': 'f51',
	'固定资产': 'f52',
	'无形资产': 'f53',
	'总负债': 'f54',
	'流动负债': 'f55',
	'长期负债': 'f56',
	'资产负债比率': 'f57',
	'股东权益': 'f58',
	'股东权益比': 'f59',
	'公积金': 'f60',
	'每股公积金': 'f61',
	'主力净流入': 'f62',
	'集合竞价': 'f63',
	'超大单流入': 'f64',
	'超大单流出': 'f65',
	'超大单净额': 'f66',
	'超大单净占比': 'f69',
	'大单流入': 'f70',
	'大单流出': 'f71',
	'大单净额': 'f72',
	'大单净占比': 'f75',
	'中单流入': 'f76',
	'中单流出': 'f77',
	'中单净额': 'f78',
	'中单净占比': 'f81',
	'小单流入': 'f82',
	'小单流出': 'f83',
	'小单净额': 'f84',
	'小单净占比': 'f87',
	'当日DDX': 'f88',
	'当日DDY': 'f89',
	'当日DDZ': 'f90',
	'5日DDX': 'f91',
	'5日DDY': 'f92',
	'10日DDX': 'f94',
	'10日DDY': 'f95',
	'DDX飘红天数(连续)': 'f97',
	'DDX飘红天数(5日)': 'f98',
	'DDX飘红天数(10日)': 'f99',
	'行业': 'f100',
	'板块领涨股': 'f128',
	'地区板块': 'f102',
	'备注': 'f103',
	'上涨家数': 'f104',
	'下跌家数': 'f105',
	'平家家数': 'f106',
	'每股收益': 'f112',
	'每股净资产': 'f113',
	'市盈率（静）': 'f114',
	'市盈率（TTM）': 'f115',
	'当前交易时间': 'f124',
	'市销率TTM': 'f130',
	'市现率TTM': 'f131',
	'总营业收入TTM': 'f132',
	'股息率': 'f133',
	'行业板块的成分股数': 'f134',
	'净资产': 'f135',
	'净利润TTM': 'f138',
	'更新日期': 'f221',
	'pre：盘前时间, after：盘后时间, period：盘中时间': 'f400'
}  # refer: https://blog.csdn.net/Scott0902/article/details/128715880


class CrawlMeta(Task):
	# refer: https://blog.csdn.net/qq_41335232/article/details/115514937

	page_url = "https://quote.eastmoney.com/center/gridlist.html#hs_a_board"

	# to fill: randint, timestamp, num_subpage, size, timestamp
	api = """https://%d.push2.eastmoney.com/api/qt/clist/get?"""  # randint
	"""cb=jQuery112401572233878044056_%d&"""  # timestamp
	"""pn=%d&pz=%d&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f3&"""  # num_page, size
	"""fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&"""
	f"""fields={field['股票代码']},{field['股票名称']},{field['市场']}&"""
	"""_=%d"""  # timestamp

	# TODO: 检查每一页返回的是否有重复——看能不能保证total=num_page*size
	def get_resp(self, num_page: int, size: int, request_config) -> requests.Response:
		now = int(time.time())
		api = self.api.format(random.randint(10, 99), now, num_page, size, now)  # TODO: 检查是否正常拼接
		resp = requests.get(api, **request_config)
		if resp.status_code != 200:
			raise HTTPError(f"get_resp@{self._id}: Invalid response, status code={resp.status_code}")
		return resp

	def parse_resp(self, resp) -> dict:
		match = re.search(r'\((.*?)\)', resp.content.decode(encoding='utf-8'))
		json_content = match.group(1)
		if json_content is None or json_content == "":
			raise ValueError(f"parse_resp@{self._id}: Empty content in resp")
		data = json.loads(json_content)
		return data

	def parse_data(self, data: dict) -> list:
		"""

		Args:
			data:

		Returns:

		"""
		data = data['data']
		if data is None:
			raise ValueError(f"parse_data@{self._id}: Empty data")
		data = data['diff']
		data = [list(record.values()) for record in data]
		return data  # stock_code, exchange_code, stock_name

	def run(self, data_queue: Queue, param_list: list[dict], request_config: dict = None):
		# param should be: [num_page: int, size: int]
		request_config = {} if request_config is None else request_config
		try:
			for param in param_list:
				resp = self.get_resp(**param, request_config=request_config)
				data = self.parse_resp(resp)
				data = self.parse_data(data)
				data_queue.put(("meta", "insert", data))
		except HTTPError or ValueError or UnicodeError:
			raise RuntimeError(f"""{self._id} Failed: """)


class CrawlKline(Task):

	@staticmethod
	def n_days_before(n: int) -> int:
		now = datetime.now()
		past_time = now - timedelta(days=n)
		return int(past_time.timestamp())

	# ATTENTION:
	# 	this api can only request limited data:
	# 		for k-5min:
	# 		for k-1min:
	# 	the duration is not decided by passed timestamp but the length of requested records

	# to fill<7>: randint, int_timestamp, int_exchange_code, stock_code, int_k, int_data_len, int_timestamp
	api = """https://%d.push2his.eastmoney.com/api/qt/stock/kline/get?"""  # randint
	f"""cb=jQuery35106627288987968145_%d&secid=%d.%d&"""  # int_timestamp, int_exchange_code, stock_code
	"""ut=fa5fd1943c7b386f172d6893dbfba10b&"""
	"""fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&"""
	"""klt=%d&fqt=1&end=20500101&lmt=%d&_=%d"""  # int_k, int_data_len, int_timestamp

	def get_resp(self, n: int, exchange_code: int, stock_code: int, k: int, data_len: int, request_config) -> requests.Response:
		int_timestamp = CrawlKline.n_days_before(n)
		api = CrawlKline.api.format(random.randint, int_timestamp, exchange_code, stock_code, k, data_len, int_timestamp)
		resp = requests.get(api, **request_config)
		if resp.status_code != 200:
			raise HTTPError(f"get_resp@{self._id}: Invalid response, status code={resp.status_code}")
		return resp

	def parse_resp(self, resp: requests.Response) -> dict:
		content = resp.content.decode(encoding='utf-8')
		match = re.search(r'\((.*?)\)', content)
		json_content = match.group(1)
		if json_content is None or json_content == "":
			raise ValueError(f"parse_resp@{self._id}: Empty content in resp")
		data = json.loads(json_content)
		return data

	use_col = list(range(7)) + [-1]

	def parse_data(self, data: dict) -> list:
		"""

		Args:
			data:

		Returns:

		"""
		k_lines: list[str] =  data['data']['kline']
		if k_lines is None:
			raise ValueError(f"parse_data@{self._id}: Empty data in {k_lines}")
		# [timestamp, start_price, close_price, high_price, low_price, volume<成交量/100>, turnover<成交额>,
		# amplitude_percentage<振幅%>, percentage_change_percentage<涨跌幅%>, price_change_percentage<涨跌额%>,
		# turnover_ratio_percentage<换手率%>]
		k_lines: np.ndarray = np.array([k_line.split(',') for k_line in k_lines])
		return k_lines[:, CrawlKline.use_col].tolist()

	def run(self, data_queue: Queue, param_list: list[dict], request_config: dict = None):
		# param should be [n, exchange_code, stock_code, k, data_len]
		request_config = {} if request_config is None else request_config
		try:
			for param in param_list:
				resp = self.get_resp(**param, request_config=request_config)
				data = self.parse_resp(resp)
				data = self.parse_data(data)
				data_queue.put(("kline", "insert", data))  # table_name, operation, data
		except HTTPError or ValueError or UnicodeError:
			raise RuntimeError(f"""{self._id} Failed: """)  # TODO: comment incomplete


class CrawlGubaTable(Task):

	guba_table_url = "https://guba.eastmoney.com/list,%d,99.html"  # to fill: stock_code

	def get_resp(self, stock_code: int, request_config: dict):
		url = self.guba_table_url.format(stock_code)
		resp = requests.get(url, **request_config)
		if resp.status_code != 200:
			raise HTTPError(f"get_resp@{self._id}: Invalid response, status code={resp.status_code}")
		return resp

	def parse_guba_table(self, html_text: str) -> dict:
		html = etree.HTML(html_text)
		if html is None:
			raise ValueError(f"get_resp@{self._id}: Empty data")

		# 分别爬取read, reply, title&data-postid&href, author&href, update
		# ATTENTION: 这里的爬取策略不是很安全
		nums_read = [elem.text for elem in html.xpath("//td/div[@class='read']")]
		nums_reply = [elem.text for elem in html.xpath("//td/div[@class='reply']")]
		update_times = [elem.text for elem in html.xpath("//td/div[@class='update']")]

		titles = [(elem.get("data-postid"), elem.get("href"), elem.text)
				  for elem in html.xpath("//td/div[@class='title']/a")]
		authors = [(elem.get("href"), elem.text) for elem in html.xpath("//td/div[@class='author']/a")]

		if not (len(nums_reply) == len(nums_read) == len(update_times) == len(titles) == len(authors)):
			raise ValueError(f"parse_guba_table@{self._id}: \
				length mismatch: {len(nums_read), len(nums_reply), len(update_times), len(titles), len(authors)}")

		return {
			'num_read': nums_read,
			'nums_reply': nums_reply,
			'titles': titles,
			'authors': authors
		}

	def parse_jquery(self, resp) -> dict:
		match = re.search(r'\((.*?)\)', resp.content.decode(encoding='utf-8'))
		json_content = match.group(1)
		if json_content is None or json_content == "":
			raise ValueError(f"parse_resp@{self._id}: Empty content in resp")
		data = json.loads(json_content)
		return data

	def run(self, params: list, request_config: dict = None):
		request_config = {} if request_config is None else request_config
		try:
			tables = []
			for param in params:
				resp = self.get_resp(*param, request_config=request_config)
				table = self.parse_guba_table(resp.text)
				tables.append(table)
			return tables  # 这里直接返回 -- 所有爬文章的任务都得等到获取了所有表才行
		except HTTPError or ValueError or UnicodeError:
			raise RuntimeError(f"""{self._id} Failed: """)  # TODO: comment incomplete


class CrawlArticle(Task):

	# 会有2种情况:
	# 	1. 评论reply太多时，需要“点击查看全部” -> https://guba.eastmoney.com/api/getData?code=300255&path=reply/api/Reply/ArticleReplyDetail
	# 	2. 评论reply内容太长时，需要“展开”
	# 	3. 评论可能需要翻页 -> get新的html即可
	# 	4. 评论reply太多时，需要翻页 -> 好像可以走api post拿到一条comment的所有reply
	# 	5. 评论太长需要“展开阅读全文”
	# 	6. 文本清洗：处理好emoji和各种引用（如@用户或股票）

	# 爬取逻辑
	# 	（爬帖子）
	# 	从股吧表获取信息: 阅读数量，评论数量，post_id，用户（，用户href）
	# 	构造出完整的消息页面（根据post_id）
	# 	检查是否需要“展开阅读全文”，如果需要，则交给driver点击后返回页面
	#	从页面中获取帖子文字内容，过滤表情包和@信息
	# 	---
	# 	（爬评论和评论的评论）

	# ATTENTION:
	# 	改爬"财富号"，好像不用传driver

	# comment_page = f"https://guba.eastmoney.com/news,{300255},{1375413310}.html"
	# TODO: 检查文章是否有需要翻页的

	def get_resp(self, href: str, request_config: dict) -> requests.Response:
		"""
			href: 来自guba_table的title里的href, 用于爬取article
		"""
		resp = requests.get(href, **request_config)
		if resp.status_code != 200:
			raise HTTPError(f"get_resp@{self._id}: Invalid response, status code={resp.status_code}")
		return resp

	def get_article(self, html_text: str) -> str:
		if html_text is None:
			raise ValueError(f"get_article@{self._id}: Empty html_text")

		# 可以直接过滤(转换)表情包和引用
		soup = BeautifulSoup(html_text, 'html.parser')
		article = ""
		for p in soup.find_all('p'):
			article += p.text + '\n'
		article = re.sub(r"\xa0", '', article)
		article = re.sub("\n本文作者可以追加内容哦 !\n\n\r", '', article)
		return article

	def run(self, hrefs: list, request_config: dict):
		request_config = {} if request_config is None else request_config
		try:
			for href in hrefs:
				...
		except HTTPError or ValueError or UnicodeError:
			raise RuntimeError(f"""{self._id} Failed: """)  # TODO: comment incomplete


class CrawlComment(Task):
	# TODO: 爬取post和它的comment，并把数据传给队列（用于传入数据库）

	def parse_jquery_text(self, jquery_text: str) -> str:
		match = re.search(r'\((.*?)\)', jquery_text)
		json_content = match.group(1)
		if json_content is None or json_content == "":
			raise ValueError(f"parse_jquery_text@{self._id}: Empty content in jquery_text")
		data = json.loads(json_content)
		return data

	def run(self, *args, **kwargs):
		...
