import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy import orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin


class Ticket(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tickets'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    appeal_creator = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("users.id"))
    appeal_text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    appeal_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    appeal_photo_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_solved = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    stated_department = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("departments.id"), nullable=True)
    dep_rel = orm.relationship("Department", back_populates="ticket_rel")

    owner = orm.relationship("User", back_populates="tickets")
