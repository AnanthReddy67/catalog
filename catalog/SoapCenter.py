from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Soap_Setup import Base, SoapCompnayName, SoapName, GmailUser
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///soaps.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Soaps Center"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
drs_son = session.query(SoapCompnayName).all()

# completed
# login


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    drs_son = session.query(SoapCompnayName).all()
    dres = session.query(SoapName).all()
    return render_template('login.html',
                           STATE=state, drs_son=drs_son, dres=dres)
    # return render_template('myhome.html', STATE=state
    # drs_son=drs_son,dres=dres)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = GmailUser(name=login_session['username'], email=login_session[
                   'email'])
    session.add(User1)
    session.commit()
    user = session.query(
                         GmailUser).filter_by(email=login_session['email']
                                              ).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(GmailUser).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(GmailUser).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

# completed
# Home


@app.route('/')
@app.route('/home')
def home():
    drs_son = session.query(SoapCompnayName).all()
    return render_template('myhome.html', drs_son=drs_son)

# completed
# Soap Compnay for admins


@app.route('/SoapsCenter')
def SoapsCenter():
    try:
        if login_session['username']:
            name = login_session['username']
            drs_son = session.query(SoapCompnayName).all()
            drs = session.query(SoapCompnayName).all()
            dres = session.query(SoapName).all()
            return render_template('myhome.html', drs_son=drs_son,
                                   drs=drs, dres=dres, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing Soaps based on Soap Compnay


@app.route('/SoapsCenter/<int:drid>/showSoapCompnay')
def showSoapCompnay(drid):
    drs_son = session.query(SoapCompnayName).all()
    drs = session.query(SoapCompnayName).filter_by(id=drid).one()
    dres = session.query(SoapName).filter_by(soapcompnaynameid=drid).all()
    try:
        if login_session['username']:
            return render_template('showSoapCompnay.html', drs_son=drs_son,
                                   drs=drs, dres=dres,
                                   uname=login_session['username'])
    except:
        return render_template('showSoapCompnay.html',
                               drs_son=drs_son, drs=drs, dres=dres)

#####
# Add New SoapCompnay


@app.route('/SoapsCenter/addSoapCompnay', methods=['POST', 'GET'])
def addSoapCompnay():
    if request.method == 'POST':
        company = SoapCompnayName(name=request.form['name'],
                                  user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('SoapsCenter'))
    else:
        return render_template('addSoapCompnay.html', drs_son=drs_son)

########
# Edit Soap Compnay


@app.route('/SoapsCenter/<int:drid>/edit', methods=['POST', 'GET'])
def editSoapCompnay(drid):
    editSoapCompnay = session.query(SoapCompnayName).filter_by(id=drid).one()
    creator = getUserInfo(editSoapCompnay.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Soap Compnay."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('SoapsCenter'))
    if request.method == "POST":
        if request.form['name']:
            editSoapCompnay.name = request.form['name']
        session.add(editSoapCompnay)
        session.commit()
        flash("Soap Compnay Edited Successfully")
        return redirect(url_for('SoapsCenter'))
    else:
        # drs_son is global variable we can them in entire application
        return render_template('editSoapCompnay.html',
                               dr=editSoapCompnay, drs_son=drs_son)

######
# Delete Soap Compnay


@app.route('/SoapsCenter/<int:drid>/delete', methods=['POST', 'GET'])
def deleteSoapCompnay(drid):
    dr = session.query(SoapCompnayName).filter_by(id=drid).one()
    creator = getUserInfo(dr.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Soap Compnay."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('SoapsCenter'))
    if request.method == "POST":
        session.delete(dr)
        session.commit()
        flash("Soap Compnay Deleted Successfully")
        return redirect(url_for('SoapsCenter'))
    else:
        return render_template('deleteSoapCompnay.html',
                               dr=dr, drs_son=drs_son)

######
# Add New Soap Name Details


@app.route('/SoapsCenter/addSoapCompnay/addSoapDetails/<string:drname>/add',
           methods=['GET', 'POST'])
def addSoapDetails(drname):
    drs = session.query(SoapCompnayName).filter_by(name=drname).one()
    # See if the logged in user is not the owner of game
    creator = getUserInfo(drs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showSoapCompnay', drid=drs.id))
    if request.method == 'POST':
        soapname = request.form['soapname']
        launchyear = request.form['launchyear']
        rating = request.form['rating']
        price = request.form['price']
        weight = request.form['weight']
        soaptype = request.form['soaptype']
        soapdetails = SoapName(soapname=soapname,
                               launchyear=launchyear,
                               rating=rating,
                               price=price,
                               weight=weight,
                               soaptype=soaptype,
                               soapcompnaynameid=drs.id,
                               gmailuser_id=login_session['user_id'])
        session.add(soapdetails)
        session.commit()
        return redirect(url_for('showSoapCompnay', drid=drs.id))
    else:
        return render_template('addSoapDetails.html',
                               drname=drs.name, drs_son=drs_son)

######
# Edit Soap details


@app.route('/SoapcCenter/<int:drid>/<string:drename>/edit',
           methods=['GET', 'POST'])
def editSoap(drid, drename):
    dr = session.query(SoapCompnayName).filter_by(id=drid).one()
    soapdetails = session.query(SoapName).filter_by(soapname=drename).one()
    # See if the logged in user is not the owner of game
    creator = getUserInfo(dr.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showSoapCompnay', drid=dr.id))
    # POST methods
    if request.method == 'POST':
        soapdetails.soapname = request.form['soapname']
        soapdetails.launchyear = request.form['launchyear']
        soapdetails.rating = request.form['rating']
        soapdetails.price = request.form['price']
        soapdetails.weight = request.form['weight']
        soapdetails.soaptype = request.form['soaptype']
        soapdetails.date = datetime.datetime.now()
        session.add(soapdetails)
        session.commit()
        flash("Soap Edited Successfully")
        return redirect(url_for('showSoapCompnay', drid=drid))
    else:
        return render_template('editSoap.html',
                               drid=drid,
                               soapdetails=soapdetails, drs_son=drs_son)

#####
# Delte Soap Edit


@app.route('/SoapsCenter/<int:drid>/<string:drename>/delete',
           methods=['GET', 'POST'])
def deleteSoap(drid, drename):
    dr = session.query(SoapCompnayName).filter_by(id=drid).one()
    soapdetails = session.query(SoapName).filter_by(soapname=drename).one()
    # See if the logged in user is not the owner of soap
    creator = getUserInfo(dr.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showSoapCompnay', drid=dr.id))
    if request.method == "POST":
        session.delete(soapdetails)
        session.commit()
        flash("Deleted Soap Successfully")
        return redirect(url_for('showSoapCompnay', drid=drid))
    else:
        return render_template('deleteSoap.html',
                               drid=drid,
                               soapdetails=soapdetails, drs_son=drs_son)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'}
                  )[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully'
                                            'disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json


@app.route('/SoapsCenter/JSON')
def allSoapsJSON():
    SoapCompnay = session.query(SoapCompnayName).all()
    category_dict = [c.serialize for c in SoapCompnay]
    for c in range(len(category_dict)):
        soaps = [i.serialize for i in session.query(
                 SoapName
                 ).filter_by(soapcompnaynameid=category_dict[c]["id"]).all()]
        if soaps:
            category_dict[c]["soap"] = soaps
    return jsonify(SoapCompnayName=category_dict)

####


@app.route('/SoapsCenter/SoapCompnay/JSON')
def categoriesJSON():
    soaps = session.query(SoapCompnayName).all()
    return jsonify(SoapCompnay=[c.serialize for c in soaps])

####


@app.route('/SoapsCenter/soaps/JSON')
def itemsJSON():
    items = session.query(SoapName).all()
    return jsonify(soaps=[i.serialize for i in items])

#####


@app.route('/SoapsCenter/<path:soap_name>/soaps/JSON')
def categoryItemsJSON(soap_name):
    SoapCompnay = session.query(
        SoapCompnayName).filter_by(name=soap_name).one()
    soaps = session.query(SoapName).filter_by(soapname=soapcategory).all()
    return jsonify(soapEdtion=[i.serialize for i in soaps])

#####


@app.route('/SoapsCenter/<path:soap_name>/<path:edition_name>/JSON')
def ItemJSON(soap_name, edition_name):
    SoapCompnay = session.query(
        SoapCompnayName).filter_by(name=soap_name).one()
    soapEdition = session.query(SoapName).filter_by(soapname=edition_name,
                                                    soapname1=SoapCompnay
                                                    ).one()
    return jsonify(soapEdition=[soapEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
