from flask_wtf import Form
from wtforms import StringField, BooleanField, ValidationError
from wtforms.validators import DataRequired, URL
import tldextract

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
        print "=============================================================="

