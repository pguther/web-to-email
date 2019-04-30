from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, URL
from .form_validators import MessagingURl


class URLForm(FlaskForm):
    url = StringField('url', validators=[DataRequired(), URL(), MessagingURl()])
