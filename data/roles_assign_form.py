from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField


class FindUserForm(FlaskForm):
    mail_or_surname = StringField('Напишите почту или фамилию пользователя')
    submit = SubmitField('Поиск')