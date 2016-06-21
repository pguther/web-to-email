from flask_wtf import Form
from wtforms import StringField, BooleanField, ValidationError
from wtforms.validators import DataRequired, URL
import tldextract
import requests
from bs4 import BeautifulSoup

class URLForm(Form):
    url = StringField('url', validators=[DataRequired(), URL()])

    @staticmethod
    def validate_url(form, field):
        print "============================Validator========================="
        print str(field.data)
        ext = tldextract.extract(field.data)
        if ext.domain != 'ucsc':
            raise ValidationError('URL must belong to a UCSC domain')
        print str(ext)

        r = requests.get(field.data)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        if r.headers['content-type'] != 'text/html; charset=UTF-8':
            raise ValidationError('Content not HTML')
        soup = BeautifulSoup(r.content, 'lxml')

        body = soup.find("body")

        valid = False

        print str(body.attrs)

        if 'class' in body.attrs:
            for class_tag in body.attrs['class']:
                if class_tag == 'left-column':
                    valid = True

        if not valid:
            raise ValidationError('URL is not a level 3 UCSC page')

        print "=============================================================="

