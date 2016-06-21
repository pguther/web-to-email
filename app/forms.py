from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, URL
from validators import Level3Url


class URLForm(Form):
    url = StringField('url', validators=[DataRequired(), URL(), Level3Url()])
