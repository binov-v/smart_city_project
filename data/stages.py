import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin


class Stage(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'stages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ticket_stage_rel = orm.relationship("Ticket", back_populates="stage_rel")