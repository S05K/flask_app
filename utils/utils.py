from flask import Response
import json
from app.models import User, ROLE_CHOICES
from app import mail
from flask_mail import Message


def make_response(status, message=None, data=None, status_code=200):
    response_data = {"status": status, "message": message, "data": data}
    return Response(
        json.dumps(response_data), status=status_code, content_type="application/json"
    )

def validate_user_data(data):
    email = data.get("email")
    name = data.get("name", None)
    password = data.get("password", None)
    # role = data.get('role')
    team_name = data.get("team_name")

    if name is None or str(name).strip() == "" or name != str(name):
        return {'Error': 'Please enter a valid name'}
    
    if email == '':
        return {'Error': 'Please enter Email'}
    
    if password == '':
        return {'Error': 'Please enter Password'}
        
    if User.query.filter_by(email=email).first():
        return {'Error': 'Email already present'}
    
    if email is None:
        return {'Error': 'Please enter your email'}

    if password is None:
        return {'Error': 'Please enter a proper password'}
    
    if len(password) < 8:
        return {'Error': 'Passowrd length should be 8 digit'}

    return None


'''
Method for sending email while purchasing 
player via owner
'''

def send_email(player_email,owner_email,owner_name):
            msg = Message('Hello', 
                          sender ='sumitraghuvanshi413@gmail.com',
                          recipients = [player_email]
                          ) 
            msg.body = f'You are sold to the owner {owner_name} and here are the contact details of your owner {owner_email}'
            mail.send(msg)


