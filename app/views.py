from flask import render_template, flash, redirect, url_for, request
from app import app
from forms import URLForm


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    if form.validate_on_submit():
        # flash('Page Conversion requested for URL="%s"' % form.url.data)
        url = request.form['url']
        return redirect(url_for('result', url=url))
    return render_template('index.html',
                           form=form)


@app.route('/result')
def result():
    return render_template('result.html', url=request.args.get('url'))
