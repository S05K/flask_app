from celery  import shared_task
from time import sleep
from app import mail
from flask_mail import Message



'''
Method for sending email while purchasing 
player via owner
'''
@shared_task
def send_email(player_email,owner_email,owner_name):
            msg = Message('Hello', 
                          sender ='sumitraghuvanshi413@gmail.com',
                          recipients = [player_email]
                          ) 
            msg.body = f'You are sold to the owner {owner_name} and here are the contact details of your owner {owner_email}'
            mail.send(msg)
