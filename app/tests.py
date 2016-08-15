import unittest
from utils import ArticleUtils
from bs4 import BeautifulSoup


class TestArticleUtils(unittest.TestCase):

    def setUp(self):
        """
        set up the testing class
        :return:
        """
        self.utils = ArticleUtils()

    def test_convert_urls(self):
        """
        tests converting the urls in a soup
        :return:
        """
        html = '<img src="/image.html"/> ' \
               '<a href="/index.html"/> ' \
               '<iframe src="/iframe.html"/> ' \
               '<link href="/resultStyle.css"/>"'

        url_base = "http://website.com/"
        url_ending = 'post.html'

        soup = BeautifulSoup(html, 'lxml')

        self.utils.convert_urls(soup, url_base + url_ending)

        image = soup.find('img')
        assert image is not None
        assert 'src' in image.attrs
        assert image.attrs['src'] == url_base + 'image.html'

        iframe = soup.find('iframe')
        assert iframe is not None
        assert 'src' in iframe.attrs
        assert iframe.attrs['src'] == url_base + 'iframe.html'

        a = soup.find('a')
        assert a is not None
        assert 'href' in a.attrs
        assert a.attrs['href'] == url_base + 'index.html'

        link = soup.find('link')
        assert link is not None
        assert 'href' in link.attrs
        assert link.attrs['href'] == url_base + 'resultStyle.css'

    def test_add_inline__ucsc_css(self):
        """
        tests adding the inline ucsc css to elements
        :return:
        """
        html = '<img src="/image.html"/> ' \
               '<a href="/index.html"/> ' \
               '<h1>This is a sample Title</h1> ' \
               '<p>This is some Sample Text</p> '

        html = self.utils.add_inline_ucsc_css(html)

        soup = BeautifulSoup(html, 'lxml')

        image = soup.find('img')
        assert image is not None
        assert 'height' in image.attrs and 'style' in image.attrs
        assert image.attrs['height'] == 'auto'
        assert image.attrs['style'] == 'height:auto; max-width:100%'

        a = soup.find('a')
        assert a is not None
        assert 'style' in a.attrs
        assert a.attrs['style'] == 'color:#09c; -webkit-transition:color 0.2s ease-out; ' \
                                   'text-decoration:none; transition:color 0.2s ease-out'

        h1 = soup.find('h1')
        assert h1 is not None
        assert 'align' in h1.attrs and 'style' in h1.attrs
        assert h1.attrs['align'] == 'left'
        assert h1.attrs['style'] == 'color:#3a3a3a; font-weight:300; line-height:1.1em; margin-bottom:0.25em; ' \
                                    'margin-top:0; font-size:2.2rem; text-align:left'

        p = soup.find('p')
        assert p is not None
        assert 'style' in p.attrs
        assert p.attrs['style'] == 'margin:0 0 2em'


if __name__ == '__main__':
    unittest.main()