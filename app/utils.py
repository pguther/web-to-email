from urlparse import urljoin
import bs4
import requests
from bs4 import BeautifulSoup
import re
import urllib
import cStringIO
from unidecode import unidecode
from PIL import Image
import datetime
from premailer import Premailer
import pprint


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


class ArticleUtils:
    """
    This class provides functions to manipulate and reformat information scraped from
    articles, like urls, category names, etc.
    """
    def __init__(self):
        self.article_slug_regex = re.compile(r".*\/([^\/\.]+)(?:.[^\.\/]+$)*")
        self.article_ending_regex = re.compile(r".*\/([^\/]+)")

    def get_nicename(self, name):
        """
        Returns the nicename version of a string; converts to lowercase and replaces
        spaces with dashes
        :param name:
        :return:
        """
        name = name.replace(' ', '-')
        name = name.lower()

        return name

    def get_url_slug(self, page_url):
        """
        Returns the last section of a url eg. 'posts' for 'wordpress.com/posts.html'
        :raises Exception: if the regex is unable to locate the url slug
        :param page_url: the page url
        :return: the url slug
        """
        slug_match = self.article_slug_regex.findall(page_url)
        if slug_match and len(slug_match) == 1:
            return slug_match[0]
        else:
            raise Exception("unable to find slug for article: " + page_url + "\n")

    def get_url_ending(self, page_url):
        """
        Gets the url slug plus the file ending eg:
        www.example.com/example.html -> example.html
        :param page_url: the url to get the ending from
        :return: the url ending
        """
        slug_match = self.article_ending_regex.findall(page_url)
        if slug_match and len(slug_match) == 1:
            return slug_match[0]
        else:
            raise Exception("unable to find ending for article: " + page_url + "\n")

    def get_image_dimens(self, image_url):
        """
        Uses the PIL Pillow fork to get the width and height of an image from a url
        :param image_url: the url of the image to get the dimensions for
        :return: height, width
        """
        try:
            url_connection = urllib.urlopen(image_url)
            image_file = cStringIO.StringIO(url_connection.read())
            im = Image.open(image_file)
            return im.size
        except IOError as e:
            raise ImageException(image_url)

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
            r.raise_for_status()
        if r.headers['content-type'] != 'text/html; charset=UTF-8':
            raise ContentNotHTMLException()
        return BeautifulSoup(r.content, 'lxml')

    def zap_tag_contents(self, tag):
        """
        Converts any Windows cp1252 or unicode characters in the text of
        a BeautifulSoup bs4.element.Tag Object to ASCII equivalents
        :rtype: bs4.element.Tag
        :param tag: the Tag object to convert
        :return: None
        """
        if hasattr(tag, 'contents'):
            content_length = len(tag.contents)

            gzapper = GremlinZapper()

            for x in range(0, content_length):
                if isinstance(tag.contents[x], bs4.element.NavigableString):
                    unicode_entry = gzapper.kill_gremlins(tag.contents[x])
                    unicode_entry = unidecode(unicode_entry)
                    tag.contents[x].replace_with(unicode_entry)
                elif isinstance(tag.contents[x], bs4.element.Tag):
                    self.zap_tag_contents(tag.contents[x])


