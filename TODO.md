# TODO List

- [x] reinstall u18 for surface3
- [x] ~~deploy mongodb on the surface3(server)~~
- [x] install edge-browser on the surface3
- [x] deploy prometheus on surface3 to monitor the host
- [x] write the crawler for stock metadata
- [x] write the crawler for stock data
- [ ] write the crawler for daily tick trading event
- [ ] write the crawler for stock comments and news in "guba"
- [ ] write the crawler for stock reports(text)
- [ ] write the crawler for news and comment in weibo
- [x] deploy postgresql and create tables
- [x] find how to get the past kline data
- [ ] write `clean_all` log in `util.Log`
- [x] find out a management of  `id` of `Worker` and `Task` 
- [ ] check the validity for meta crawler
- [ ] check the validity for stocks quit from market


# Operation Log

- the cpu of surface3 doesn't support avx -> latest mongodb failed to start.(https://stackoverflow.com/questions/68742794/mongodb-failed-result-core-dump)

- prometheus expressions:
  - cpu util rate: `100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
  - mem util rate: `100 - ((node_memory_MemAvailable_bytes{instance="<your-instance>"} / node_memory_MemTotal_bytes{instance="<your-instance>"})) * 100`
  - disk util rate: `100 - (node_filesystem_avail_bytes{instance="<your-instance>", mountpoint="<your-mountpoint>"} / node_filesystem_size_bytes{instance="<your-instance>", mountpoint="<your-mountpoint>"}) * 100`

- deploy postgresql and create user: 
  - install on Ubuntu1804: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04
  - remote connection: https://zhuanlan.zhihu.com/p/467644334
  - role management: https://www.postgresqltutorial.com/postgresql-administration/postgresql-roles/
  - python driver: https://www.postgresqltutorial.com/postgresql-python/connect/

- fincance metrics:
  - turnover<成交额> = avg_price<平均成交价格> * (volume<成交量> * 100)
  - turnover_ratio<换手率> = volume / circulating_supply<流通总量>

  
# Comment

目前设计为，股票数据（包括股吧的股吧和研报）“离线抓取”，即仅在上午场结束和下午场结束后启动爬虫收集并更新数据，财报为每周一检测一次，收集并更新；
新闻及其评论数据为早上7点至晚上22点，每30分钟检测收集并更新一次。

