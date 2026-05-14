import requests
import datetime

from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user, login_required

from data import db_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.add_ticket import AddTicketForm
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
    return render_template('ticket_info.html', user_ticket=user_ticket, is_it_for_moder=False)


@app.route('/tickets', methods=['GET', 'POST'])
@login_required
def list_user_ticket():
    response = requests.get('http://localhost:5000/api/v1/tickets', params={'user_id': current_user.id})
    data = response.json()
    user_tickets = data.get('tickets', [])
    return render_template('tickets.html', list_tickets=user_tickets, is_it_for_moder=False)


@app.route('/tickets/new', methods=['GET', 'POST'])
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

                dep = {'transport': 1, 'improvement_and_eco': 2, 'communal': 3, 'safety': 4}
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
        try:
            user = session.query(User).filter(User.id == id).first()

            if request.method == 'POST':
                new_role = request.form.get('user_role')
                user.user_role = int(new_role)
                user.modified_date = datetime.datetime.now
                session.commit()
                return redirect(f'/users')
        finally:
            session.close()

        return render_template('assign_role.html', user=user)


@app.route('/tickets/moderation')
@login_required
def tickets_list_moderation():
    response = requests.get('http://localhost:5000/api/v1/tickets', params={'moderation_stage': True})
    data = response.json()
    user_tickets = data.get('tickets', [])
    return render_template('tickets.html', list_tickets=user_tickets, is_it_for_moder=True)


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

    return render_template('ticket_info.html', user_ticket=user_ticket, is_it_for_moder=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


#
#
# @app.route('/addjob', methods=['GET', 'POST'])
# def addjob():
#     form = AddJobForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         job = Jobs(
#             job=form.job.data,
#             team_leader=form.team_leader.data,
#             work_size=form.work_size.data,
#             collaborators=form.collaborators.data,
#             is_finished=form.is_finished.data
#         )
#         category = db_sess.query(Category).get(form.category.data)
#         if category:
#             job.categories.append(category)
#         else:
#             pass
#
#         db_sess.add(job)
#         db_sess.commit()
#         return redirect('/')
#
#     return render_template('addjob.html', title='Adding a job', form=form)
#
#
# @app.route('/adddep', methods=['GET', 'POST'])
# def add_dep():
#     add_form = AddDepForm()
#     if add_form.validate_on_submit():
#         db_sess = db_session.create_session()
#         deps = Department(
#             title=add_form.title.data,
#             chief=add_form.chief.data,
#             members=add_form.members.data,
#             email=add_form.email.data
#         )
#         db_sess.add(deps)
#         db_sess.commit()
#         return redirect('/departments')
#     return render_template('adddep.html', title='Adding a department', form=add_form)
#
#
# @app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_job(id):
#     form = AddJobForm()
#     db_sess = db_session.create_session()
#     job = db_sess.query(Jobs).filter(Jobs.id == id).first()
#
#     if not job:
#         abort(404)
#     if job.team_leader != current_user.id and current_user.id != 1:
#         abort(403)
#
#     if request.method == "GET":
#         form.job.data = job.job
#         form.team_leader.data = job.team_leader
#         form.work_size.data = job.work_size
#         form.collaborators.data = job.collaborators
#         form.is_finished.data = job.is_finished
#
#         if job.categories:
#             form.category.data = job.categories[0].id
#
#     if form.validate_on_submit():
#         job.job = form.job.data
#         job.team_leader = form.team_leader.data
#         job.work_size = form.work_size.data
#         job.collaborators = form.collaborators.data
#         job.is_finished = form.is_finished.data
#
#         category = db_sess.query(Category).get(form.category.data)
#
#         if category:
#             job.categories = [category]
#         else:
#             job.categories = []
#         db_sess.commit()
#         return redirect('/')
#
#     return render_template('addjob.html', title='Редактирование работы', form=form)
#
#
# @app.route('/edit_dep/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_dep(id):
#     form = AddDepForm()
#     db_sess = db_session.create_session()
#     dep = db_sess.query(Department).filter(Department.id == id).first()
#
#     if not dep:
#         abort(404)
#     if dep.chief != current_user.id and current_user.id != 1:
#         abort(403)
#
#     if request.method == "GET":
#         form.title.data = dep.title
#         form.chief.data = dep.chief
#         form.email.data = dep.email
#         form.members.data = dep.members
#
#     if form.validate_on_submit():
#         dep.title = form.title.data
#         dep.chief = form.chief.data
#         dep.email = form.email.data
#         dep.members = form.members.data
#         db_sess.commit()
#         return redirect('/departments')
#
#     return render_template('adddep.html', title='Редактирование департамента', form=form)
#
#
# @app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
# @login_required
# def jobs_delete(id):
#     db_sess = db_session.create_session()
#     jobs = db_sess.query(Jobs).filter(Jobs.id == id,
#                                       Jobs.team_leader == current_user.id | current_user.id == 1,
#                                       ).first()
#     if jobs:
#         db_sess.delete(jobs)
#         db_sess.commit()
#     else:
#         abort(404)
#     return redirect('/')
#
#
# @app.route('/deps_delete/<int:id>', methods=['GET', 'POST'])
# @login_required
# def deps_delete(id):
#     db_sess = db_session.create_session()
#     deps = db_sess.query(Department).filter(Department.id == id,
#                                             Department.chief == current_user.id | current_user.id == 1,
#                                             ).first()
#     if deps:
#         db_sess.delete(deps)
#         db_sess.commit()
#     else:
#         abort(404)
#     return redirect('/departments')
#
#


def main():
    db_session.global_init("db/smart_city.db")
    # app.run(host='localhost', port=5000)
    serve(app, host='localhost', port=5000)


if __name__ == '__main__':
    main()
