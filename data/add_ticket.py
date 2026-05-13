from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, FileField, HiddenField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired


class AddTicketForm(FlaskForm):
    type = SelectField(
        'Выберите категорию обращения',
        validators=[DataRequired(message="Пожалуйста, выберите категорию")],
        choices=[
            ('', 'Выберите вариант...'),
            ('transport', 'Дороги и транспорт'),
            ('improvement_and_eco', 'Благоустройство и экология'),
            ('communal', 'ЖКХ'),
            ('safety', 'Безопасность и правопорядок')
        ]
    )
    textarea = TextAreaField('Опишите вашу проблему')
    coords = HiddenField()
    file = FileField('Фото проблемы (обязательно)', validators=[
        FileAllowed(['jpg', 'png', 'dng', 'jpeg', 'hevc'], 'Разрешены только изображения!')
    ])
    submit = SubmitField('Отправить')
