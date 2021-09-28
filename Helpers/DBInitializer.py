from Connection import Connection
from sqlite3 import Error

class DBInitializer():

	def __init__(self):
		self.connection = Connection().create()
		self.sqlCreateMovieTable = """ CREATE TABLE IF NOT EXISTS movie (
											id integer PRIMARY KEY AUTOINCREMENT,
											name text NOT NULL,
											year text
										); """
		self.sqlCreateParticipantTable = """ CREATE TABLE IF NOT EXISTS participant (
											id integer PRIMARY KEY AUTOINCREMENT,
											name text NOT NULL,
											role text NOT NULL
										); """
		self.sqlCreateMovieParticipantTable = """ CREATE TABLE IF NOT EXISTS movie_participant (
												id integer PRIMARY KEY AUTOINCREMENT,
												idMovie integer,
												idParticipant
											); """
		self.sqlCountMovieTableRows = ' SELECT count(id) AS total FROM movie; '
		self.sqlCountParticipantTableRows = ' SELECT count(id) AS total FROM participant; '
		self.sqlCountMovieParticipantTableRows = ' SELECT count(id) AS total FROM movie_participant; '

	def start(self):
		try:
			self.dropTables()
			self.createTables()
			if self.countMovieTableRows() == 0:
				self.insertIntoMovieTable()
			if self.countParticipantTableRows() == 0:
				self.insertIntoParticipantTable()
			if self.countMovieParticipantTableRows() == 0:
				self.insertIntoMovieParticipantTable()
		except Error as e:
			print(e)

	def dropTables(self):
		c = self.connection.cursor()
		c.execute('DROP TABLE IF EXISTS movie')
		c.execute('DROP TABLE IF EXISTS participant')
		c.execute('DROP TABLE IF EXISTS movie_participant')

	def createTables(self):
		c = self.connection.cursor()
		c.execute(self.sqlCreateMovieTable)
		c.execute(self.sqlCreateParticipantTable)
		c.execute(self.sqlCreateMovieParticipantTable)

	def countMovieTableRows(self):
		c = self.connection.cursor()
		c.execute(self.sqlCountMovieTableRows)
		return c.fetchone()[0]

	def countParticipantTableRows(self):
		c = self.connection.cursor()
		c.execute(self.sqlCountParticipantTableRows)
		return c.fetchone()[0]

	def countMovieParticipantTableRows(self):
		c = self.connection.cursor()
		c.execute(self.sqlCountMovieParticipantTableRows)
		return c.fetchone()[0]

	def getMovie(self, name, year):
		c = self.connection.cursor()
		c.execute(' SELECT id FROM movie WHERE name = "' + name + '" AND year = "' + year + '" ')
		return c.fetchone()[0]

	def insertIntoMovieTable(self):
		file = open('Helpers/movies.txt', 'r')

		sqlInsertMovie = ' INSERT INTO movie (name, year) VALUES '

		insertValues = []
		for movie in file:
			movie = movie.strip().split(',')
			name = movie[0] if len(movie) > 0 else ''
			year = movie[1] if len(movie) > 1 else 9999
			insertValues.append(' ("' + name.upper() + '", "' + year + '") ')

		sqlInsertMovie += ','.join(insertValues)

		try:
			c = self.connection.cursor()
			c.execute(sqlInsertMovie)
			self.connection.commit()
		except Error as e:
			print(e)

		file.close()

	def insertIntoParticipantTable(self):
		allDirectors, allActors = self.getDirectorsActorsFromFile()

		sqlInsertsParticipants = ' INSERT INTO participant (name, role) VALUES '

		if len(allDirectors):
			insertValues = []
			for director in allDirectors:
				insertValues.append(' ("' + director + '","' + "director" + '") ')
			sqlInsertsParticipants += ','.join(insertValues)

		if len(allActors):
			insertValues = []
			for actor in allActors:
				insertValues.append(' ("' + actor + '","' + "actor" + '") ')
			sqlInsertsParticipants += ',' + ','.join(insertValues)

		try:
			c = self.connection.cursor()
			c.execute(sqlInsertsParticipants)
			self.connection.commit()
		except Error as e:
			print(e)
		
	def getDirectorsActorsFromFile(self):
		file = open('Helpers/movies.txt', 'r')

		allDirectors = []
		allActors = []

		for movie in file:
			movie = movie.strip().split(',')
			self.getDirectorsActorsFromMovie(movie, allDirectors, allActors)
	
		file.close()

		return (allDirectors, allActors)

	def getDirectorsActorsFromMovie(self, line, allDirectors, allActors):
		directors = [line[2]] if len(line) > 2 else []
		actors = line[3:] if len(line) > 3 else []

		directorsLine = []
		actorsLine = []

		for director in directors.copy():
			if len(director):
				director = director.upper().strip()
				directorsLine.append(director)
				if director not in allDirectors:
					allDirectors.append(director)

		for actor in actors.copy():
			actor = actor.split('=')[0] # Remove nome do personagem
			if len(actor):
				isDirector = 'dir:' in actor.lower()
				actor = actor.replace('dir:', '').upper().strip()
				
				if isDirector:
					directorsLine.append(actor)
				else:
					actorsLine.append(actor)
				
				if isDirector and actor not in allDirectors:
					allDirectors.append(actor)
				elif not isDirector and actor not in allActors:
					allActors.append(actor)

		return (directorsLine, actorsLine)

	def insertIntoMovieParticipantTable(self):
		file = open('Helpers/movies.txt', 'r')

		allDirectors = []
		allActors = []

		sqlInsertMovieParticipant = ' INSERT INTO movie_participant (idMovie, idParticipant) VALUES '

		insertValues = []
		for movie in file:
			movie = movie.strip().split(',')

			name = movie[0] if len(movie) > 0 else ''
			name = name.upper()
			year = movie[1] if len(movie) > 1 else 9999

			idMovie = str(self.getMovie(name, year))

			directors, actors = self.getDirectorsActorsFromMovie(movie, allDirectors, allActors)
			if len(directors) or len(actors):
				for director in directors:
					insertValues.append(
						' ( ' +
						' ( ' + idMovie + ' ), ' +
						' (SELECT id FROM participant WHERE name = "' + director.upper() + '" AND role = "director") ' +
						' ) '
					)

				for actor in actors:
					insertValues.append(
						' ( ' +
						' ( ' + idMovie + ' ), ' +
						' (SELECT id FROM participant WHERE name = "' + actor.upper() + '" AND role = "actor") ' +
						' ) '
					)
		
		sqlInsertMovieParticipant += ','.join(insertValues)

		try:
			c = self.connection.cursor()
			c.execute(sqlInsertMovieParticipant)
			self.connection.commit()
		except Error as e:
			print(e)