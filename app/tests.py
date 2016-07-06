import unittest
from utils import ArticleScraper, ArticleUtils, PageScraper, TuesdayNewsdayScraper
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
               '<link href="/style.css"/>"'

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
        assert link.attrs['href'] == url_base + 'style.css'

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


class TestPageScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = PageScraper()
        self.utils = ArticleUtils()

    def test_get_title(self):
        """
        tests getting the title from a level 3 page
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<h1 class="page-title" id="title">Sample Title</h1>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        title = self.scraper.get_title(body)

        assert title is not None
        assert title == '<h1 class="page-title" id="title">Sample Title</h1>'

    def test_get_nonexistent_title(self):
        """
        tests getting the title from a level 3 page when it doesn't exist
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<h2" id="title">Sample Sub Header</h1>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        title = self.scraper.get_title(body)

        assert title is None

    def test_get_content(self):
        """
        test getting the content of a level 3 page
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<div class="content contentBox">Content Box 1</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        content = self.scraper.get_content(body)

        assert content is not None
        assert content == 'Content Box 1'

        html = '<div class="main-content" id="main" role="main">' \
               '<div class="contentBox content-box">Content Box 2</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        content = self.scraper.get_content(body)

        assert content is not None
        assert content == 'Content Box 2'
        html = '<div class="main-content" id="main" role="main">' \
               '<div class="contentBox">Content Box 3</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        content = self.scraper.get_content(body)
        assert content is not None
        assert content == 'Content Box 3'

    def test_get_nonexistent_content(self):
        """
        test getting the content of a level 3 page when it doesn't exist
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<div class="bannerBox">A Banner Box</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        content = self.scraper.get_content(body)

        assert content is None

    def test_get_banner_image(self):
        """
        test getting the banner image for a level 3 page
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<div id="bannerBox"> ' \
               '<img id="banner" src="source"/> ' \
               '</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        banner = self.scraper.get_banner_image(body)

        assert banner is not None
        assert banner == '<img id="banner" src="source"/>'

    def test_get_nonexistent_banner_image(self):
        """
        test getting the banner image for a level 3 page when it doesn't exist
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<div id="bannerBox"> ' \
               '</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        banner = self.scraper.get_banner_image(body)

        assert banner is None


class TestArticleScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = ArticleScraper()
        self.utils = ArticleUtils()

    def test_get_author_info(self):
        """
        tests getting the author info vcard
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<p class="vcard">By ' \
               '<a class="email fn"><span class="name">Sample Author</span></a>' \
               '</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        author_info = self.scraper.get_author_info(body)

        assert author_info is not None
        assert author_info == '<p class="vcard">By <a class="email fn"><span class="name">Sample Author</span></a></p>'

    def test_get_nonexistent_author_info(self):
        """
        tests getting the author info vcard when it doesn't exist
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<p>A random tag</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        author_info = self.scraper.get_author_info(body)

        assert author_info is None

    def test_get_campus_message(self):
        """
        tests getting campus messages
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<div class="campus-message">' \
               '<p><strong>To:</strong><span class="message-to">Sample Recipient</span></p>' \
               '<p><strong>From:</strong><span class="message-from">Sample Sender</span></p>' \
               '</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        campus_message = self.scraper.get_campus_message_info(body)

        assert campus_message is not None
        assert campus_message == '<p><strong>To:</strong><span class="message-to">Sample Recipient</span></p>' \
                                 '<p><strong>From:</strong><span class="message-from">Sample Sender</span></p>'

    def test_get_nonexistent_campus_message(self):
        """
        tests getting campus messages when it doesn't exist
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<p>Unrelated Paragraph</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        campus_message = self.scraper.get_campus_message_info(body)

        assert campus_message is None

    def test_get_date(self):
        """
        tests getting the date paragraph
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<p class="date">Month Day, Year</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        date = self.scraper.get_date(body)

        assert date is not None
        assert date == '<p class="date">Month Day, Year</p>'

    def test_get_nonexistent_date(self):
        """
        tests getting the date paragraph when it doesn't exist
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<p>Unrelated Paragraph</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        date = self.scraper.get_date(body)

        assert date is None

    def test_get_headers(self):
        """
        tests getting both title and subhead if they both exist
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<h1 id="title">Sample Title</h1>' \
               '<p class="subhead">Sample Subheader</p>' \
               '<p>Unrelated Paragraph</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        title, subhead = self.scraper.get_headers(body)

        assert title is not None
        assert subhead is not None

        assert title == '<h1 id="title">Sample Title</h1>'
        assert subhead == '<p class="subhead">Sample Subheader</p>'

    def test_get_headers_nonexistent_title(self):
        """
        tests getting the title and subhead when the title does not exist
        but the subhead does
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<p class="subhead">Sample Subheader</p>' \
               '<p>Unrelated Paragraph</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        title, subhead = self.scraper.get_headers(body)

        assert title is None
        assert subhead is not None

        assert subhead == '<p class="subhead">Sample Subheader</p>'

    def test_get_headers_nonexistent_subhead(self):
        """
        tests getting both title and subhead when the subhead doesn't exist
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<h1 id="title">Sample Title</h1>' \
               '<p>Unrelated Paragraph</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        title, subhead = self.scraper.get_headers(body)

        assert title is not None
        assert subhead is None

        assert title == '<h1 id="title">Sample Title</h1>'

    def test_get_nonexistent_headers(self):
        """
        tests getting both title and subhead when neither exists
        :return:
        """

        html = '<div class="main-content" id="main" role="main">' \
               '<p>Unrelated Paragraph</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        title, subhead = self.scraper.get_headers(body)

        assert title is None
        assert subhead is None

    def test_get_images(self):
        """
        test getting images from article
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<p>Unrelated Paragraph</p>' \
               '<figure class="lead-image article-image">' \
               '<img alt="image_alt" src="image_src"/>' \
               '<figcaption class="caption">Sample Caption</figcaption>' \
               '</figure>'' \
               ''</div>'

        body = BeautifulSoup(html, 'lxml')

        figures_string = self.scraper.get_images(body)

        assert figures_string is not None
        assert figures_string == '<figure align="right" class="lead-image article-image" width="300px">' \
                                 '<img alt="image_alt" src="image_src"/>' \
                                 '<figcaption class="caption">Sample Caption</figcaption></figure>'

    def test_get_nonexistent_images(self):
        """
        test getting images from article
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<p>Unrelated Paragraph</p>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        figures_string = self.scraper.get_images(body)

        assert figures_string is None

    def test_get_article_string(self):
        """
        tests getting the article string
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<figure class="lead-image article-image">' \
               '<img alt="image_alt" src="image_src"/>' \
               '<figcaption class="caption">Sample Caption</figcaption>' \
               '</figure>' \
               '<div class="article-body">Article Body</div>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        article_text = self.scraper.get_article_text(body)

        assert article_text is not None
        assert article_text == 'Article Body'

    def test_get_nonexistent_article_string(self):
        """
        tests getting the article string when it doesn't exist
        :return:
        """
        html = '<div class="main-content" id="main" role="main">' \
               '<figure class="lead-image article-image">' \
               '<img alt="image_alt" src="image_src"/>' \
               '<figcaption class="caption">Sample Caption</figcaption>' \
               '</figure>' \
               '</div>'

        body = BeautifulSoup(html, 'lxml')

        article_text = self.scraper.get_article_text(body)

        assert article_text is None


if __name__ == '__main__':
    unittest.main()