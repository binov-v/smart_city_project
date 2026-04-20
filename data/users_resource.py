from flask_restful import Resource, abort
from . import db_session
from users import User
from flask import jsonify
from werkzeug.security import generate_password_hash
from reqparse_user import parser


def set_password(password):
    return generate_password_hash(password)


class UsersResource(Resource):
    def get(self, users_id):
        abort_if_news_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.get(User, users_id)
        return jsonify(
            {
                'user':
                    [user.to_dict(only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address',
                                        'email', 'hashed_password'))]
            }
        )

    def delete(self, users_id):
        abort_if_news_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify(
            {
                'users': [
                    [item.to_dict(only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address',
                                        'email', 'hashed_password')) for item in users]
                ]
            }
        )

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        user = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            hashed_password=set_password(args['hashed_password'])

        )
        db_sess.add(user)
        db_sess.commit()
        return jsonify({'id': user.id})


def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"Users {user_id} not found")
