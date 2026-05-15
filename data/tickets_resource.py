from flask_restful import Resource, abort, reqparse
from . import db_session
from data.tickets import Ticket
from flask import jsonify

parser = reqparse.RequestParser()
parser.add_argument('user_id', required=False, type=int, location=['args'])
parser.add_argument('moderation_stage', type=bool, location=['args'])
parser.add_argument('for_department', type=int, location=['args'])


class TicketsListResource(Resource):
    def get(self):
        args = parser.parse_args()
        session = db_session.create_session()
        try:
            if args.get('user_id'):
                tickets = session.query(Ticket).filter(Ticket.appeal_creator == args['user_id']).all()

                return jsonify({
                    'tickets': [
                        item.to_dict(only=('id', 'appeal_creator', 'appeal_text', 'appeal_photo_path',
                                           'process_level', 'marker_id', 'created_date', 'stated_department'))
                        for item in tickets
                    ]
                })
            elif args.get('moderation_stage'):
                tickets = session.query(Ticket).filter(Ticket.process_level == 1).all()

                return jsonify({
                    'tickets': [
                        item.to_dict(only=('id', 'appeal_creator', 'appeal_text', 'appeal_photo_path',
                                           'process_level', 'marker_id', 'created_date', 'stated_department'))
                        for item in tickets
                    ]
                })
            elif args.get('for_department'):
                tickets_for_dep = session.query(Ticket).filter(Ticket.stated_department == args['for_department'], Ticket.process_level == 2).all()
                return jsonify({
                    'tickets': [
                        item.to_dict(only=('id', 'appeal_creator', 'appeal_text', 'appeal_photo_path',
                                           'process_level', 'marker_id', 'created_date', 'stated_department', 'chief_note'))
                        for item in tickets_for_dep
                    ]
                })
        finally:
            session.close()


class TicketResource(Resource):
    def get(self, tick_id):
        session = db_session.create_session()
        try:
            ticket = session.query(Ticket).filter(Ticket.id == tick_id).first()
            if not ticket:
                return jsonify({'message': 'Ticket not found'}), 404

            return jsonify({
                'ticket': ticket.to_dict(only=(
                    'id', 'appeal_creator', 'appeal_text', 'appeal_photo_path',
                    'process_level', 'marker_id', 'created_date', 'stated_department',
                    'dep_rel.chief_rel.name', 'appeal_answer_text', 'appeal_answer_photo_path', 'chief_note'
                ))
            })
        finally:
            session.close()


def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    try:
        ticket = session.get(Ticket, user_id)
        if not ticket:
            abort(404, message=f"Tickets {user_id} not found")
    finally:
        session.close()
