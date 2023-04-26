import sqlalchemy as sq
from sqlalchemy import func
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Creator(Base):
    __tablename__ = 'creator'

    creator_id = sq.Column(sq.Integer, primary_key=True)
    creator_name = sq.Column(sq.String(length=30), nullable=False)
    creator_email = sq.Column(sq.String(length=45), unique=True, index=True, nullable=False)
    password = sq.Column(sq.String(length=32), nullable=False)

    advertisement_relationship = relationship('Advertisement', back_populates='creator_relationship', cascade='all, delete')


class Advertisement(Base):
    __tablename__ = 'advertisement'

    advertisement_id = sq.Column(sq.Integer, primary_key=True)
    advertisement_title = sq.Column(sq.String(length=100), nullable=False)
    advertisement_description = sq.Column(sq.String(length=100), nullable=False)
    advertisement_created_at = sq.Column(sq.DateTime, server_default=func.now())
    creator_id = sq.Column(sq.Integer, sq.ForeignKey('creator.creator_id'), nullable=False)

    creator_relationship = relationship('Creator', back_populates='advertisement_relationship')


def create_table(engine):
    Base.metadata.create_all(engine)
