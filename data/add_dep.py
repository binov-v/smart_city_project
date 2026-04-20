from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, EmailField
from wtforms.validators import DataRequired


class AddDepForm(FlaskForm):
    title = StringField('Dep Title', validators=[DataRequired()])
    chief = IntegerField('Chief id', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')