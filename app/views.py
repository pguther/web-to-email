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

            content, empty_tags, altless_images = scraper.scrape(url)

            return render_template(template, content=content)

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
