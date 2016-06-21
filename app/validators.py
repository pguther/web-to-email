from wtforms import ValidationError
import tldextract
import requests
from bs4 import BeautifulSoup


class Level3Url(object):
    """
    Validates that a URL points at a level 3 UCSC content page
    """

    def __call__(self, form, field):
        ext = tldextract.extract(field.data)
        if ext.domain != 'ucsc':
            raise ValidationError('URL must belong to a UCSC domain')

        r = requests.get(field.data)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        if r.headers['content-type'] != 'text/html; charset=UTF-8':
            raise ValidationError('Content not HTML')
        soup = BeautifulSoup(r.content, 'lxml')

        body = soup.find("body")

        valid = False

        if 'class' in body.attrs:
            for class_tag in body.attrs['class']:
                if class_tag == 'left-column':
                    valid = True

        if not valid:
            raise ValidationError('URL is not a level 3 UCSC page')