__author__ = 'parker'


from src.settings import *
from base_parser import *
from src.parsers import *


"""
RegExp: /(.*?)\t+((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\s*(\(.*?\))?\s*(\(.*\))?\s*(\[.*\])?\s*(<.*>)?$/gm
pattern: (.*?)\t+((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\s*(\(.*?\))?\s*(\(.*\))?\s*(\[.*\])?\s*(<.*>)?$
flags: gm
12 capturing groups:
    group 1: (.*?)                               surname, name
    group 2: #TITLE (UNIQUE KEY)
    group 3: (.*? \(\S{4,}\))                    movie name + year
    group 4: (\(\S+\))                           type ex:(TV)
    group 5: (\{(.*?) ?(\(\S+?\))?\})            series info ex: {Ally Abroad (#3.1)}
    group 6: (.*?)                               episode name ex: Ally Abroad
    group 7: (\(\S+?\))                          episode number ex: (#3.1)
    group 8: (\{\{SUSPENDED\}\})                 is suspended?
    group 9: (\(.*?\))                           info 1
    group 10: (\(.*\))                           info 2
    group 11: (\[.*\])                           role
    group 12: ()
"""

actors_matcher_pattern = '(.*?)\t+((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\s*(\(.*?\))?\s*(\(.*\))?\s*(\[.*\])?\s*(<.*>)?$'

actors_file = file_locations["actors"]
actress_file = file_locations["actress"]
SKIP_LINE = 239
import uuid

class PreformerParser(BaseParser):
    def __init__(self, actors_file, actress_file):
        self.actors_file = actors_file
        self.actress_file = actress_file
        self.db_connection = None

    def parse_all(self):
        self.db_connection = psycopg2.connect(get_connection_string())
        gender_file_map = {"male": self.actors_file,
                           "female": self.actress_file}

        for gender in gender_file_map.keys():
            with open(gender_file_map[gender], 'rU') as f:
                records_parsed = 0
                current_uuid = None
                f = self.prime_file_input(f, SKIP_LINE)
                for line in f:
                    if records_parsed % 10000 == 0:
                        print str(records_parsed) + " Records processed"
                    match = re.search(actors_matcher_pattern, line)
                    if match is not None:
                        if match.group(1) is not None and match.group(1) != '':
                            #This is an actor line, we need to insert a new performer
                            current_uuid = self.insert_performer(match, gender)

                        #Regardless of if this is an actor line, we need to insert the performance
                        self.insert_performance_from_match(match, current_uuid)

                    records_parsed += 1

    def insert_performance_from_match(self, match, current_actor_uuid):
        performance_uuid, tv_show_uuid, role, billing = BaseParser.get_performance_information_from_match(self.db_connection, match)
        if performance_uuid is None:
            return
        self.insert_performance(current_actor_uuid, performance_uuid, tv_show_uuid, role, billing)

    def insert_performer(self, match, gender):
        ''' Inserts a performer and returns the generated uuid for that performer.
        :param match:
        :param gender:
        :return:
        '''
        first_name, last_name = BaseParser.clean_person_name(match.group(1))
        performer_id = str(uuid.uuid4())
        sql = "INSERT INTO actors(id, first_name, last_name, gender) VALUES(%s, %s, %s, %s)"
        args = [performer_id, convert_latin1(first_name), convert_latin1(last_name), gender]
        execute_sql(self.db_connection, sql, args)
        return performer_id

    def insert_performance(self, performer_uuid, performance_uuid, ep_uuid, character_name, billing_position):
        ''' Inserts a performance
        :param performer_uuid:
        :param performance_uuid:
        :param character_name:
        :param billing_position:
        :return:
        '''
        sql = "INSERT INTO roles(performers_id, performance_id, character_name, billing_position, episode_id) " \
              "VALUES(%s, %s, %s, %s, %s)"
        args = [performer_uuid, performance_uuid, convert_latin1(character_name), billing_position, ep_uuid]
        execute_sql(self.db_connection, sql, args)

if __name__ == '__main__':
    m = PreformerParser(actors_file, actress_file)
    m.parse_all()
