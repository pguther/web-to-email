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

    def test_non_url(self):
        """
        test entering something that isn't a valid url
        :return:
        """
        rv = self.app.get('/?url=' + self.non_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 2
        assert error_messages[0] == 'Invalid URL. '
        assert error_messages[1] == 'Invalid URL ucsc: No schema supplied. Perhaps you meant https://ucsc? '

    def test_non_domain(self):
        """
        test entering a url that doesn't belong to a ucsc domain
        :return:
        """
        rv = self.app.get('/?url=' + self.non_ucsc_domain_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL must belong to a UCSC domain '

    def test_non_emailbuilder_ucsc_url(self):
        """
        test entering a url that belongs to a ucsc domain but not emailbuilder.ucsc.edu
        :return:
        """
        rv = self.app.get('/?url=' + self.non_emailbuilder_ucsc_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL must be from emailbuilder.ucsc.edu '

    def test_emailbuilder(self):
        """
        test a emailbuilder.ucsc.edu post
        :return:
        """
        rv = self.app.get('/?url=' + self.emailbuilder_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'class': 'main'})

        assert email_table is not None

    def test_errors_email(self):
        """
        test a messaging.ucsc.edu post with errors
        :return:
        """
        rv = self.app.get('/?url=' + self.errors_email, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        missing_src_list = soup.find_all('li', {'class': 'missing-source'})
        assert len(missing_src_list) == 1

        missing_alt_list = soup.find_all('li', {'class': 'missing-alt-text'})
        assert len(missing_alt_list) == 1

        missing_href_list = soup.find_all('li', {'class': 'missing-href'})
        assert len(missing_href_list) == 1

        empty_link_list = soup.find_all('li', {'class': 'empty-link'})
        assert len(empty_link_list) == 1

        empty_tag_list = soup.find_all('li', {'class': 'empty-tag'})
        assert len(empty_tag_list) == 1




if __name__ == '__main__':
    unittest.main()
