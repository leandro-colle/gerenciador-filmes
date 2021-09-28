import sqlite3
from sqlite3 import Error

class Connection:

	def __init__(self):
		self.dbFile = r"db/database.db"
		self.conn = None

	def create(self):
		try:
			self.conn = sqlite3.connect(self.dbFile)
		except Error as e:
			print(e)

		return self.conn