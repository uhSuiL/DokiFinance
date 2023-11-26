import logging

from pymongo import MongoClient
from logging.handlers import BaseRotatingHandler


class DataBaseHandler(logging.Handler):
	# Refer: https://geek-docs.com/python/python-ask-answer/287_python_python_logging_to_database.html
	def __init__(self, conn, log_table: str = "log"):
		super().__init__()

		# Create log_table in the connected database
		# the field will compulsively be: id, level, message, create_time
		cursor = conn.cursor()
		cursor.execute(f"""
		CREATE TABLE IF NOT EXISTS {log_table} (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			level VARCHAR(10),
			message TEXT,
			create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		""")
		cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_create_time ON {log_table} (create_time)")
		conn.commit()
		# conn.close()

		self.connection = conn
		self.log_table = log_table

	def emit(self, record):
		self.connection.execute(
			f"INSERT INTO {self.log_table} (level, message) VALUES (?, ?)",
			(record.levelname, record.getMessage())
		)
		self.connection.commit()
		# self.connection.close()
