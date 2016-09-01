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

    def test_image_check(self):
        """

        :return:
        """
        html = '<img src="http://www.ucsc.edu/identity/images/ucsc-stack.jpg"/> ' \
               '<a href="http://www.ucsc.edu/index.html"/> ' \
               '<div><img src="not a real link" alt="Has Alt Text 1"/>' \
               '<img src=""/></div>' \
               '<img/></div>' \
               '<h1>This is a sample Title</h1> ' \
               '<img src="http://www.ucsc.edu/identity/images/ucsc-stack.jpg" alt="Has Alt Text 2"/>' \
               '<img src="http://www.ucsc.edu/identity/images/ucsc-stack.jpg" alt=" \n"/>' \
               '<img alt="" class="mFullImage" ' \
               'src="http://www.ucsc.edu/identity/images/ucsc-stack.jpg" style="height="185" width="250"/>' \
               '<img src="http://www.ucsc.edu/identity/images/nonexistant_image.jpg" alt="not working link"/>'

        soup = BeautifulSoup(html, 'lxml')

        image_errors = self.utils.image_check(soup)

        assert image_errors.category == 'Image Check' and image_errors.class_name == 'image-check'
        assert len(image_errors.types) == 2

        missing_src = image_errors.get_type('Missing Source')
        assert missing_src is not None
        assert len(missing_src.tags) == 2

        missing_alt = image_errors.get_type('Missing Alt Text')
        assert missing_alt is not None
        assert len(missing_alt.tags) == 5

    def test_link_check(self):
        """

        :return:
        """
        html = '<a>Tag with no href</a>' \
               '<a href="">Tag with empty href</a>' '' \
               '<a href="not a real link">Tag with not working link</a>' \
               '<a href="http://messaging.ucsc.edu/testing/may/admin-letter-test.html"></a>' \
               '<a href="http://messaging.ucsc.edu/testing/may/admin-letter-test.html"><Working Link</a>'

        soup = BeautifulSoup(html, 'lxml')

        link_errors = self.utils.link_check(soup)

        assert link_errors.category == 'Link Check' and link_errors.class_name == 'link-check'
        assert len(link_errors.types) == 2

        empty_link = link_errors.get_type('Empty Link')
        assert empty_link is not None
        assert len(empty_link.tags) == 1

        missing_href = link_errors.get_type('Missing href')
        assert missing_href is not None
        assert len(missing_href.tags) == 2

    def test_tag_check(self):
        """
        Checks content tag check function
        :return:
        """
        html = '<h1></h1>' \
               '<h1> </h1>' \
               '<h1>Not Empty</h1>' \
               '<h2></h2>' \
               '<h2> </h2>' \
               '<h2>Not Empty</h2>' \
               '<h3></h3>' \
               '<h3> </h3>' \
               '<h3>Not Empty</h3>' \
               '<h4></h4>' \
               '<h4> </h4>' \
               '<h4>Not Empty</h4>' \
               '<h5></h5>' \
               '<h5> </h5>' \
               '<h5>Not Empty</h5>' \
               '<h6></h6>' \
               '<h6> </h6>' \
               '<h6>Not Empty</h6>' \
               '<p></p>'   \
               '<p> </p>'   \
               '<p>Not Empty</p>'   \
               '<li></li>' \
               '<li> </li>' \
               '<li>Not Empty</li>'

        soup = BeautifulSoup(html, 'lxml')

        tag_errors = self.utils.tag_check(soup)

        assert tag_errors.category == 'Tag Check' and tag_errors.class_name == 'tag-check'
        assert len(tag_errors.types) == 1

        empty_tag = tag_errors.get_type('Empty Tag')
        assert empty_tag is not None
        assert len(empty_tag.tags) == 16

if __name__ == '__main__':
    unittest.main()
