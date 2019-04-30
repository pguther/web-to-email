from urllib.parse import urljoin, urlparse
import bs4
import requests
from bs4 import BeautifulSoup
import re
from premailer import Premailer
from .errors import ErrorCategory, ErrorType


class ContentNotHTMLException(Exception):
    """
    Exception for when a url doesn't return html content
    """
    def __init__(self):
        Exception.__init__(self, "Content type not text/html; charset=UTF-8")


class NoDateException(Exception):
    """
    Exception for when an article doesn't contain a date
    """
    def __init__(self):
        Exception.__init__(self, "Article does not contain a date")


class BodyIsNoneException(Exception):
    """
    Exception for when an article doesn't contain a date
    """
    def __init__(self):
        Exception.__init__(self, "Body is None")


class ImageException(Exception):
    def __init__(self, image_url):
        Exception.__init__(self, "Error getting height and width of image " + image_url)


class ArticleUtils(object):
    """
    This class provides functions to manipulate and reformat information scraped from
    articles, like urls, category names, etc.
    """
    def __init__(self):
        self.article_slug_regex = re.compile(r".*\/([^\/\.]+)(?:.[^\.\/]+$)*")
        self.article_ending_regex = re.compile(r".*\/([^\/]+)")
        self.content_tags_dict = {
            'h1':   True,
            'h2':   True,
            'h3':   True,
            'h4':   True,
            'h5':   True,
            'h6':   True,
            'p':    True,
            'li':   True,
        }

    def get_soup_from_url(self, page_url):
        """
        Takes the url of a web page and returns a BeautifulSoup Soup object representation
        :param page_url: the url of the page to be parsed
        :param article_url: the url of the web page
        :raises: r.raise_for_status: if the url doesn't return an HTTP 200 response
        :return: A Soup object representing the page html
        """
        r = requests.get(page_url)
        if r.status_code != requests.codes.ok:
            return 404
        if r.headers['content-type'] != 'text/html; charset=UTF-8':
            raise ContentNotHTMLException()
        return BeautifulSoup(r.content, 'lxml')

    def get_response(self, url):
        """
        Gets the response code for a url
        :param url:
        :return:
        """

        # noinspection PyBroadException
        try:
            r = requests.get(url)
        except:
            return 404
        return r.status_code

    def unicode_to_html_entities(self, content_string):
        """
        converts all unicode characters in a string to their html entity equivalents
        without converting any already existing html entities into their ascii equivalents
        :param content_string:
        :return:
        """

        transformed = ""
        i = 0
        while i < len(content_string):
            if ord(content_string[i]) >= 128:
                temp = content_string[i] + content_string[i + 1] + content_string[i + 2] + content_string[i + 3]
                print(temp + content_string[i + 4] + content_string[i + 5] + content_string[i + 6] + content_string[i + 7])

                try:
                    transformed += temp.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
                except UnicodeDecodeError as e:
                    transformed += temp.decode('iso-8859-1').encode('ascii', 'xmlcharrefreplace')
                i += 4
            else:
                transformed += content_string[i]
                i += 1

        return transformed

    def convert_urls(self, body, page_url):
        """
        converts all urls in the body from relative to full urls
        :param page_url:
        :param body:
        :return:
        """
        images = body.find_all("img")
        if images is not None:
            for image in images:
                if 'src' in image.attrs:
                    image_relative_src = image.attrs['src']
                    image_src = urljoin(page_url, image_relative_src)
                    image.attrs['src'] = image_src

        iframes = body.find_all("iframe")
        if iframes is not None:
            for iframe in iframes:
                if 'src' in iframe.attrs:
                    iframe_relative_src = iframe.attrs['src']
                    iframe_src = urljoin(page_url, iframe_relative_src)
                    iframe.attrs['src'] = iframe_src

        a_tags = body.find_all("a")
        if a_tags is not None:
            for a_tag in a_tags:
                if 'href' in a_tag.attrs:
                    a_tag_relative_src = a_tag.attrs['href']
                    a_tag_src = urljoin(page_url, a_tag_relative_src)
                    a_tag.attrs['href'] = a_tag_src

        links = body.find_all("link")
        if links is not None:
            for link in links:
                if 'href' in link.attrs:
                    link_relative_src = link.attrs['href']
                    link_src = urljoin(page_url, link_relative_src)
                    link.attrs['href'] = link_src


    def tag_check(self, soup):
        """
        Takes a BeautifulSoup soup, iterates through each tag, and if the tag is
        an empty tag, adds it to the list of empty tags
        :param soup:
        :return:
        """

        tag_check = ErrorCategory('Tag Check')
        empty_tag = ErrorType('Empty tag')

        for child in soup.recursiveChildGenerator():
            if isinstance(child, bs4.element.Tag):
                if str(child.name).lower() in self.content_tags_dict:
                    if len(child.contents) == 0:
                        empty_tag.add_tag(str(child))
                    else:
                        empty = True
                        for content in child.contents:
                            if isinstance(content, bs4.element.Tag):
                                stripped_content = content.encode(formatter='html').lstrip().rstrip()
                            else:
                                stripped_content = content.encode('utf-8').lstrip().rstrip()
                            if len(stripped_content) != 0:
                                empty = False
                        if empty:
                            empty_tag.add_tag(str(child))

        if len(empty_tag.tags) > 0:
            tag_check.add_type(empty_tag)

        return tag_check

    def image_check(self, soup):
        """
        Takes a bs4 Soup , iterates through all the image tags, and checks them for errors including:
            - missing alt attribute
            - missing src attribute
            - broken link
        :param soup:
        :return:
        """

        image_check = ErrorCategory('Image Check')
        missing_src = ErrorType('Missing source')
        missing_alt = ErrorType('Missing alt text')

        images = soup.find_all("img")
        if images is not None:
            for image in images:
                if 'src' not in image.attrs:
                    missing_src.add_tag(str(image))
                elif len(image['src'].lstrip().rstrip()) == 0:
                    missing_src.add_tag(str(image))

                if 'alt' in image.attrs:
                    alt = image.attrs['alt'].lstrip().rstrip()
                    if len(alt) == 0:
                        missing_alt.add_tag(str(image))
                else:
                    missing_alt.add_tag(str(image))

        if len(missing_src.tags) > 0:
            image_check.add_type(missing_src)

        if len(missing_alt.tags) > 0:
            image_check.add_type(missing_alt)

        return image_check

    def link_check(self, soup):
        """
        Takes a bs4 Soup , iterates through all the <a> tags, and checks them for errors including:
            - missing alt attribute
            - missing src attribute
            - broken link
        :param soup:
        :return:
        """

        link_check = ErrorCategory('Link Check')
        empty_link = ErrorType('Empty link')
        missing_href = ErrorType('Missing href')

        links = soup.find_all("a")
        if links is not None:
            for link in links:
                if len(link.contents) == 0:
                    empty_link.add_tag(str(link))
                else:
                    empty = True
                    for content in link.contents:
                        if isinstance(content, bs4.element.Tag):
                            stripped_content = content.encode(formatter='html').lstrip().rstrip()
                        else:
                            stripped_content = (content.encode('utf-8')).lstrip().rstrip()
                        if len(stripped_content) != 0:
                            empty = False
                    if empty:
                        empty_link.add_tag(str(link))
                if 'href' not in link.attrs:
                    missing_href.add_tag(str(link))
                else:
                    if len(link['href'].lstrip().rstrip()) == 0:
                        missing_href.add_tag(str(link))

        if len(empty_link.tags) > 0:
            link_check.add_type(empty_link)

        if len(missing_href.tags) > 0:
            link_check.add_type(missing_href)

        return link_check

    def get_errors_dict(self, soup):
        """
        Returns a dictionary of error categories, each containing a dictionary of error types and lists of tags
        :param soup:
        :return:
        """

        return [
            self.image_check(soup),
            self.link_check(soup),
            self.tag_check(soup),
        ]


