from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user, login_required

from data import db_session
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.users import User
from data.add_job import AddJobForm
from data.add_dep import AddDepForm
from data.departments import Department
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).filter(User.email == form.email.data).first()
#         if user and user.check_password(form.password.data):
#             login_user(user, remember=form.remember_me.data)
#             return redirect("/")
#         return render_template('login.html',
#                                message="Неправильный логин или пароль",
#                                form=form)
#     return render_template('login.html', title='Авторизация', form=form)
#
#
@app.route("/login_or_register", methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return '<h1>Успешно вошли</h1>'
        return render_template('index.html', message="Неправильный логин или пароль", form=form)

    return render_template('index.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
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
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login_or_register')
    return render_template('register.html', title='Регистрация', form=form)


#
#
# @app.route("/departments")
# def departments():
#     db_sess = db_session.create_session()
#     deps = db_sess.query(Department).all()
#     return render_template('departments.html', deps=deps, title='Departments log')
#
#
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect('/')
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
    app.run()


if __name__ == '__main__':
    main()
