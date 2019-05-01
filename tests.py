#!flask/bin/python
import unittest
from app import app
from bs4 import BeautifulSoup


class TestCase(unittest.TestCase):

    def get_error_messages(self, html):
        """
        returns any error messages flashed by a form
        :param soup:
        :return:
        """
        soup = BeautifulSoup(html, 'lxml')

        flashed_message_tags = soup.find_all('span', {'class': 'flashed-message'})

        error_messages = []

        if flashed_message_tags is not None:
            for flashed_message_tag in flashed_message_tags:
                error_messages.append(flashed_message_tag.get_text())

        return error_messages

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        self.non_url = "ucsc"
        self.non_ucsc_domain_url = 'https://google.com'
        self.non_emailbuilder_ucsc_url = 'https://www.ucsc.edu'
        self.emailbuilder_url = 'https://emailbuilder.ucsc.edu/samples/newsletter/index.html'
        self.errors_email = 'https://emailbuilder.ucsc.edu/samples/tests/test-email.html'

    




if __name__ == '__main__':
    unittest.main()
