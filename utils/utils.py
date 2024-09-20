from flask import Response
import json
from app.models import User, ROLE_CHOICES


def make_response(status, message=None, data=None, status_code=200):
    response_data = {"status": status, "message": message, "data": data}
    return Response(
        json.dumps(response_data), status=status_code, content_type="application/json"
    )

def validate_user_data(data):
    email = data.get("email")
    name = data.get("name", None)
    password = data.get("password", None)
    role = data.get('role')

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