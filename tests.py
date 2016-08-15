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
        self.non_ucsc_domain_url = 'http://google.com'
        self.non_messaging_ucsc_url = 'http://www.ucsc.edu'
        self.messaging_url = 'http://messaging.ucsc.edu/testing/may/my-testing-email.html'

    def test_non_url(self):
        """
        test entering something that isn't a valid url
        :return:
        """
        rv = self.app.get('/?url=' + self.non_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 2
        assert error_messages[0] == 'Invalid URL. '
        assert error_messages[1] == 'Invalid URL \'ucsc\': No schema supplied. Perhaps you meant http://ucsc? '

    def test_non_domain(self):
        """
        test entering a url that doesn't belong to a ucsc domain
        :return:
        """
        rv = self.app.get('/?url=' + self.non_ucsc_domain_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL must belong to a UCSC domain '

    def test_non_messaging_ucsc_url(self):
        """
        test entering a url that belongs to a ucsc domain but not messaging.ucsc.edu
        :return:
        """
        rv = self.app.get('/?url=' + self.non_messaging_ucsc_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL is not a messaging.ucsc.edu post '

    def test_urlquery_messaging(self):
        """
        test a tuesday newsday archive
        :return:
        """
        rv = self.app.get('/?url=' + self.messaging_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'align': 'center', 'summary': 'Email content'})

        assert email_table is not None


if __name__ == '__main__':
    unittest.main()
