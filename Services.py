from Connection import Connection

class Services():

	def __init__(self, action, params):
		self.action = action
		self.params = params
		self.result = []

	def execute(self):
		if self.action == 'list-participants':
			self.listParticipants(self.params)
		if self.action == 'list-movies':
			self.listMovies(self.params)
		if self.action == 'list-partner-actors':
			self.listPartnerActors(self.params)
		if self.action == 'list-duplicated-movies':
			self.listDuplicatedMovies()
		if self.action == 'insert-movie':
			self.insertMovie(self.params)
		if self.action == 'delete-movie':
			self.deleteMovie(self.params)

		return self.result
	
	def listParticipants(self, params):
		connection = Connection().create()
		c = connection.cursor()

		sql = (' SELECT p.id, p.name FROM participant AS p ')

		if 'name' in params:
			sql += ' WHERE ' if 'WHERE' not in sql else ' AND '
			sql += ' p.name = "' + params['name'] + '" '

		if 'role' in params:
			sql += ' WHERE ' if 'WHERE' not in sql else ' AND '
			sql += ' p.role = "' + params['role'] + '" '

		if 'assortment' in params:
			sql += ' ORDER BY p.name ' + params['assortment'] + ' '
		else:
			sql += ' ORDER BY p.name asc '

		c.execute(sql)
		participants = c.fetchall()
		self.result = []
		for participant in participants:
			self.result.append({
				'id': participant[0],
				'name': participant[1]
			})

	def listPartnerActors(self, params):
		self.listMovies(params);
		if len(self.result) > 0:
			idsMovies = []
			for r in self.result:
				idsMovies.append(str(r['id']))

			connection = Connection().create()
			c = connection.cursor()

			sql = (
				' SELECT p.name AS participant, m.name AS movie FROM participant p ' +
				' JOIN movie_participant mp ON mp.idParticipant = p.id ' +
				' JOIN movie m ON m.id = mp.idMovie ' +
				' WHERE m.id IN (' + ','.join(idsMovies) + ') ' +
				' AND p.role = "actor" '
			)

			if 'actor' in params:
				sql += ' AND p.name != "' + params['actor'].upper() + '" '
			elif 'director' in params:
				sql += ' AND p.name != "' + params['director'].upper() + '" '

			c.execute(sql)
			actors = c.fetchall();
			self.result = []
			for actor in actors:
				self.result.append({
					'actor': actor[0],
					'movie': actor[1]
				})

	def listMovies(self, params):
		connection = Connection().create()
		c = connection.cursor()

		sql = (
			' SELECT m.id, m.name, m.year FROM movie AS m ' +
			' LEFT JOIN movie_participant AS mp ON mp.idMovie = m.id ' +
			' LEFT JOIN participant AS p ON p.id = mp.idParticipant '
		)

		if 'name' in params:
			sql += ' WHERE ' if 'WHERE' not in sql else ' AND '
			sql += ' m.name = "' + params['name'].upper() + '" '

		if 'year' in params and params['year'] != 9999:
			sql += ' WHERE ' if 'WHERE' not in sql else ' AND '
			sql += ' m.year = "' + str(params['year']) + '" '

		if 'actor' in params:
			sql += ' WHERE ' if 'WHERE' not in sql else ' AND '
			sql += ' p.name = "' + params['actor'].upper() + '" AND p.role = "actor" '

		if 'director' in params:
			sql += ' WHERE ' if 'WHERE' not in sql else ' AND '
			sql += ' p.name = "' + params['director'].upper() + '" AND p.role = "director" '

		sql += ' GROUP BY m.id '

		if 'assortment' in params:
			sql += ' ORDER BY m.name ' + params['assortment'] + ' '
		else:
			sql += ' ORDER BY m.year asc '

		c.execute(sql)
		movies = c.fetchall()
		self.result = []
		for movie in movies:
			self.result.append({
				'id': movie[0],
				'name': movie[1],
				'year': movie[2]
			})

	def listDuplicatedMovies(self):
		connection = Connection().create()
		c = connection.cursor()

		sql = (' SELECT name, year FROM movie GROUP BY name, year HAVING COUNT(*) >= 2 ')

		c.execute(sql)
		movies = c.fetchall()
		for movie in movies:
			self.result.append({
				'name': movie[0],
				'year': movie[1]
			})

	def insertMovie(self, params):
		self.listMovies(params);
		if len(self.result) > 0:
			self.result = {'erro': 'Este filme já está cadastrado.'}
		else:
			connection = Connection().create()
			c = connection.cursor()

			name = params['name'].upper()
			year = params['year'] if params['year'] != "" else 9999
			sql = (' INSERT INTO movie(name, year) VALUES("' + name + '", "' + str(year) + '") ')
			c.execute(sql)

			sql = (' SELECT last_insert_rowid(); ')
			c.execute(sql)
			idMovie = c.fetchone()[0]

			participants = []
			if idMovie > 0:
				if 'actors' in params:
					for actor in params['actors'].split(','):
						participants.append({
							'name': actor.strip().upper(),
							'role': 'actor'
						})
				if 'directors' in params:
					for director in params['directors'].split(','):
						participants.append({
							'name': director.strip().upper(),
							'role': 'director'
						})

				for participant in participants:
					self.listParticipants({
						'name': participant['name'],
						'role': participant['role']	
					})

					if len(self.result) > 0:
						idParticipant = self.result[0]['id']
					else:
						sql = (' INSERT INTO participant(name, role) VALUES("' + participant['name'].upper() + '", "' + participant['role'] + '") ')
						c.execute(sql)

						sql = (' SELECT last_insert_rowid(); ')
						c.execute(sql)
						idParticipant = c.fetchone()[0]

					sql = (' INSERT INTO movie_participant(idMovie, idParticipant) VALUES("' + str(idMovie) + '", "' + str(idParticipant) + '") ')
					c.execute(sql)

			connection.commit()

	def deleteMovie(self, params):
		self.listMovies(params);
		if len(self.result) == 0:
			self.result = {'erro': 'Este filme não está cadastrado.'}
		else:
			connection = Connection().create()
			c = connection.cursor()

			sql = (
				' DELETE FROM movie ' +
				' WHERE name = "' + params['name'].upper() + '" '
			)
			if 'year' in params and params['year'] != 9999:
				sql += ' AND year = "' + str(params['year']) + '" '
			c.execute(sql)

			sql = (
				' DELETE FROM movie_participant ' +
				' WHERE idMovie = "' + str(self.result[0]['id']) + '" '
			)
			c.execute(sql)

			connection.commit()
			
