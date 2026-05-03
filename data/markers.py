import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin


class Marker(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'markers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    lat = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    lon = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ticket_mark_rel = orm.relationship("Ticket", back_populates="marker_rel")