from flask import render_template, flash, redirect, url_for, request
from app import app
from forms import URLForm
from utils import PageScraper


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    if form.validate_on_submit():
        # flash('Page Conversion requested for URL="%s"' % form.url.data)
        url = request.form['url']
        scraper = PageScraper()
        article_dictionary = scraper.scrape_page(url)
        return render_template('result.html', banner_image=article_dictionary['banner_image'],
                               title=article_dictionary['title'],
                               content=article_dictionary['content'])
    return render_template('index.html',
                           form=form)
