from mongoengine import *

connect('jungo')

class User(Document):
    email = StringField(required=True)