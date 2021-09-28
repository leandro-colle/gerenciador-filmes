import os
import sys
from Client import Client
from Helpers.DBInitializer import DBInitializer

def main(args):

	# Descomentar para resetar o banco de dados
	# initializer = DBInitializer();
	# initializer.start();

	os.system('cls||clear')

	action = args[1] if len(args) > 1 else ''
	params = args[2:] if len(args) > 2 else ['']

	if action == '--help' or action == '-h':
		print('-- MENU --')
		print('1 - Listar todos os atores: [<option> <desc|asc>]')
		print('2 - Listar filmes por ator: [<option> "<actor>"]')
		print('3 - Listar todos os filmes: [<option> <desc|asc>]')
		print('4 - Inserir filme: [<option> "<name>" <year> "<actors, ...>" "<directors, ...>"]')
		print('5 - Remover filme: [<option> "<name>" <year>]')
		print('6 - Listar filmes por diretor: [<option> "<director>"]')
		print('7 - Listar atores coadjuvantes: [<option> "<actor>"]')
		print('8 - Listar atores coadjuvantes: [<option> "<director>"]')
		print('9 - Listar filmes duplicados [<option>]')
		sys.exit(0)

	if action == '1' and params[0] in ['desc', 'asc']:
		response = Client().call({
			'action': 'list-participants',
			'params': {'role': 'actor', 'assortment': params[0]}
		});
		for r in response:
			del r['id']
			print('%s' % r)
	elif action == '2' and len(params) > 0:
		response = Client().call({
			'action': 'list-movies',
			'params': {'actor': params[0].upper()}
		});
		for r in response:
			del r['id']
			print('%s' % r)
	elif action == '3' and params[0] in ['desc', 'asc']:
		response = Client().call({
			'action': 'list-movies',
			'params': {'assortment': params[0]}
		});
		for r in response:
			del r['id']
			print('%s' % r)
	elif action == '4' and len(params) > 0:
		response = Client().call({
			'action': 'insert-movie',
			'params': {
				'name': params[0],
				'year': params[1] if len(params) > 1 else 9999,
				'actors': params[2] if len(params) > 2 else '',
				'directors': params[3] if len(params) > 3 else '',
			}
		});
		if 'erro' in response:
			print(response['erro'])
	elif action == '5' and len(params) > 0:
		response = Client().call({
			'action': 'delete-movie',
			'params': {
				'name': params[0],
				'year': params[1] if len(params) > 1 else 9999,
			}
		});
		if 'erro' in response:
			print(response['erro'])
	elif action == '5' and len(params) > 0:
		response = Client().call({
			'action': 'delete-movie',
			'params': {
				'name': params[0]
			}
		});
		if 'erro' in response:
			print(response['erro'])
	elif action == '6' and len(params) > 0:
		response = Client().call({
			'action': 'list-movies',
			'params': {'director': params[0].upper()}
		});
		for r in response:
			del r['id']
			print('%s' % r)
	elif action == '7' and len(params) > 0:
		response = Client().call({
			'action': 'list-partner-actors',
			'params': {'actor': params[0].upper()}
		});
		for r in response:
			print('%s' % r)
	elif action == '8' and len(params) > 0:
		response = Client().call({
			'action': 'list-partner-actors',
			'params': {'director': params[0].upper()}
		});
		for r in response:
			print('%s' % r)
	elif action == '9':
		response = Client().call({
			'action': 'list-duplicated-movies',
			'params': {}
		});
		for r in response:
			print('%s' % r)
	else:
		print('Parâmetros inválidos. Utilize --help para ver as opções disponíveis.')

if __name__ == '__main__':
	main(sys.argv)