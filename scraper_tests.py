from premailer import Premailer
from bs4 import BeautifulSoup
from app.utils import PageScraper

scraper = PageScraper()

scraper.scrape_page('http://www.ucsc.edu/research/research-news.html')
