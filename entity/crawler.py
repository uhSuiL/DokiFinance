import re
import json
import requests
from requests import HTTPError
from entity.service import Task


class Crawler(Task):
	def get_resp(self, url: str, request_config: dict):
		resp = requests.get(url, **request_config)
		if resp.status_code != 200:
			raise HTTPError(f"get_resp@{self._id}: Invalid response, status code={resp.status_code}")
		return resp

	def parse_jquery_text(self, jquery_text: str) -> dict:
		match = re.search(r'\((.*?)\)', jquery_text)
		json_content = match.group(1)
		if json_content is None or json_content == "":
			raise ValueError(f"parse_jquery_text@{self._id}: Empty content in jquery_text")
		data = json.loads(json_content)
		return data

	def run(self, *args, **kwargs):
		try:
			return self.crawl()
		except HTTPError or ValueError or UnicodeError:
			raise RuntimeError(f"""{self._id} Failed: """)  # TODO: comment incomplete

	def crawl(self):
		raise NotImplementedError
