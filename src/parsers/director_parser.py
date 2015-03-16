__author__ = 'parker'


from src.parsers.base_parser import BaseParser
from src.parsers import *


director_matcher_pattern = '(.*?)\t+((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\s*(\(.*\)|EDIT)?\s*(<.*>)?$'
"""
RegExp: /(.*?)\t+((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\s*(\(.*\)|EDIT)?\s*(<.*>)?$/gm
pattern: (.*?)\t+((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\s*(\(.*\)|EDIT)?\s*(<.*>)?$
flags: gm
10 capturing groups:
    group 1: (.*?)                               surname, name
    group 2: #TITLE (UNIQUE KEY)
    group 3: (.*? \(\S{4,}\))                    movie name + year
    group 4: (\(\S+\))                           type ex:(TV)
    group 5: (\{(.*?) ?(\(\S+?\))?\})            series info ex: {Ally Abroad (#3.1)}
    group 6: (.*?)                               episode name ex: Ally Abroad
    group 7: (\(\S+?\))                          episode number ex: (#3.1)
    group 8: (\{\{SUSPENDED\}\})                 is suspended?
    group 9: (\(.*\))                            info
    group 10: ()
"""

SKIP_LINE = 235
import uuid

class DirectorParser(BaseParser):
    def __init__(self, director_file):
        self.director_file = director_file
        self.db_connection = None

    def parse_all(self):
        self.db_connection = psycopg2.connect(get_connection_string())
        self.generic_parse_all(self.director_file,
            SKIP_LINE, director_matcher_pattern, self.match_line_impl)

        self.db_connection.close()

    def match_line_impl(self, line_match):
        if line_match.group(1) is not None and line_match.group(1) != '':
            #This is a director line, we need to insert a new director
            self.current_uuid = self.insert_director(line_match)

        #Regardless of if this is a director line, we need to insert the performance
        self.insert_performance_from_match(line_match)

    def insert_director(self, match):
        ''' Inserts a director and returns the generated uuid for that performer.
        :param match:
        :param gender:
        :return:
        '''
        first_name, last_name = BaseParser.clean_person_name(match.group(1))
        director_id = str(uuid.uuid4())
        sql = "INSERT INTO directors(id, first_name, last_name) VALUES(%s, %s, %s)"
        args = [director_id, convert_latin1(first_name), convert_latin1(last_name)]
        execute_sql(self.db_connection, sql, args)
        return director_id

    def insert_performance_from_match(self, match):
        performance_uuid, tv_show_uuid, role, billing = BaseParser.get_performance_information_from_match(self.db_connection, match)
        if performance_uuid is None:
            return
        sql = "INSERT INTO director_to_performance VALUES(%s, %s, %s)"
        args = [self.current_uuid, performance_uuid, tv_show_uuid]
        execute_sql(self.db_connection, sql, args)



if __name__ == '__main__':
    d = DirectorParser(file_locations["directors"])
    d.parse_all()