from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Soap_Setup import *

engine = create_engine('sqlite:///soaps.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
session.query(SoapCompnayName).delete()
session.query(SoapName).delete()
session.query(GmailUser).delete()
# Create sample users data
User1 = GmailUser(name="Ananthreddy Vennapusa",
                  email="ananthreddy67@gmail.com",)
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample SoapCompnay
Compnay1 = SoapCompnayName(name="KAMA AYURVEDA",
                           user_id=1)
session.add(Compnay1)
session.commit()

Compnay2 = SoapCompnayName(name="SOULFLOWER",
                           user_id=1)
session.add(Compnay2)
session.commit

Compnay3 = SoapCompnayName(name="HERMES",
                           user_id=1)
session.add(Compnay3)
session.commit()

Compnay4 = SoapCompnayName(name="KOZICARE",
                           user_id=1)
session.add(Compnay4)
session.commit()

Compnay5 = SoapCompnayName(name="L'OCCITANE",
                           user_id=1)
session.add(Compnay5)
session.commit()

Compnay6 = SoapCompnayName(name="BEARDO",
                           user_id=1)
session.add(Compnay6)
session.commit()

# Populare a bykes with models for testing
# Using different users for bykes names year also
Soap1 = SoapName(soapname="TURMERIC",
                 launchyear="2002",
                 price="650/-",
                 weight="125GM",
                 rating="9.2",
                 soaptype="100% Natural, Ideal for delicate skin",
                 soapcompnaynameid=1,
                 gmailuser_id=1)
session.add(Soap1)
session.commit()

Soap2 = SoapName(soapname="DEOD0RIZING CHARCOAL SOAP",
                 launchyear="2001",
                 price="340.00",
                 weight="150GM",
                 rating="9.2",
                 soaptype="Ultimate 24 Hours Body Odor Control",
                 soapcompnaynameid=2,
                 gmailuser_id=1)
session.add(Soap2)
session.commit()

Soap3 = SoapName(soapname="24 FAUBOURG PERFUMED SOAP",
                 launchyear="1837",
                 price="2,140.00",
                 weight="100ml/3.5oz",
                 rating="9.2",
                 soaptype="body",
                 soapcompnaynameid=3,
                 gmailuser_id=1)
session.add(Soap3)
session.commit()

Soap4 = SoapName(soapname="Skin Whitening Soap",
                 launchyear="1999",
                 price="285.00",
                 weight="75GM",
                 rating="9.2",
                 soaptype="100% Natural",
                 soapcompnaynameid=4,
                 gmailuser_id=1)
session.add(Soap4)
session.commit()

Soap5 = SoapName(soapname="Unisex Shea Butter And Verbena Extra Gentle Soap",
                 launchyear="2013",
                 price="510.00",
                 weight="100GM",
                 rating="9.2",
                 soaptype=" Natural body skin",
                 soapcompnaynameid=5,
                 gmailuser_id=1)
session.add(Soap5)
session.commit()

Soap6 = SoapName(soapname="Activated Charcoal Brick Soap",
                 launchyear="2018",
                 price="195.00",
                 weight="125GM",
                 rating="9.2",
                 soaptype="body",
                 soapcompnaynameid=6,
                 gmailuser_id=1)
session.add(Soap6)
session.commit()

print("Your soaps database has been inserted!")
