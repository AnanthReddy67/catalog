import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class GmailUser(Base):
    __tablename__ = 'gmailuser'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(220), nullable=False)


class SoapCompnayName(Base):
    __tablename__ = 'soapcompnayname'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey('gmailuser.id'))
    user = relationship(GmailUser, backref="soapcompnayname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class SoapName(Base):
    __tablename__ = 'soapname1'
    id = Column(Integer, primary_key=True)
    soapname = Column(String(350), nullable=False)
    launchyear = Column(String(150))
    rating = Column(String(150))
    weight = Column(String(150))
    soaptype = Column(String(150))
    price = Column(String(10))
    soapcompnaynameid = Column(Integer, ForeignKey('soapcompnayname.id'))
    soapcompnayname = relationship(
        SoapCompnayName, backref=backref('soapname', cascade='all, delete'))
    gmailuser_id = Column(Integer, ForeignKey('gmailuser.id'))
    gmailuser = relationship(GmailUser, backref="soapname1")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'soapname': self. soapname,
            'launchyear': self. launchyear,
            'price': self. price,
            'weight': self. weight,
            'rating': self. rating,
            'soaptype': self. soaptype,
            'id': self. id
        }

engin = create_engine('sqlite:///soaps.db')
Base.metadata.create_all(engin)
