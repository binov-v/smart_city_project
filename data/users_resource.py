from flask_restful import Resource, abort, reqparse
from . import db_session
from data.users import User
from flask import jsonify
from sqlalchemy import or_

parser = reqparse.RequestParser()
parser.add_argument('keyword', required=True, type=str, location=['args'])


class UsersListResource(Resource):
    def get(self):
        args = parser.parse_args()
        keyword = args['keyword']

        session = db_session.create_session()
        try:

            users = session.query(User).filter(
                or_(
                    User.surname.ilike(f'%{keyword}%'),
                    User.email.ilike(f'%{keyword}%')
                )
            ).all()

            return jsonify(
                [
                    item.to_dict(only=('id', 'surname', 'name', 'age', 'address',
                                       'email', 'modified_date', 'user_role', 'department'))
                    for item in users
                ]
            )
        finally:
            session.close()


def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    try:
        users = session.query(User).get(user_id)
        if not users:
            abort(404, message=f"Users {user_id} not found")
    finally:
        session.close()
