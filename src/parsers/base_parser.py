
import re
from src.parsers import *

class BaseParser():
    def parse_all(self):
        raise NotImplemented

    def prime_file_input(self, f, skip_line):
        cur_line = 0
        for line in f:
            cur_line += 1
            if cur_line > skip_line:
                break

        return f

    def generic_parse_all(self, file_name, skipline, matcher_pattern, fun):
        with open(file_name, 'rU') as f:
            records_processed = 0
            f = self.prime_file_input(f, skipline)
            for line in f:
                if records_processed % 10000 == 0:
                    print str(records_processed) + " Records processed"
                match = re.search(matcher_pattern, line)
                if match is not None:
                    fun(match)
                records_processed += 1

    @staticmethod
    def get_performance_from_db(db_connection, title, year_str, performance_type):
        look_up_uuid_sql = "SELECT id " \
                           "FROM performances " \
                           "WHERE release_year = to_date(%s, 'YYYY') " \
                           "AND title = %s " \
                           "AND performance_type=%s"
        args = [year_str, convert_latin1(title), performance_type]
        rs = execute_sql_select(db_connection, look_up_uuid_sql, args)
        if len(rs) == 1:
            return rs[0]['id']
        else:
            return None

    @staticmethod
    def get_performer_from_db(db_connection, fname, lname, gender):
        rs = execute_sql_select(db_connection,
                   "SELECT id "
                   "FROM actors "
                   "WHERE first_name=%s "
                   "AND last_name=%s "
                   "AND gender=%s",
                   [convert_latin1(fname), convert_latin1(lname), gender])
        if len(rs) == 1:
            return rs[0]['id']
        else:
            return None

    @staticmethod
    def get_director_from_db(db_connection, fname, lname):
        rs = execute_sql_select(db_connection,
                   "SELECT id "
                   "FROM directors "
                   "WHERE first_name=%s "
                   "AND last_name=%s ",
                   [convert_latin1(fname), convert_latin1(lname)])
        if len(rs) == 1:
            return rs[0]['id']
        else:
            return None

    @staticmethod
    def get_tv_show_from_db(db_connection, performance_id, ep_season, ep_number):
        rs = execute_sql_select(db_connection,
                                "SELECT id "
                                "FROM tv_episodes "
                                "WHERE episode_number = %s "
                                "AND episode_season = %s "
                                "AND tv_show_id = %s ",
                                [ep_number, ep_season, performance_id])
        if len(rs) == 1:
            return rs[0]['id']
        else:
            return None

    @staticmethod
    def clean_episode_info(ep_name, ep_num_str):
        '''
        This function takes an episode name i.e Ally Abroad and an ep_num_str i.e (#3.1)}
        and parses out the name, and the number
        :param ep_name:
        :param ep_num_str:
        :return: a tuple with the cleaned episode name,
        an integer representing the season, and an integer
        representing the episode number in that season
        '''

        if ep_name is not None:
            ep_name = BaseParser.strip_quotes(ep_name)

        if ep_num_str is None or '#' not in ep_num_str or '.' not in ep_num_str or ')' not in ep_num_str:
            #the episode string name is messed up, just return None
            return ep_name, None, None

        ep_season = ep_num_str[ep_num_str.index('#')+1: ep_num_str.index('.')]
        ep_num = ep_num_str[ep_num_str.index('.')+1: ep_num_str.index(')')]
        try:
            ep_season = int(ep_season)
        except ValueError:
            ep_season = None
        try:
            ep_num = int(ep_num)
        except ValueError:
            ep_num = None

        return ep_name, ep_season, ep_num

    @staticmethod
    def clean_title(title):
        '''
        This function takes a title, which may be wrapped in quotes and include a year,
        and strips these.  It returns just the title of the movie or show
        :param title: the title to be cleaned
        :return: a clean title string
        '''
        year_reg_ex = '\(\S{4,}\)$'
        year_match = re.search(year_reg_ex, title)

        year_str = None
        if not year_match is None:
            #we will return the year string as well, incase the entry does not have an entry in the year column
            year_str = year_match.group().replace('(', '').replace(')', '')
            #Sometimes we can have a year string like (2004/I) we can still get a date out of this,
            #we just need to chop off the /I
            if '/' in year_str:
                year_str = year_str[:year_str.index('/')]
            try:
                int(year_str)
            except ValueError:
                #If it can't be parsed into a year, its not a real date.
                year_str = None

            #This should pull out the year
            title = title[0:year_match.span()[0]].strip()

        title = title.strip()
        title = BaseParser.strip_quotes(title)
        #now that we have stripped the quotes, if they were there, we might add back in the year IF it has a /I in it
        if '/I' in year_match.group():
            title = title + " " + year_match.group()

        return title, year_str

    @staticmethod
    def get_start_date_from_year_group(year_str):
        if year_str is None:
            return None
        if '-' in year_str:
            year_str = year_str[:year_str.index('-')]
        try:
            int(year_str)
            return year_str
        except ValueError:
            #Will happen if the year is ???? or
            # if its something else that isnt a number
            return None

    @staticmethod
    def clean_person_name(actor_str):
        '''
        parses out the person's name from the base string.
        :param actor_str:
        :return: a tuple of strings.  The first is the first name, the second the last name.
        If there is no comma in the actor string then the last name will be None
        '''

        fnln = actor_str.split(',')
        if len(fnln) == 2:
            first_name = fnln[1].strip()
            last_name = fnln[0].strip()
        else:
            first_name = fnln[0].strip()
            last_name = None

        return first_name, last_name

    @staticmethod
    def strip_quotes(s):
        if s.startswith('"') and s.endswith('"'):
            s = s[1:][:-1]
        elif s.startswith("'") and s.endswith("'"):
            s = s[1:][:-1]
        return s

    @staticmethod
    def get_performance_information_from_match(db_connection, match):
        ep_name, ep_season, ep_num = BaseParser.clean_episode_info(match.group(6), match.group(7))

        if ep_name is None:
            #This was a movie
            performance_type = 1
        else:
            #Its a tv show since there is an episode name
            performance_type = 2

        title, year_str = BaseParser.clean_title(match.group(3))

        performance_uuid = BaseParser.get_performance_from_db(
            db_connection, title, year_str, performance_type)

        if performance_uuid is None:
            #We don't recognize the performance, ignore this one
            return None, None, None, None

        if performance_type == 2:
            tv_show_uuid = BaseParser.get_tv_show_from_db(
                db_connection, performance_uuid, ep_season, ep_num)
            if tv_show_uuid is None:
                #In this case we have a record of a specific episode's performance,
                # but no information on the episode, we will ignore this entry
                return None, None, None, None
        else:
            tv_show_uuid = None

        if (match.re.groups < 11) or match.group(11) is None or match.group(11) == '':
            role = None
        else:
            role = match.group(11).strip('[').strip(']')

        if (match.re.groups < 12) or match.group(12) is None or match.group(12) == '':
            billing = None
        else:
            billing = match.group(12).strip('<').strip('>')
            try:
                billing = int(billing)
            except ValueError:
                #Billings should only be numbers, ignore it if it isn't
                billing = None

        return performance_uuid, tv_show_uuid, role, billing
