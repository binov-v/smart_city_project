import requests
import datetime

from flask import Flask, render_template, redirect, request, abort, url_for
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user, login_required

from data import db_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.add_ticket import AddTicketForm
from data.chief_role_form import SelectRoleForm
from data.roles_assign_form import FindUserForm
from data.tickets import Ticket
from data.markers import Marker
from data.users import User
from data import tickets_resource, markers_resource
from data import users_resource
from data.departments import Department
from data.stages import Stage
from flask_restful import reqparse, abort, Api, Resource
import uuid
import json
from waitress import serve

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/tickets'
app = Flask(__name__)
api = Api(app)
api.add_resource(tickets_resource.TicketsListResource, '/api/v1/tickets')
api.add_resource(tickets_resource.TicketResource, '/api/v1/tickets/<int:tick_id>')
api.add_resource(markers_resource.MarkersListResource, '/api/v1/markers')
api.add_resource(users_resource.UsersListResource, '/api/v1/users')

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    try:
        return session.get(User, int(user_id))
    finally:
        session.close()


@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect('/master')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            try:
                user = session.query(User).filter(User.email == form.email.data).first()
                if user and user.check_password(form.password.data):
                    login_user(user, remember=True)
                    return redirect('/master')
                return render_template('index.html', message="Неправильный логин или пароль", form=form)
            finally:
                session.close()

    return render_template('index.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        try:
            if session.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                email=form.email.data,
                name=form.name.data,
                surname=form.surname.data,
                age=form.age.data,
                address=form.address.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/')
        finally:
            session.close()
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/master', methods=['GET', 'POST'])
@login_required
def master_page():
    return render_template('master.html')


@app.route('/tickets/<int:tick_id>', methods=['GET', 'POST'])
@login_required
def one_ticket(tick_id):
    response = requests.get(f'http://localhost:5000/api/v1/tickets/{tick_id}')
    if response.status_code == 200:
        data = response.json()
        user_ticket = data.get('ticket')
    else:
        user_ticket = None
    return render_template('ticket_info.html', user_ticket=user_ticket, is_it_for_moder=False, is_it_for_chief=False)


@app.route('/tickets/department_solution/<int:tick_id>', methods=['GET', 'POST'])
@login_required
def ticket_solution(tick_id):
    response = requests.get(f'http://localhost:5000/api/v1/tickets/{tick_id}')
    if response.status_code == 200:
        data = response.json()
        user_ticket = data.get('ticket')
    else:
        user_ticket = None

    if request.method == 'POST':
        answer_text = request.form.get('answer_text')
        file = request.files.get('file')

        relative_path = None
        file_path = None

        if file and file.filename:
            filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            relative_path = f"uploads/tickets/{filename}"

            file.save(file_path)

        session = db_session.create_session()
        try:
            ticket = session.query(Ticket).filter(Ticket.id == tick_id).first()

            ticket.answer_text = answer_text
            ticket.answer_file_path = relative_path
            ticket.process_level = 3

            session.commit()
        finally:
            session.close()

        return redirect(url_for('ticket_solution', tick_id=tick_id))

    return render_template('ticket_info.html', user_ticket=user_ticket, is_it_for_moder=False, is_it_for_chief=True)


@app.route('/tickets/department_solution', methods=['GET', 'POST'])
@login_required
def list_department_ticket():
    session = db_session.create_session()
    dep = session.query(Department.id).filter(Department.chief == current_user.id).first()
    dep_id = dep[0] if dep else None

    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id')
        chief_note = request.form.get('chief_note')

        ticket = session.query(Ticket).filter(Ticket.id == ticket_id, Ticket.stated_department == dep_id).first()
        if ticket:
            ticket.chief_note = chief_note
            session.commit()
        session.close()
        return redirect(url_for('list_department_ticket'))

    response = requests.get('http://localhost:5000/api/v1/tickets', params={'for_department': dep_id})
    data = response.json()
    user_tickets = data.get('tickets', [])
    session.close()

    return render_template('tickets.html', list_tickets=user_tickets, is_it_for_moder=False, is_it_for_chief=True)


@app.route('/tickets', methods=['GET', 'POST'])
@login_required
def list_user_ticket():
    response = requests.get('http://localhost:5000/api/v1/tickets', params={'user_id': current_user.id})
    data = response.json()
    user_tickets = data.get('tickets', [])
    return render_template('tickets.html', list_tickets=user_tickets, is_it_for_moder=False, is_it_for_chief=False)


@app.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    form = AddTicketForm()

    if form.validate_on_submit():
        if form.submit.data:
            file = form.file.data
            relative_path = None
            file_path = None

            if file:
                filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                relative_path = f"uploads/tickets/{filename}"
            else:
                return render_template('add_ticket.html', form=form, message="Приложите файл с фото")

            coodinates_str = form.coords.data
            if not coodinates_str:
                return render_template('add_ticket.html', form=form, message="Пожалуйста, укажите место на карте!")

            if not form.textarea.data:
                return render_template('add_ticket.html', form=form, message="Обязательно опишите проблему")

            coodinates_list = json.loads(coodinates_str)
            session = db_session.create_session()
            try:

                marker = Marker(lat=str(coodinates_list[0]),
                                lon=str(coodinates_list[1]))
                session.add(marker)
                session.commit()

                dep = {
                    'transport': 1,
                    'improvement_and_eco': 2,
                    'communal': 3,
                    'safety': 4
                }

                if form.type.data not in dep:
                    return render_template('add_ticket.html', form=form, message="Некорректный тип обращения")
                ticket = Ticket(
                    appeal_creator=current_user.id,
                    appeal_text=form.textarea.data,
                    appeal_photo_path=relative_path,
                    process_level=1,
                    marker_id=marker.id,
                    stated_department=dep[form.type.data]
                )
                file.save(file_path)
                session.add(ticket)
                session.commit()

                return redirect('/tickets')
            finally:
                session.close()

    return render_template('add_ticket.html', form=form)


@app.route('/users', methods=['GET', 'POST'])
@login_required
def list_of_users():
    if current_user.user_role == 1 or current_user.user_role == 3:
        form = FindUserForm()
        if form.validate_on_submit():
            response = requests.get('http://localhost:5000/api/v1/users', params={'keyword': form.mail_or_surname.data})
            data = response.json()
            return render_template('users.html', form=form, users_list=data)
        return render_template('users.html', form=form)


@app.route('/users/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_role(id):
    if current_user.user_role == 1:
        session = db_session.create_session()
        user = session.query(User).filter(User.id == id).first()
        try:
            form = SelectRoleForm()
            if request.method == 'GET':
                form.role_field.data = str(user.user_role) if user.user_role else '4'

            if form.validate_on_submit():
                dept = None
                if form.save_button.data:
                    if form.role_field.data == '2':
                        dept = session.query(Department).filter(Department.title == form.type.data).first()
                        if dept:
                            past_chief = session.query(User).filter(User.id == dept.chief).first()
                            if past_chief:
                                if past_chief.user_role != 1:
                                    past_chief.user_role = None
                                    past_chief.modified_date = datetime.datetime.now()

                            dept.chief = user.id

                        user.user_role = int(form.role_field.data) if form.role_field.data in ('1', '2', '3') else None
                        user.modified_date = datetime.datetime.now()
                    elif form.role_field.data in ('1', '3', '4'):
                        dept = session.query(Department).filter(Department.chief == user.id).first()
                        if dept:
                            dept.chief = None
                        if form.role_field.data == '4':
                            user.user_role = None
                        else:
                            user.user_role = int(form.role_field.data)
                        user.modified_date = datetime.datetime.now()
                    session.commit()
                    return redirect('/users')
            return render_template('assign_role.html', user=user, form=form)
        finally:
            session.close()


@app.route('/tickets/moderation')
@login_required
def tickets_list_moderation():
    response = requests.get('http://localhost:5000/api/v1/tickets', params={'moderation_stage': True})
    data = response.json()
    user_tickets = data.get('tickets', [])
    return render_template('tickets.html', list_tickets=user_tickets, is_it_for_moder=True, is_it_for_chief=False)


@app.route('/tickets/moderation/<int:tick_id>', methods=['GET', 'POST'])
@login_required
def ticket_moderation(tick_id):
    response = requests.get(f'http://localhost:5000/api/v1/tickets/{tick_id}')
    if response.status_code == 200:
        data = response.json()
        user_ticket = data.get('ticket')
    else:
        user_ticket = None

    if request.method == 'POST':
        session = db_session.create_session()
        try:
            ticket = session.query(Ticket).filter(Ticket.id == tick_id).first()
            button_value = request.form.get('action')
            if button_value == 'rejectBtn':
                ticket.process_level = 4
            elif button_value == 'confirmBtn':
                ticket.process_level = 2
                ticket.stated_department = request.form.get('department_name')
            session.commit()
            return redirect('/tickets/moderation')
        finally:
            session.close()

    return render_template('ticket_info.html', user_ticket=user_ticket, is_it_for_moder=True, is_it_for_chief=False)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init("db/smart_city.db")
    # app.run(host='localhost', port=5000)
    serve(app, host='localhost', port=5000)


if __name__ == '__main__':
    main()
