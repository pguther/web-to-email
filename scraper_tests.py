from premailer import Premailer
from bs4 import BeautifulSoup
from app.utils import scrape_level3_page
import pprint

article_dictionary = scrape_level3_page('http://history.ucsc.edu/graduate/index.html')

pp = pprint.PrettyPrinter(indent=4)

pp.pprint(article_dictionary)


