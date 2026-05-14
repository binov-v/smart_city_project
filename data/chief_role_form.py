from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired


class SelectRoleForm(FlaskForm):
    type = SelectField(''
                       'Выберите департамент',
                       choices=[
                           ('transport', 'Дороги и транспорт'),
                           ('improvement_and_eco', 'Благоустройство и экология'),
                           ('communal', 'ЖКХ'),
                           ('safety', 'Безопасность и правопорядок')
                       ]
                       )
    role_field = RadioField(''
                            'Роль',
                            choices=[
                                ('1', 'Админ'),
                                ('3', 'Модератор'),
                                ('2', 'Глава департамента'),
                                ('4', 'Пользователь')
                            ]
                            )
    save_button = SubmitField('Сохранить')
