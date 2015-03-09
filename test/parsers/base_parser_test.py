__author__ = 'parker'

import unittest

from src.parsers.base_parser import *


class BaseParserTest(unittest.TestCase):

    def setUp(self):
        self.mp = BaseParser()

    def test_title_cleaner(self):
        t, y = self.mp.clean_title('"!Next?" (1994)')
        self.assertEqual(t, "!Next?")
        self.assertEqual(y, "1994")

        t, y = self.mp.clean_title('Anno 2006 (2007)')
        self.assertEqual(t, "Anno 2006")
        self.assertEqual(y, "2007")

        t, y = self.mp.clean_title('"10 Years Younger" (2004/II)')
        self.assertEqual(t, "10 Years Younger (2004/II)")
        self.assertEqual(y, '2004')

        t, y = self.mp.clean_title('SOMEMOVIE (????)')
        self.assertEqual(y, None)

    def test_year_cleaner(self):
        self.assertEqual('1999', self.mp.get_start_date_from_year_group('1999-????'))
        self.assertEqual('1999', self.mp.get_start_date_from_year_group('1999'))
        self.assertEqual(None, self.mp.get_start_date_from_year_group('????'))
        self.assertEqual(None, self.mp.get_start_date_from_year_group(None))

    def test_actor_name_cleaner(self):
        self.assertEquals('Bob', self.mp.clean_person_name('Boberson, Bob')[0])
        self.assertEquals('Boberson', self.mp.clean_person_name('Boberson, Bob')[1])
        self.assertEquals('The Goofy Names', self.mp.clean_person_name('The Goofy Names')[0])
        self.assertEquals(None, self.mp.clean_person_name('The Goofy Names')[1])

    def test_episode_name_cleaner(self):
        ename, eseason, enum = self.mp.clean_episode_info("'Crazy Name'", '(#3.1)')
        self.assertEqual('Crazy Name', ename)
        self.assertEqual(3, eseason)
        self.assertEqual(1, enum)

        ename, eseason, enum = self.mp.clean_episode_info('"ANOTHER CRAZY NAME"', '(#300.12)')
        self.assertEqual('ANOTHER CRAZY NAME', ename)
        self.assertEqual(300, eseason)
        self.assertEqual(12, enum)

        ename, eseason, enum = self.mp.clean_episode_info('"ANOTHER CRAZY NAME"', '(#3.12)')
        self.assertEqual(3, eseason)
        self.assertEqual(12, enum)

        ename, eseason, enum = self.mp.clean_episode_info('"ANOTHER CRAZY NAME"', '(#f.1200)')
        self.assertEqual(None, eseason)
        self.assertEqual(1200, enum)

        ename, eseason, enum = self.mp.clean_episode_info('"ANOTHER CRAZY NAME"', '(#5.wamp)')
        self.assertEqual(5, eseason)
        self.assertEqual(None, enum)

        ename, eseason, enum = self.mp.clean_episode_info('"ANOTHER CRAZY NAME"', 'uhoh')
        self.assertEqual(None, eseason)
        self.assertEqual(None, enum)