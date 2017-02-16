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

            content, errors = scraper.scrape(url)

            return render_template(template, content=content, errors=errors)

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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500