class MessagingScraper(object):
    """
    scrapes a tuesday newsday page
    """
    def __init__(self, start_index=0):
        """
        Initializes the index counter for parsed objects to start_index or 0 if none is given
        :return:
        """
        self.utils = ArticleUtils()

    def scrape(self, url):
        """

        :param url:
        :return:
        """
        soup = self.utils.get_soup_from_url(url)

        self.utils.convert_urls(soup, url)

        body = soup.body

        content_div = soup.new_tag('div')

        content_div.attrs['class'] = 'content_div'

        for content in reversed(body.contents):
            content_div.insert(0, content.extract())

        body.append(content_div)

        # soup_string = str(soup)

        soup_string = soup.encode(formatter='html')

        soup_string = self.utils.unicode_to_html_entities(soup_string)

        premailer = Premailer(html=soup_string)

        output = premailer.transform()

        inline_body_soup = BeautifulSoup(output, 'lxml')

        content_tag = inline_body_soup.find('div', {'class': 'content_div'})

        content_string = ''

        if content_tag is not None:
            for content in content_tag.contents:

                if isinstance(content, bs4.element.Tag):
                    if 'class' in content.attrs:
                        for class_name in content.attrs['class']:
                            if class_name == 'ignore':
                                continue

                if isinstance(content, bs4.element.Comment):
                    content_string += '<!--' + str(content) + '-->'
                elif isinstance(content, bs4.element.NavigableString):
                    content_string += str(content)
                elif isinstance(content, bs4.element.Tag):
                    content_string += content.encode(formatter='html')

        content_string = self.utils.unicode_to_html_entities(content_string)
        errors = self.utils.get_errors_dict(content_tag)

        return content_string, errors
