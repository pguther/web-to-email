from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class URLForm(Form):
    url = StringField('url', validators=[DataRequired()])
