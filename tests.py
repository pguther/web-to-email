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
        self.non_level_3_url = 'http://www.ucsc.edu'
        self.level_3_url = 'http://history.ucsc.edu/graduate/index.html'
        self.news_url = 'http://news.ucsc.edu/2016/06/archivist.html'
        self.tuesday_newsday_url = 'http://news.ucsc.edu/tuesday-newsday/2016/june-21/index.html'

    def test_get_non_url(self):
        """
        test entering something that isn't a valid url
        :return:
        """
        rv = self.app.get('/?url=' + self.non_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 2
        assert error_messages[0] == 'Invalid URL. '
        assert error_messages[1] == 'Invalid URL \'ucsc\': No schema supplied. Perhaps you meant http://ucsc? '

    def test_get_non_domain(self):
        """
        test entering a url that doesn't belong to a ucsc domain
        :return:
        """
        rv = self.app.get('/?url=' + self.non_ucsc_domain_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL must belong to a UCSC domain '

    def test_get_non_level_3(self):
        """
        test entering a url that isn't a level 3 page, a news article, or a tuesday newsday archive
        :return:
        """
        rv = self.app.get('/?url=' + self.non_level_3_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL is not a level 3 UCSC page '

    def test_get_level_3(self):
        """
        test a level 3 page
        :return:
        """
        rv = self.app.get('/?url=' + self.level_3_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'id': 'emailTable'})
        assert email_table is not None

        banner = email_table.find('img', {'id': 'banner'})
        assert banner is not None

        title = email_table.find('h1', {'id': 'title'})
        assert title is not None

    def test_get_news_article(self):
        """
        test a news article
        :return:
        """
        rv = self.app.get('/?url=' + self.news_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'id': 'emailTable'})
        assert email_table is not None

        banner = email_table.find('img', {'id': 'banner'})
        assert banner is None

        title = email_table.find('h1', {'id': 'title'})
        assert title is not None

    def test_get_tuesday_newsday(self):
        """
        test a tuesday newsday archive
        :return:
        """
        rv = self.app.get('/?url=' + self.tuesday_newsday_url, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'class': 'wrap', 'summary': 'Tuesday Newsday email main content'})
        assert email_table is not None



    """
    def test_page_post(self):
        url = 'http://history.ucsc.edu/graduate/index.html'
        url = 'http://news.ucsc.edu/'
        rv = self.app.post('/', data={
            'url': url
        }, follow_redirects=True)

        print rv.data

        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'id': 'emailTable'})
        assert email_table is not None

        banner = email_table.find('img', {'id': 'banner'})
        assert banner is not None
    """

    def test_post_non_url(self):
        """
        test entering something that isn't a valid url
        :return:
        """
        rv = self.app.post('/', data={
            'url': self.non_url
        }, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 2
        assert error_messages[0] == 'Invalid URL. '
        assert error_messages[1] == 'Invalid URL \'ucsc\': No schema supplied. Perhaps you meant http://ucsc? '

    def test_post_non_domain(self):
        """
        test entering a url that doesn't belong to a ucsc domain
        :return:
        """
        rv = self.app.post('/', data={
            'url': self.non_ucsc_domain_url
        }, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL must belong to a UCSC domain '

    def test_post_non_level_3(self):
        """
        test entering a url that isn't a level 3 page, a news article, or a tuesday newsday archive
        :return:
        """
        rv = self.app.post('/', data={
            'url': self.non_level_3_url
        }, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 1
        assert error_messages[0] == 'URL is not a level 3 UCSC page '

    def test_post_level_3(self):
        """
        test a level 3 page
        :return:
        """
        rv = self.app.post('/', data={
            'url': self.level_3_url
        }, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'id': 'emailTable'})
        assert email_table is not None

        banner = email_table.find('img', {'id': 'banner'})
        assert banner is not None

        title = email_table.find('h1', {'id': 'title'})
        assert title is not None

    def test_post_news_article(self):
        """
        test a news article
        :return:
        """
        rv = self.app.post('/', data={
            'url': self.news_url
        }, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'id': 'emailTable'})
        assert email_table is not None

        banner = email_table.find('img', {'id': 'banner'})
        assert banner is None

        title = email_table.find('h1', {'id': 'title'})
        assert title is not None

    def test_post_tuesday_newsday(self):
        """
        test a tuesday newsday archive
        :return:
        """
        rv = self.app.post('/', data={
            'url': self.tuesday_newsday_url
        }, follow_redirects=True)
        error_messages = self.get_error_messages(rv.data)
        assert len(error_messages) == 0
        soup = BeautifulSoup(rv.data, 'lxml')

        result_div = soup.find('div', {'id': 'result'})
        assert result_div is not None

        email_table = result_div.find('table', {'class': 'wrap', 'summary': 'Tuesday Newsday email main content'})
        assert email_table is not None

if __name__ == '__main__':
    unittest.main()
