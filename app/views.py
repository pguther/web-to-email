from flask import render_template, flash, redirect, url_for, request
from app import app
from forms import URLForm
from utils import PageScraper, scrape_level3_page


@app.route('/', methods=['GET', ])
def index():
    form = URLForm()
    if 'url' in request.args:
        url = request.args.get('url')
        form.url.data = url
        if form.validate():
            article_dictionary, template = scrape_level3_page(url)

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
        """
        if form.validate_on_submit():
            url = request.form['url']
            article_dictionary, template = scrape_level3_page(url)

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
        flash_errors(form)
        """
        return render_template('index.html',
                               form=URLForm())


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error)
