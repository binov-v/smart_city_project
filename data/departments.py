import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy import orm, ForeignKey
from sqlalchemy_serializer import SerializerMixin


class Department(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'departments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chief = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("users.id"))
    chief_rel = orm.relationship("User", foreign_keys=[chief], back_populates="dep_rel")
    ticket_dep_rel = orm.relationship("Ticket", back_populates="dep_rel")