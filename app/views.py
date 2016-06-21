from flask import render_template, flash, redirect, url_for, request
from app import app
from forms import URLForm
from utils import PageScraper, scrape_level3_page
from validators import Level3Url
from wtforms.compat import iteritems


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    if 'url' in request.args:
        url = request.args.get('url')
        form.url.data = url

        if form.validate():
            article_dictionary = scrape_level3_page(url)
            return render_template('result.html', banner_image=article_dictionary['banner_image'],
                                   title=article_dictionary['title'],
                                   content=article_dictionary['content'])
        for field, errors in form.errors.items():
            for error in errors:
                flash(error)
        return redirect(url_for('index'))
    else:
        if form.validate_on_submit():
            # flash('Page Conversion requested for URL="%s"' % form.url.data)
            url = request.form['url']
            article_dictionary = scrape_level3_page(url)
            return render_template('result.html', banner_image=article_dictionary['banner_image'],
                                   title=article_dictionary['title'],
                                   content=article_dictionary['content'])
        return render_template('index.html',
                               form=form)