class PageScraper(object):
    """
    Takes a list of a or a single ucsc site page and returns the title, the main content,
    and the banner image url if it exists
    """
    def __init__(self, start_index=0):
        """
        Initializes the index counter for parsed objects to start_index or 0 if none is given
        :return:
        """
        self.gremlin_zapper = GremlinZapper()
        self.utils = ArticleUtils()

    def get_title(self, body):
        """
        returns the title of a page given the soup of its body
        :param body:
        :return:
        """
        return str(body.find("h1", {"id": "title"}))

    def get_content(self, body):
        """
        returns the main content html of a page given the body
        :param body:
        :return:
        """
        valid_content_classes = ['content contentBox', 'contentBox content-box', 'contentBox']

        # pp = pprint.PrettyPrinter(indent=4)

        content_tags = []

        for content_class in valid_content_classes:
            content_tags = body.find_all("div", {"class": content_class})
            if len(content_tags) > 0:
                break

        if content_tags is None:
            return

        content_tag_string = ''
        # pp.pprint(content_tag)
        for content_tag in content_tags:
            for item in content_tag.contents:
                content_tag_string += str(item)

        return content_tag_string

    def add_inline_ucsc_css(self, tag_text):
        """
        adds inline ucsc css to the given body
        :param body:
        :return:
        """
        premailer = Premailer(html=tag_text,
                      external_styles=['app/static/email_style.css',])

        output = premailer.transform()

        soup = BeautifulSoup(output, 'lxml')

        body_contents = ''

        for item in soup.body.contents:
            body_contents += str(item)

        return body_contents

    def get_banner_image(self, body):
        """
        returns the banner image url
        :param body:
        :return:
        """
        banner_box = body.find("div", {"id": "bannerBox"})
        if banner_box is not None:
            banner_image = str(banner_box.find("img", {"id": "banner"}))
        else:
            banner_image = None

        return banner_image

    def convert_urls(self, body, page_url):
        """
        converts all urls in the body from relative to full urls
        :param page_url:
        :param body:
        :return:
        """
        images = body.findAll("img")
        if images is not None:
            for image in images:
                image_relative_src = image['src']
                image_src = urljoin(page_url, image_relative_src)
                image['src'] = image_src

        iframes = body.findAll("iframe")
        if iframes is not None:
            for iframe in iframes:
                iframe_relative_src = iframe['src']
                iframe_src = urljoin(page_url, iframe_relative_src)
                iframe['src'] = iframe_src

        links = body.findAll("a")
        if links is not None:
            for link in links:
                link_relative_src = link['href']
                link_src = urljoin(page_url, link_relative_src)
                link['href'] = link_src


    def scrape_page(self, page_url):
        """

        :param page_url:
        :return:
        """
        soup = self.utils.get_soup_from_url(page_url)

        body = soup.find("div", {"id": "main"})
        # print '================================================='
        # print str(body)

        self.utils.zap_tag_contents(body)

        inline_body_string = self.add_inline_ucsc_css(str(body))

        inline_body_soup = BeautifulSoup(inline_body_string, 'lxml')

        # print '================================================='
        # print str(inline_body_soup)

        body = inline_body_soup.find("div", {"id": "main"})

        self.convert_urls(body, page_url)

        title = self.get_title(body)

        content = self.get_content(body)

        # print '================================================='
        # print content

        banner_image = self.get_banner_image(body)

        return {'title': title,
                'content': content,
                'banner_image': banner_image}


