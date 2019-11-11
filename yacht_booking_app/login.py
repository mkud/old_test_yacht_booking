# -*- coding: utf-8 -*-
'''
Created on 3 aug 2017

@author: maxx
'''

from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Length, EqualTo, Email
from flask_login import UserMixin

class LoginForm(FlaskForm):
    email = EmailField('email', validators=[Required(), Email()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)
    login = SubmitField('login')

class RegisterForm(FlaskForm):
    email = EmailField('email', validators=[Required(), Email()])
    confirm_password = PasswordField('confirm_password', validators=[
        Required(),
        EqualTo('password', message='Passwords do not match')
    ])
    password = PasswordField('password', validators=[Required()])
    first_name = TextField('first_name', validators=[Length(max=127)])
    second_name = TextField('second_name', validators=[Length(max=127)])
    register = SubmitField('register')
    
class User(UserMixin):
    def __init__(self, in_id, email, first_name, second_name, count_unfinished_books = 0):
        self.id = in_id
        self.email = email
        self.first_name = first_name
        self.second_name = second_name
        self.count_unfinished_books = count_unfinished_books 
        
    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    @staticmethod
    def get_by_id(in_id, data_base):
        result = data_base.Site_GetClientInfo(in_id)
        
        return User(in_id, result[0][1], result[0][3], result[0][4], result[0][5]) if len(result) else None
    
    @staticmethod
    def get_by_email_pass(email, passwd, data_base):
        result = data_base.Site_LoginClient(email, passwd)
        return User(result[0][0], result[0][1], result[0][3], result[0][4], result[0][5]) if len(result) else None
    
    @staticmethod
    def register_new_user(email, passwd, first_name, second_name, data_base):
        result = data_base.Site_RegisterClient(email, passwd, first_name, second_name)
        return User(result[0][0], email, first_name, second_name) if len(result) and result[0][0] > 0 else None
    
