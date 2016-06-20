from app.utils import PageScraper

scraper = PageScraper()
article_dictionary = scraper.scrape_page('http://history.ucsc.edu/graduate/index.html')

print "title: " + str(article_dictionary['title'])

print "banner image: " + str(article_dictionary['banner_image'])

print "content: " + str(article_dictionary['content'])