class ArticleScraper(object):
    """
    Takes a list of news.ucsc.edu articles, scrapes and writes them to files so that they can be used
    by jekyll to create a wordpress import file.  Also creates a file of statistics on the scrapeability
    the articles
    """
    def __init__(self, start_index=0):
        """
        Initializes the index counter for parsed objects to start_index or 0 if none is given
        :return:
        """
        self.gremlin_zapper = GremlinZapper()
        self.utils = ArticleUtils()
        self.object_index = start_index
        self.date_regex = re.compile(r"[A-Za-z]+\s*\d{1,2}\,\s*\d{4}")
        self.word_regex = re.compile(r"([^\s\n\r\t]+)")
        self.author_regex = re.compile(r"By\s*(.+)")

        self.author_whitelist = {
            'tim stephens':                 'Tim Stephens',
            'jennifer mcnulty':             'Jennifer McNulty',
            'scott rappaport':              'Scott Rappaport',
            'gwen mickelson':               'Gwen Jourdonnais',
            'gwen jourdonnais':             'Gwen Jourdonnais',
            'dan white':                    'Daniel White',
            'daniel white':                 'Daniel White',
            'scott hernandez-jason':        'Scott Hernandez-Jason',
            'peggy townsend':               'Peggy Townsend',
            'public information office':    'Public Information Office'
        }

    def get_next_index(self):
        """
        Used as a counter to give each item (posts, images, and videos) a unique ID
        :return: the next unique id
        """
        self.object_index += 1
        return self.object_index

    def get_author_info(self, body):
        """
        finds and returns the author info from a news.ucsc.edu article, or None
        :param body: the BeautifulSoup object representing the news.ucsc.edu article body
        :return: author, author_role, author_telephone: of the news.ucsc.edu article
        """
        author_tag = body.find("span", {"class": "name"})
        if author_tag is not None:
            self.utils.zap_tag_contents(author_tag)
            author = author_tag.get_text()
        else:
            author = 'Public Information Office'

        author_telephone_tag = body.find("span", {"class": "tel"})
        if author_telephone_tag is not None:
            self.utils.zap_tag_contents(author_telephone_tag)
            author_telephone = author_telephone_tag.get_text()
        else:
            author_telephone = None

        author_role_tag = body.find("span", {"class": "role"})
        if author_role_tag is not None:
            self.utils.zap_tag_contents(author_role_tag)
            author_role = author_role_tag.get_text()
        else:
            author_role = None

        return author, author_role, author_telephone

    def categorize_author(self, author):
        """
        Checks if the given author is one of the current ucsc news writers.  If they are, author is returned as
        author, and an empty string is return as article_author.  If they are not, Public Information Office is returned
        as author and the given author is returned as article_author
        :param author:
        :return:
        """
        if author.lower() in self.author_whitelist:
            return self.author_whitelist[author.lower()], None
        else:
            return 'Public Information Office', author

    def get_campus_message_info(self, body):
        """
        Gets the sender and audience for a campus message
        :param body:
        :return:
        """
        raw_message_from = body.find("span", {"class": "message-from"})
        if raw_message_from is not None:
            message_from = self.gremlin_zapper.zap_string(raw_message_from.get_text())
        else:
            message_from = None

        raw_message_to = body.find("span", {"class": "message-to"})
        if raw_message_to is not None:
            message_to = self.gremlin_zapper.zap_string(raw_message_to.get_text())
        else:
            message_to = None

        return message_from, message_to

    def get_date(self, body):
        """
        returns date of news.ucsc.edu article or raises exception
        :param body:
        :raises
        :return:
        """
        date_tag = body.find("p", {"class": "date"})
        if date_tag is not None:
            date_string = date_tag.get_text()
            matches = self.date_regex.findall(date_string)
            if matches:
                # Convert date from Month, Day Year to Year-Month-Day
                try:
                    raw_date = matches[0]
                    raw_date = raw_date.rstrip()
                    raw_date = raw_date.lstrip()
                    return datetime.datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
                except ValueError:
                    raise NoDateException()
        else:
            raise NoDateException()

    def get_headers(self, body):
        """
        returns title and subhead of news.ucsc.edu article
        :param body:
        :return:
        """
        title_tag = body.find("h1", {"id": "title"})
        if title_tag is not None:
            raw_title = title_tag.get_text()
            title = self.gremlin_zapper.zap_string(raw_title)
        else:
            title = None

        subhead_tag = body.find("p", {"class": "subhead"})
        if subhead_tag is not None:
            raw_subhead = subhead_tag.get_text()
            subhead = self.gremlin_zapper.zap_string(raw_subhead)
        else:
            subhead = None

        return title, subhead

    def get_images(self, article_url, body):
        """
        Creates a dictionary of dictionaries of information about images in the article
        :param article_url
        :param body:
        :return:
        """

        images_dictionary = dict()

        figures = body.findAll("figure", {"class": "article-image"})

        for figure in figures:

            image_tag = figure.find("img")
            if image_tag is not None:
                image_relative_src = image_tag['src']
                image_src = urljoin(article_url, image_relative_src)

                image_src = image_src.replace(' ', '%20')
                # image_src = image_src.replace('_', '%5F')

                image_id = str(self.get_next_index())

                caption_tag = figure.find("figcaption", {"class": "caption"})
                if caption_tag is not None:
                    raw_caption = caption_tag.get_text()
                    matches = self.word_regex.findall(raw_caption)
                    image_caption = ' '.join(matches)
                    image_caption = self.gremlin_zapper.zap_string(image_caption)
                else:
                    image_caption = ''

                image_width, image_height = self.utils.get_image_dimens(image_src)
                if 'height' in image_tag:
                    image_height = image_tag['height']
                if 'width' in image_tag:
                    image_width = image_tag['width']

                images_dictionary[image_src] = {
                    'image_caption': image_caption,
                    'image_height': str(image_height),
                    'image_width': str(image_width),
                    'image_id': image_id
                }

        images = body.findAll("img")
        if images is not None:
            for image in images:
                image_relative_src = image['src']
                image_src = urljoin(article_url, image_relative_src)
                image['src'] = image_src

        iframes = body.findAll("iframe")
        if iframes is not None:
            for iframe in iframes:
                iframe_relative_src = iframe['src']
                iframe_src = urljoin(article_url, iframe_relative_src)
                iframe['src'] = iframe_src

        links = body.findAll("a")
        if links is not None:
            for link in links:
                link_relative_src = link['href']
                link_src = urljoin(article_url, link_relative_src)
                link['href'] = link_src

        return images_dictionary

    def get_article_text(self, body):
        """
        Gets the article main text
        :param body:
        :return:
        """
        raw_article_body = body.find("div", {"class": "article-body"})

        article_body_no_html = raw_article_body

        if article_body_no_html is not None:
            article_body_no_html = article_body_no_html.get_text()
            article_body_no_html = self.gremlin_zapper.zap_string(article_body_no_html)

        if raw_article_body is not None:
            self.utils.zap_tag_contents(raw_article_body)
            article_body = ''
            for item in raw_article_body.contents:
                article_body += str(item)
        else:
            article_body = ''

        # article_body, errors = tidy_fragment(article_body, options={'numeric-entities': 1})

        return article_body  # , article_body_no_html

    def get_categories(self, page_html):
        """
        Gets the categories of the given news.ucsc.edu article page
        :param page_html:
        :return:
        """
        category_tags = page_html.findAll(attrs={"name": "category"})

        categories = []

        for category_tag in category_tags:
            self.utils.zap_tag_contents(category_tag)
            categories.append(category_tag['content'])

        return categories

    def scrape_article(self, article_url, no_html=False):
        """

        :param article_url:
        :return:
        """
        soup = self.utils.get_soup_from_url(article_url)

        categories = self.get_categories(soup)

        body = soup.find("div", {"id": "main"})

        author, article_author_title, article_author_telephone = self.get_author_info(body)

        author, article_author,  = self.categorize_author(author)

        date = self.get_date(body)

        title, subhead = self.get_headers(body)

        # images_dictionary = dict()

        images_dictionary = self.get_images(article_url, body)

        message_from, message_to = self.get_campus_message_info(body)

        slug = self.utils.get_url_slug(article_url)

        source_permalink = "<p><a href=\"" + article_url + "\" title=\"Permalink to " + slug + "\">Source</a></p>"

        file_name = date + '-' + slug + ".md"

        article_body, article_body_no_html = self.get_article_text(body)

        return {
            'file_name': file_name,
            'source_permalink': source_permalink,
            'author': author,
            'article_author': article_author,
            'article_author_title': article_author_title,
            'article_author_telephone': article_author_telephone,
            'categories': categories,
            'message_from': message_from,
            'message_to': message_to,
            'date': date,
            'title': title,
            'subhead': subhead,
            'images_dictionary': images_dictionary,
            'article_body': article_body,
            'article_body_no_html': article_body_no_html,
            'post_id': str(self.get_next_index())
        }

    def scrape_articles(self, article_list, screen=None):
        """
        Scrapes the urls in article_list and writes the resulting articles
        :param article_list: The list of article URLs to scrape
        :param screen: the CommandLineDisplay object to update the progress of the scraper with
        :return:
        """
        num_urls = len(article_list)
        current_url_num = 1
        prog_percent = 0

        unscrapeable_article_dict = dict()

        articles_dictionary = dict()

        for article in article_list:
            if screen is not None:
                screen.report_progress('Scraping Articles', 'Scraping Article', article, prog_percent)
                prog_percent = int(((current_url_num + 0.0) / num_urls) * 100)
                current_url_num += 1

            try:
                article_info = self.scrape_article(article)

                articles_dictionary[article] = article_info

            except Exception as e:
                unscrapeable_article_dict[article] = str(e)
                # screen.end_session()
                # print e
                # exit()

        return articles_dictionary, unscrapeable_article_dict


