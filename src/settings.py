config = {
    "db_host": "127.0.0.1",
    "db_port": "5432",
    "db_password": "postgres",
    "db_username": "postgres",
    "db_name": "imdb"
}

file_locations = {
    "movies": '/Users/ADINSX/IMDB_DATA/movies.list',
    "actors": '/Users/ADINSX/IMDB_DATA/actors.list',
    "actress": '/Users/ADINSX/IMDB_DATA/actresses.list',
    "directors": '/Users/ADINSX/IMDB_DATA/directors.list',
    "genres": '/Users/ADINSX/IMDB_DATA/genres.list',
    "ratings": '/Users/ADINSX/IMDB_DATA/ratings.list'
}

def get_connection_string():
    return "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (config['db_host'],
                                                                        config['db_port'],
                                                                        config['db_name'],
                                                                        config['db_username'],
                                                                        config['db_password'])