import sys
import json
import socket
from Connection import Connection
from Services import Services

# python3 server.py <porta>

class Server():

	def __init__(self):
		self.host = 'localhost'
		self.ip = None
		self.soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def init(self, args):
		if len(args) != 2:
			print('%s <port>' % args[0])
			sys.exit(0)
		else:
			self.ip = int(args[1])
			self.soquete.bind((self.host, self.ip))
			self.soquete.listen(10)

			while True:
				s, client = self.soquete.accept()
				data = s.recv(4096).decode('utf-8')
				data = json.loads(data) 
				s.send(
					json.dumps(
						Services(data['action'], data['params']).execute()
					).encode()
				)
				s.close()

			self.soquete.close()

if __name__ == '__main__':
	Server().init(sys.argv)



