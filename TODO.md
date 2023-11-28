# TODO List

- [x] reinstall u18 for surface3
- [x] ~~deploy mongodb on the surface3(server)~~
- [x] install edge-browser on the surface3
- [x] deploy prometheus on surface3 to monitor the host
- [ ] write the crawler for stock data
- [ ] write the crawler for news and comment in weibo
- [x] deploy postgresql and create tables
- [ ] find how to get the past kline data


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