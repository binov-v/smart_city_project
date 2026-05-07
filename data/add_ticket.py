from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class AddTicketForm(FlaskForm):
    type = SelectField(
        'Выберите категорию обращения',
        validators=[DataRequired(message="Пожалуйста, выберите категорию")],
        choices=[
            ('', 'Выберите вариант...'),
            ('transport', 'Дороги и транспорт'),
            ('improvement', 'Благоустройство и экология'),
            ('communal', 'ЖКХ'),
            ('safety', 'Безопасность и правопорядок')
        ]
    )
    textarea = TextAreaField('Опишите вашу проблему')
    submit = SubmitField('Отправить')