class GremlinZapper(object):
    """
    Class to convert windows cp1252 characters to unicode characters or
    to convert cp1252 and unicode characters to their ascii equivalents
    """

    def __init__(self):

        self.gremlin_regex_1252 = re.compile(r"[\x00-\xff]")

        self.cp1252 = {
            "0x00": "0x0000",   # NULL
            "0x01": "0x0001",   # START OF HEADING
            "0x02": "0x0002",   # START OF TEXT
            "0x03": "0x0003",   # END OF TEXT
            "0x04": "0x0004",   # END OF TRANSMISSION
            "0x05": "0x0005",   # ENQUIRY
            "0x06": "0x0006",   # ACKNOWLEDGE
            "0x07": "0x0007",   # BELL
            "0x08": "0x0008",   # BACKSPACE
            "0x09": "0x0009",   # HORIZONTAL TABULATION
            "0x0A": "0x000A",   # LINE FEED
            "0x0B": "0x000B",   # VERTICAL TABULATION
            "0x0C": "0x000C",   # FORM FEED
            "0x0D": "0x000D",   # CARRIAGE RETURN
            "0x0E": "0x000E",   # SHIFT OUT
            "0x0F": "0x000F",   # SHIFT IN
            "0x10": "0x0010",   # DATA LINK ESCAPE
            "0x11": "0x0011",   # DEVICE CONTROL ONE
            "0x12": "0x0012",   # DEVICE CONTROL TWO
            "0x13": "0x0013",   # DEVICE CONTROL THREE
            "0x14": "0x0014",   # DEVICE CONTROL FOUR
            "0x15": "0x0015",   # NEGATIVE ACKNOWLEDGE
            "0x16": "0x0016",   # SYNCHRONOUS IDLE
            "0x17": "0x0017",   # END OF TRANSMISSION BLOCK
            "0x18": "0x0018",   # CANCEL
            "0x19": "0x0019",   # END OF MEDIUM
            "0x1A": "0x001A",   # SUBSTITUTE
            "0x1B": "0x001B",   # ESCAPE
            "0x1C": "0x001C",   # FILE SEPARATOR
            "0x1D": "0x001D",   # GROUP SEPARATOR
            "0x1E": "0x001E",   # RECORD SEPARATOR
            "0x1F": "0x001F",   # UNIT SEPARATOR
            "0x20": "0x0020",   # SPACE
            "0x21": "0x0021",   # EXCLAMATION MARK
            "0x22": "0x0022",   # QUOTATION MARK
            "0x23": "0x0023",   # NUMBER SIGN
            "0x24": "0x0024",   # DOLLAR SIGN
            "0x25": "0x0025",   # PERCENT SIGN
            "0x26": "0x0026",   # AMPERSAND
            "0x27": "0x0027",   # APOSTROPHE
            "0x28": "0x0028",   # LEFT PARENTHESIS
            "0x29": "0x0029",   # RIGHT PARENTHESIS
            "0x2A": "0x002A",   # ASTERISK
            "0x2B": "0x002B",   # PLUS SIGN
            "0x2C": "0x002C",   # COMMA
            "0x2D": "0x002D",   # HYPHEN-MINUS
            "0x2E": "0x002E",   # FULL STOP
            "0x2F": "0x002F",   # SOLIDUS
            "0x30": "0x0030",   # DIGIT ZERO
            "0x31": "0x0031",   # DIGIT ONE
            "0x32": "0x0032",   # DIGIT TWO
            "0x33": "0x0033",   # DIGIT THREE
            "0x34": "0x0034",   # DIGIT FOUR
            "0x35": "0x0035",   # DIGIT FIVE
            "0x36": "0x0036",   # DIGIT SIX
            "0x37": "0x0037",   # DIGIT SEVEN
            "0x38": "0x0038",   # DIGIT EIGHT
            "0x39": "0x0039",   # DIGIT NINE
            "0x3A": "0x003A",   # COLON
            "0x3B": "0x003B",   # SEMICOLON
            "0x3C": "0x003C",   # LESS-THAN SIGN
            "0x3D": "0x003D",   # EQUALS SIGN
            "0x3E": "0x003E",   # GREATER-THAN SIGN
            "0x3F": "0x003F",   # QUESTION MARK
            "0x40": "0x0040",   # COMMERCIAL AT
            "0x41": "0x0041",   # LATIN CAPITAL LETTER A
            "0x42": "0x0042",   # LATIN CAPITAL LETTER B
            "0x43": "0x0043",   # LATIN CAPITAL LETTER C
            "0x44": "0x0044",   # LATIN CAPITAL LETTER D
            "0x45": "0x0045",   # LATIN CAPITAL LETTER E
            "0x46": "0x0046",   # LATIN CAPITAL LETTER F
            "0x47": "0x0047",   # LATIN CAPITAL LETTER G
            "0x48": "0x0048",   # LATIN CAPITAL LETTER H
            "0x49": "0x0049",   # LATIN CAPITAL LETTER I
            "0x4A": "0x004A",   # LATIN CAPITAL LETTER J
            "0x4B": "0x004B",   # LATIN CAPITAL LETTER K
            "0x4C": "0x004C",   # LATIN CAPITAL LETTER L
            "0x4D": "0x004D",   # LATIN CAPITAL LETTER M
            "0x4E": "0x004E",   # LATIN CAPITAL LETTER N
            "0x4F": "0x004F",   # LATIN CAPITAL LETTER O
            "0x50": "0x0050",   # LATIN CAPITAL LETTER P
            "0x51": "0x0051",   # LATIN CAPITAL LETTER Q
            "0x52": "0x0052",   # LATIN CAPITAL LETTER R
            "0x53": "0x0053",   # LATIN CAPITAL LETTER S
            "0x54": "0x0054",   # LATIN CAPITAL LETTER T
            "0x55": "0x0055",   # LATIN CAPITAL LETTER U
            "0x56": "0x0056",   # LATIN CAPITAL LETTER V
            "0x57": "0x0057",   # LATIN CAPITAL LETTER W
            "0x58": "0x0058",   # LATIN CAPITAL LETTER X
            "0x59": "0x0059",   # LATIN CAPITAL LETTER Y
            "0x5A": "0x005A",   # LATIN CAPITAL LETTER Z
            "0x5B": "0x005B",   # LEFT SQUARE BRACKET
            "0x5C": "0x005C",   # REVERSE SOLIDUS
            "0x5D": "0x005D",   # RIGHT SQUARE BRACKET
            "0x5E": "0x005E",   # CIRCUMFLEX ACCENT
            "0x5F": "0x005F",   # LOW LINE
            "0x60": "0x0060",   # GRAVE ACCENT
            "0x61": "0x0061",   # LATIN SMALL LETTER A
            "0x62": "0x0062",   # LATIN SMALL LETTER B
            "0x63": "0x0063",   # LATIN SMALL LETTER C
            "0x64": "0x0064",   # LATIN SMALL LETTER D
            "0x65": "0x0065",   # LATIN SMALL LETTER E
            "0x66": "0x0066",   # LATIN SMALL LETTER F
            "0x67": "0x0067",   # LATIN SMALL LETTER G
            "0x68": "0x0068",   # LATIN SMALL LETTER H
            "0x69": "0x0069",   # LATIN SMALL LETTER I
            "0x6A": "0x006A",   # LATIN SMALL LETTER J
            "0x6B": "0x006B",   # LATIN SMALL LETTER K
            "0x6C": "0x006C",   # LATIN SMALL LETTER L
            "0x6D": "0x006D",   # LATIN SMALL LETTER M
            "0x6E": "0x006E",   # LATIN SMALL LETTER N
            "0x6F": "0x006F",   # LATIN SMALL LETTER O
            "0x70": "0x0070",   # LATIN SMALL LETTER P
            "0x71": "0x0071",   # LATIN SMALL LETTER Q
            "0x72": "0x0072",   # LATIN SMALL LETTER R
            "0x73": "0x0073",   # LATIN SMALL LETTER S
            "0x74": "0x0074",   # LATIN SMALL LETTER T
            "0x75": "0x0075",   # LATIN SMALL LETTER U
            "0x76": "0x0076",   # LATIN SMALL LETTER V
            "0x77": "0x0077",   # LATIN SMALL LETTER W
            "0x78": "0x0078",   # LATIN SMALL LETTER X
            "0x79": "0x0079",   # LATIN SMALL LETTER Y
            "0x7A": "0x007A",   # LATIN SMALL LETTER Z
            "0x7B": "0x007B",   # LEFT CURLY BRACKET
            "0x7C": "0x007C",   # VERTICAL LINE
            "0x7D": "0x007D",   # RIGHT CURLY BRACKET
            "0x7E": "0x007E",   # TILDE
            "0x7F": "0x007F",   # DELETE
            "0x80": "0x20AC",   # EURO SIGN
            "0x82": "0x201A",   # SINGLE LOW-9 QUOTATION MARK
            "0x83": "0x0192",   # LATIN SMALL LETTER F WITH HOOK
            "0x84": "0x201E",   # DOUBLE LOW-9 QUOTATION MARK
            "0x85": "0x2026",   # HORIZONTAL ELLIPSIS
            "0x86": "0x2020",   # DAGGER
            "0x87": "0x2021",   # DOUBLE DAGGER
            "0x88": "0x02C6",   # MODIFIER LETTER CIRCUMFLEX ACCENT
            "0x89": "0x2030",   # PER MILLE SIGN
            "0x8A": "0x0160",   # LATIN CAPITAL LETTER S WITH CARON
            "0x8B": "0x2039",   # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
            "0x8C": "0x0152",   # LATIN CAPITAL LIGATURE OE
            "0x8E": "0x017D",   # LATIN CAPITAL LETTER Z WITH CARON
            "0x91": "0x2018",   # LEFT SINGLE QUOTATION MARK
            "0x92": "0x2019",   # RIGHT SINGLE QUOTATION MARK
            "0x93": "0x201C",   # LEFT DOUBLE QUOTATION MARK
            "0x94": "0x201D",   # RIGHT DOUBLE QUOTATION MARK
            "0x95": "0x2022",   # BULLET
            "0x96": "0x2013",   # EN DASH
            "0x97": "0x2014",   # EM DASH
            "0x98": "0x02DC",   # SMALL TILDE
            "0x99": "0x2122",   # TRADE MARK SIGN
            "0x9A": "0x0161",   # LATIN SMALL LETTER S WITH CARON
            "0x9B": "0x203A",   # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
            "0x9C": "0x0153",   # LATIN SMALL LIGATURE OE
            "0x9E": "0x017E",   # LATIN SMALL LETTER Z WITH CARON
            "0x9F": "0x0178",   # LATIN CAPITAL LETTER Y WITH DIAERESIS
            "0xA0": "0x00A0",   # NO-BREAK SPACE
            "0xA1": "0x00A1",   # INVERTED EXCLAMATION MARK
            "0xA2": "0x00A2",   # CENT SIGN
            "0xA3": "0x00A3",   # POUND SIGN
            "0xA4": "0x00A4",   # CURRENCY SIGN
            "0xA5": "0x00A5",   # YEN SIGN
            "0xA6": "0x00A6",   # BROKEN BAR
            "0xA7": "0x00A7",   # SECTION SIGN
            "0xA8": "0x00A8",   # DIAERESIS
            "0xA9": "0x00A9",   # COPYRIGHT SIGN
            "0xAA": "0x00AA",   # FEMININE ORDINAL INDICATOR
            "0xAB": "0x00AB",   # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
            "0xAC": "0x00AC",   # NOT SIGN
            "0xAD": "0x00AD",   # SOFT HYPHEN
            "0xAE": "0x00AE",   # REGISTERED SIGN
            "0xAF": "0x00AF",   # MACRON
            "0xB0": "0x00B0",   # DEGREE SIGN
            "0xB1": "0x00B1",   # PLUS-MINUS SIGN
            "0xB2": "0x00B2",   # SUPERSCRIPT TWO
            "0xB3": "0x00B3",   # SUPERSCRIPT THREE
            "0xB4": "0x00B4",   # ACUTE ACCENT
            "0xB5": "0x00B5",   # MICRO SIGN
            "0xB6": "0x00B6",   # PILCROW SIGN
            "0xB7": "0x00B7",   # MIDDLE DOT
            "0xB8": "0x00B8",   # CEDILLA
            "0xB9": "0x00B9",   # SUPERSCRIPT ONE
            "0xBA": "0x00BA",   # MASCULINE ORDINAL INDICATOR
            "0xBB": "0x00BB",   # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
            "0xBC": "0x00BC",   # VULGAR FRACTION ONE QUARTER
            "0xBD": "0x00BD",   # VULGAR FRACTION ONE HALF
            "0xBE": "0x00BE",   # VULGAR FRACTION THREE QUARTERS
            "0xBF": "0x00BF",   # INVERTED QUESTION MARK
            "0xC0": "0x00C0",   # LATIN CAPITAL LETTER A WITH GRAVE
            "0xC1": "0x00C1",   # LATIN CAPITAL LETTER A WITH ACUTE
            "0xC2": "0x00C2",   # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
            "0xC3": "0x00C3",   # LATIN CAPITAL LETTER A WITH TILDE
            "0xC4": "0x00C4",   # LATIN CAPITAL LETTER A WITH DIAERESIS
            "0xC5": "0x00C5",   # LATIN CAPITAL LETTER A WITH RING ABOVE
            "0xC6": "0x00C6",   # LATIN CAPITAL LETTER AE
            "0xC7": "0x00C7",   # LATIN CAPITAL LETTER C WITH CEDILLA
            "0xC8": "0x00C8",   # LATIN CAPITAL LETTER E WITH GRAVE
            "0xC9": "0x00C9",   # LATIN CAPITAL LETTER E WITH ACUTE
            "0xCA": "0x00CA",   # LATIN CAPITAL LETTER E WITH CIRCUMFLEX
            "0xCB": "0x00CB",   # LATIN CAPITAL LETTER E WITH DIAERESIS
            "0xCC": "0x00CC",   # LATIN CAPITAL LETTER I WITH GRAVE
            "0xCD": "0x00CD",   # LATIN CAPITAL LETTER I WITH ACUTE
            "0xCE": "0x00CE",   # LATIN CAPITAL LETTER I WITH CIRCUMFLEX
            "0xCF": "0x00CF",   # LATIN CAPITAL LETTER I WITH DIAERESIS
            "0xD0": "0x00D0",   # LATIN CAPITAL LETTER ETH
            "0xD1": "0x00D1",   # LATIN CAPITAL LETTER N WITH TILDE
            "0xD2": "0x00D2",   # LATIN CAPITAL LETTER O WITH GRAVE
            "0xD3": "0x00D3",   # LATIN CAPITAL LETTER O WITH ACUTE
            "0xD4": "0x00D4",   # LATIN CAPITAL LETTER O WITH CIRCUMFLEX
            "0xD5": "0x00D5",   # LATIN CAPITAL LETTER O WITH TILDE
            "0xD6": "0x00D6",   # LATIN CAPITAL LETTER O WITH DIAERESIS
            "0xD7": "0x00D7",   # MULTIPLICATION SIGN
            "0xD8": "0x00D8",   # LATIN CAPITAL LETTER O WITH STROKE
            "0xD9": "0x00D9",   # LATIN CAPITAL LETTER U WITH GRAVE
            "0xDA": "0x00DA",   # LATIN CAPITAL LETTER U WITH ACUTE
            "0xDB": "0x00DB",   # LATIN CAPITAL LETTER U WITH CIRCUMFLEX
            "0xDC": "0x00DC",   # LATIN CAPITAL LETTER U WITH DIAERESIS
            "0xDD": "0x00DD",   # LATIN CAPITAL LETTER Y WITH ACUTE
            "0xDE": "0x00DE",   # LATIN CAPITAL LETTER THORN
            "0xDF": "0x00DF",   # LATIN SMALL LETTER SHARP S
            "0xE0": "0x00E0",   # LATIN SMALL LETTER A WITH GRAVE
            "0xE1": "0x00E1",   # LATIN SMALL LETTER A WITH ACUTE
            "0xE2": "0x00E2",   # LATIN SMALL LETTER A WITH CIRCUMFLEX
            "0xE3": "0x00E3",   # LATIN SMALL LETTER A WITH TILDE
            "0xE4": "0x00E4",   # LATIN SMALL LETTER A WITH DIAERESIS
            "0xE5": "0x00E5",   # LATIN SMALL LETTER A WITH RING ABOVE
            "0xE6": "0x00E6",   # LATIN SMALL LETTER AE
            "0xE7": "0x00E7",   # LATIN SMALL LETTER C WITH CEDILLA
            "0xE8": "0x00E8",   # LATIN SMALL LETTER E WITH GRAVE
            "0xE9": "0x00E9",   # LATIN SMALL LETTER E WITH ACUTE
            "0xEA": "0x00EA",   # LATIN SMALL LETTER E WITH CIRCUMFLEX
            "0xEB": "0x00EB",   # LATIN SMALL LETTER E WITH DIAERESIS
            "0xEC": "0x00EC",   # LATIN SMALL LETTER I WITH GRAVE
            "0xED": "0x00ED",   # LATIN SMALL LETTER I WITH ACUTE
            "0xEE": "0x00EE",   # LATIN SMALL LETTER I WITH CIRCUMFLEX
            "0xEF": "0x00EF",   # LATIN SMALL LETTER I WITH DIAERESIS
            "0xF0": "0x00F0",   # LATIN SMALL LETTER ETH
            "0xF1": "0x00F1",   # LATIN SMALL LETTER N WITH TILDE
            "0xF2": "0x00F2",   # LATIN SMALL LETTER O WITH GRAVE
            "0xF3": "0x00F3",   # LATIN SMALL LETTER O WITH ACUTE
            "0xF4": "0x00F4",   # LATIN SMALL LETTER O WITH CIRCUMFLEX
            "0xF5": "0x00F5",   # LATIN SMALL LETTER O WITH TILDE
            "0xF6": "0x00F6",   # LATIN SMALL LETTER O WITH DIAERESIS
            "0xF7": "0x00F7",   # DIVISION SIGN
            "0xF8": "0x00F8",   # LATIN SMALL LETTER O WITH STROKE
            "0xF9": "0x00F9",   # LATIN SMALL LETTER U WITH GRAVE
            "0xFA": "0x00FA",   # LATIN SMALL LETTER U WITH ACUTE
            "0xFB": "0x00FB",   # LATIN SMALL LETTER U WITH CIRCUMFLEX
            "0xFC": "0x00FC",   # LATIN SMALL LETTER U WITH DIAERESIS
            "0xFD": "0x00FD",   # LATIN SMALL LETTER Y WITH ACUTE
            "0xFE": "0x00FE",   # LATIN SMALL LETTER THORN
            "0xFF": "0x00FF",   # LATIN SMALL LETTER Y WITH DIAERESIS
        }

    def kill_gremlins(self, text):
        """
        From http://effbot.org/zone/unicode-gremlins.htm
        map cp1252 gremlins to real unicode characters
        :return:
        """

        if re.search(u"[\x80-\x9f]", text):
            def fixup(m):
                s = m.group(0)
                return self.cp1252.get(s, s)

            if isinstance(text, type("")):
                # make sure we have a unicode string
                text = unicode(text, "iso-8859-1")
            text = re.sub(self.gremlin_regex_1252, fixup, text)
        return text

    def zap_string(self, the_string):
        """
        Converts any Windows cp1252 or unicode characters in a string to ASCII equivalents
        :param the_string: the string to perform the conversion on
        :return: input string with gremlins replaced
        """
        the_string = self.kill_gremlins(the_string)
        if isinstance(the_string, unicode):
            the_string = unidecode(the_string)
        return the_string