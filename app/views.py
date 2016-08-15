from flask import render_template, flash, redirect, url_for, request
from app import app
from forms import URLForm
from utils import MessagingScraper


@app.route('/', methods=['GET', ])
def index():
    form = URLForm()
    if 'url' in request.args:
        url = request.args.get('url')
        form.url.data = url
        if form.validate():

            template = 'result.html'
            scraper = MessagingScraper()

            article_dictionary = scraper.scrape(url)

            if 'banner_image' in article_dictionary:
                banner_image = article_dictionary['banner_image']
            else:
                banner_image = None

            if 'title' in article_dictionary:
                title = article_dictionary['title']
            else:
                title = None

            if 'content' in article_dictionary:
                content = article_dictionary['content']
            else:
                content = None

            return render_template(template, banner_image=banner_image,
                                   title=title,
                                   content=content)

        for field, errors in form.errors.items():
            for error in errors:
                flash(error)
        return redirect(url_for('index'))
    else:
        return render_template('index.html',
                               form=URLForm())


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error)
