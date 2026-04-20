import sqlalchemy

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Role(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'roles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    role_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    users = orm.relationship("User", back_populates="role")