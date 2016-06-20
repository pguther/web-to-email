from premailer import Premailer
from bs4 import BeautifulSoup

premailer = Premailer(html="<p>Welcome to the Graduate Program, Department of History at the University of California, Santa Cruz.</p>",
                      external_styles=['app/static/ucsc.css',])

output = premailer.transform()

soup = BeautifulSoup(output, 'lxml')

body_contents = ''

for item in soup.body.contents:
    body_contents += str(item)
print "==========================================================="
print body_contents
