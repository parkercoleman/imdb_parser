from src.parsers import *
from src.parsers.base_parser import *



"""
RegExp: /\s*(\S*)\s*(\S*)\s*(\S*)\s*((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)$/gm
pattern: \s*(\S*)\s*(\S*)\s*(\S*)\s*((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)$
flags: gm
10 capturing groups:
    group 1: (\S*)                               distribution
    group 2: (\S*)                               votes
    group 3: (\S*)                               rank
    group 4: #TITLE (UNIQUE KEY)
    group 5: (.*? \(\S{4,}\))                    movie name + year
    group 6: (\(.+\))                            type ex:(TV)
    group 7: (\{(.*?)\s?(\(.+?\))\})             series info ex: {Ally Abroad (#3.1)}
    group 8: (.*?)                               episode name ex: Ally Abroad
    group 9: (\(.+?\))                           episode number ex: (#3.1)
    group 10: (\{\{SUSPENDED\}\})                is suspended?
"""

# properties
base_matcher_pattern = "\s*(\S*)\s*(\S*)\s*(\S*)\s*((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)$"
SKIP_LINE = 28


class RatingsParser(BaseParser):
    def __init__(self, genres_file):
        self.ratings_file = genres_file
        self.db_connection = None

    def parse_all(self):
        self.db_connection = psycopg2.connect(get_connection_string())
        self.generic_parse_all(self.ratings_file,
            SKIP_LINE, base_matcher_pattern, self.match_line_impl)

        self.db_connection.close()

    def match_line_impl(self, line_match):
        entity_name = line_match.groups()[3]

        entity_name = convert_latin1(entity_name)
        rs = execute_sql_select(self.db_connection, "SELECT id FROM performances WHERE raw LIKE %s",
                                [entity_name + "%"])

        if len(rs) >= 1:
            execute_sql(self.db_connection,
                        "INSERT INTO ratings VALUES(%s, %s, %s)",
                        [rs[0]["id"], line_match.group(2), line_match.group(3)])

        else:
            #Might be an entry for a specific episode
            rs = execute_sql_select(self.db_connection, "SELECT id FROM tv_episodes WHERE raw LIKE %s",
                                    [entity_name + "%"])
            if len(rs) >= 1:
                execute_sql(self.db_connection,
                            "INSERT INTO ratings VALUES(%s, %s, %s)",
                            [rs[0]["id"], line_match.group(2), line_match.group(3)])

if __name__ == '__main__':
    r = RatingsParser(file_locations["ratings"])
    r.parse_all()