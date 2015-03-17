from src.parsers import *
from src.parsers.base_parser import *
from src.parsers.movie_parser import MovieParser


"""
RegExp: /((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\t+(.*)$/gm
pattern: ((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\t+(.*)$
flags: gm
8 capturing groups:
    group 1: #TITLE (UNIQUE KEY)
    group 2: (.*? \(\S{4,}\))                    movie name + year
    group 3: (\(\S+\))                           type ex:(TV)
    group 4: (\{(.*?) ?(\(\S+?\))?\})            series info ex: {Ally Abroad (#3.1)}
    group 5: (.*?)                               episode name ex: Ally Abroad
    group 6: ((\(\S+?\))                         episode number ex: (#3.1)
    group 7: (\{\{SUSPENDED\}\})                 is suspended?
    group 8: (.*)                                genre
"""

# properties
base_matcher_pattern = "((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\t+(.*)$"
SKIP_LINE = 381


class GenresParser(BaseParser):
    def __init__(self, genres_file):
        self.genres_file = genres_file
        self.db_connection = None

    def parse_all(self):
        self.db_connection = psycopg2.connect(get_connection_string())
        self.generic_parse_all(self.genres_file,
            SKIP_LINE, base_matcher_pattern, self.match_line_impl)

        self.db_connection.close()

    def match_line_impl(self, line_match):
        entity_name = convert_latin1(line_match.groups()[-8])
        rs = execute_sql_select(self.db_connection, "SELECT id FROM performances WHERE raw LIKE %s",
                                [entity_name + "%"])

        if len(rs) == 1:
            execute_sql(self.db_connection,
                        "INSERT INTO genres VALUES(%s, %s)",
                        [rs[0]["id"], line_match.group(8)])

        else:
            #Might be an entry for a specific episode
            rs = execute_sql_select(self.db_connection, "SELECT id FROM tv_episodes WHERE raw LIKE %s",
                                    [entity_name + "%"])
            if len(rs) == 1:
                execute_sql(self.db_connection,
                            "INSERT INTO genres VALUES(%s, %s)",
                            [rs[0]["id"], line_match.group(8)])

if __name__ == '__main__':
    g = GenresParser(file_locations["genres"])
    g.parse_all()