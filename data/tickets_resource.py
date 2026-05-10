from flask_restful import Resource, abort, reqparse
from . import db_session
from data.tickets import Ticket
from flask import jsonify

parser = reqparse.RequestParser()
parser.add_argument('user_id', required=True, type=int, location=['args'])


class TicketsListResource(Resource):
    def get(self):
        args = parser.parse_args()
        session = db_session.create_session()

        tickets = session.query(Ticket).filter(Ticket.appeal_creator == args['user_id']).all()

        return jsonify({
            'tickets': [
                item.to_dict(only=('id', 'appeal_creator', 'appeal_text', 'appeal_photo_path',
                                   'process_level', 'marker_id', 'created_date', 'stated_department'))
                for item in tickets
            ]
        })

class TicketResource(Resource):
    def get(self, tick_id):
        session = db_session.create_session()

        ticket = session.query(Ticket).filter(Ticket.id == tick_id).first()

        return jsonify({
            'ticket': [
                item.to_dict(only=('id', 'appeal_creator', 'appeal_text', 'appeal_photo_path',
                                   'process_level', 'marker_id', 'created_date', 'stated_department'))
                for item in ticket
            ]
        })



def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    users = session.query(Ticket).get(user_id)
    if not users:
        abort(404, message=f"Tickets {user_id} not found")