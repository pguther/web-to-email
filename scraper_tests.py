from premailer import Premailer
from bs4 import BeautifulSoup
from app.utils import PageScraper, ArticleScraper
import pprint

scraper = ArticleScraper()

article_dictionary = scraper.scrape_article('http://news.ucsc.edu/2016/06/archivist.html')

pp = pprint.PrettyPrinter(indent=4)

pp.pprint(article_dictionary)


