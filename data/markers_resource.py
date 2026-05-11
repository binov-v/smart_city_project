from flask_restful import Resource, abort, reqparse
from . import db_session
from data.tickets import Ticket
from flask import jsonify



class MarkersListResource(Resource):
    def get(self):
        session = db_session.create_session()

        tickets_at_work = session.query(Ticket).filter(Ticket.process_level == 2).all()
        results = []
        for ticket in tickets_at_work:
            if ticket.marker_rel:
                results.append({
                    'id': ticket.id,
                    'lat': ticket.marker_rel.lat,
                    'lon': ticket.marker_rel.lon,
                    'title': f"Заявка №{ticket.id}",
                    'description': ticket.appeal_text,
                    'photo': ticket.appeal_photo_path
                })

        return jsonify(results)




def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    users = session.query(Ticket).get(user_id)
    if not users:
        abort(404, message=f"Tickets {user_id} not found")