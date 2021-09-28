import sys
import json
import socket

class Client():

	def __init__(self):
		self.host = 'localhost'
		self.ip = 18000
		self.soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def call(self, args):
		self.soquete.connect((self.host, self.ip))
		self.soquete.send(json.dumps(args).encode())
		response = ''
		while True:
			part = self.soquete.recv(4096).decode('utf-8')
			response += part
			if len(part) < 4096:
				break;
		
		data = json.loads(response)
		self.soquete.close()
		return data