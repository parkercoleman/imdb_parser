#Stolen from imdb_parser, thanks
"""
Parses movies.list dump

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
    group 8: (.*)                                year
"""

import psycopg2
from src.util.sql_util import *
from src.parsers.base_parser import *

movies_file = file_locations["movies"]
movie_matcher_pattern = "((.*? \(\S{4,}\)) ?(\(\S+\))? ?(?!\{\{SUSPENDED\}\})(\{(.*?) ?(\(\S+?\))?\})? ?(\{\{SUSPENDED\}\})?)\t+(.*)$"

#Number of lines in the file to skip
SKIP_LINE = 15


class MovieParser(BaseParser):
    def __init__(self, file_name):
        self.file_name = file_name
        self.db_connection = None

    def parse_all(self):
        records_inserted = 0
        self.db_connection = psycopg2.connect(get_connection_string())
        with open(movies_file, 'rU') as f:
            f = self.prime_file_input(f, SKIP_LINE)
            for line in f:
                if records_inserted % 10000 == 0:
                    print str(records_inserted) + " Records inserted"
                match = re.search(movie_matcher_pattern, line)
                if match is not None:
                    record_type = MovieParser.is_movie_show_or_episode(match)
                    if record_type == 'movie':
                        self.insert_performance(match, 1)
                    if record_type == 'show':
                        self.insert_performance(match, 2)
                    if record_type == 'episode':
                        self.insert_episode(match)

                records_inserted += 1

    def insert_performance(self, match, performance_type):
        title, year, suspended = MovieParser.get_movie_and_show_info(match)
        sql = "INSERT INTO performances(title, release_year, performance_type, suspended, raw) " \
              "VALUES(%s, to_date(%s, 'YYYY'), %s, %s, %s)"
        args = [convert_latin1(title), year, performance_type, suspended, convert_latin1(match.string)]
        execute_sql(self.db_connection, sql, args)

    def insert_episode(self, match):
        uuid, ep_name, year, ep_season, ep_num, ep_raw = self.get_episode_info(match)
        if uuid is None:
            #if there isn't a tv show for this 'sode then we can't insert it
            return None

        sql = "INSERT INTO tv_episodes(episode_name, episode_date," \
                "episode_season, episode_number, episode_id_raw, tv_show_id, raw) " \
                "VALUES(%s, to_date(%s, 'YYYY'), %s, %s, %s, %s, %s)"
        args = [convert_latin1(ep_name), year, ep_season, ep_num, convert_latin1(ep_raw), uuid, convert_latin1(match.string)]
        execute_sql(self.db_connection, sql, args)

    @staticmethod
    def get_movie_and_show_info(match, prefer_title_year=False):
        '''
        Pulls out the title and year from the match.
        If 'prefer_title_year' is set to true the year in the title is used isntead of the year column
        this is useful when trying for find the show name for an episode
        :param match:
        :param prefer_title_year:
        :return:
        '''
        title, year = MovieParser.clean_title(match.group(2))
        year_column = MovieParser.get_start_date_from_year_group(match.group(8))
        #If the movie column is available we will use that, if its None for whatever reason we won't
        if year_column is not None and (not prefer_title_year):
            year = year_column
        suspended = MovieParser.is_suspended(match)
        return title, year, suspended

    def get_episode_info(self, match):
        #To find the show this episode belongs to, we need to use the release year
        show_name, release_year, suspended = MovieParser.get_movie_and_show_info(match, prefer_title_year=True)

        #However, when we insert the tv episode into the database, we want to use the air date, which is in the 8th match group
        air_date = MovieParser.get_start_date_from_year_group(match.group(8))

        ep_name, ep_season, ep_num = MovieParser.clean_episode_info(match.group(5), match.group(6))
        ep_raw = match.group(4)
        uuid = BaseParser.get_performance_from_db(self.db_connection, show_name, release_year, 2)
        return uuid, ep_name, air_date, ep_season, ep_num, ep_raw

    @staticmethod
    def is_suspended(match):
        #If group 7 has made a match, the show is suspended
        return not match.group(7) is None

    @staticmethod
    def is_movie_show_or_episode(match):
        '''
        This function determines if the matched value is a tv show or a movie.
        :param match: the matched string, our current line entry
        :return: 'show' if the match is a tv show, and 'movie' if it is a movie and 'episode' if it is the episode name for a tv show
        '''
        if((match.group(4) is not None)\
                or (match.group(5) is not None)\
                or (match.group(6) is not None)):
            #This means the entry is an episode for a show that should already exist in our tv shows table
            return 'episode'

        if (
                (match.group(3) is not None and match.group(3) == '(TV)')
                or (match.group(8) is None or '-' in match.group(8))
            ):
            #This means that its a show, with a specified start and end date, which will have 1 or more episodes
            return 'show'
        else:
            #Otherwise basically its a movie TODO: Maybe actually check to see if it is, we could return a "garbage line" status
            return 'movie'


if __name__ == '__main__':
    m = MovieParser(movies_file)
    m.parse_all()