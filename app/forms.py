from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, URL
from .form_validators import MessagingURl


class URLForm(Form):
    url = StringField('url', validators=[DataRequired(), URL(), MessagingURl()])
