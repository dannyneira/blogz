from flask import Markup
from re import match
from hashlib import sha256
from random import choice
import string


def is_empty(input):
    return True if input == "" else False

def has_space(input):
    return True if " " in input else False

def valid_len(value):
    val_len = len(value)
    return True if val_len >= 3 and val_len <= 20 else False

def valid_pass(password, verify):
    return True if password == verify else False

def valid_email(email):
    reg = match(r"[^@]+@[^@]+\.[^@]+", email)
    return True if reg != None else False

def gen_hash(password, salt=None):
    if not salt:
        salt = "".join(choice(string.ascii_letters) for i in range(5))
    return "{0},{1}".format(sha256(str.encode(password+salt)).hexdigest(),salt)

def check_hash(pw_hash, password):
    pw_hash = pw_hash.split(',')
    return True if pw_hash[0] == sha256(str.encode(password+pw_hash[1])).hexdigest() else False

def check_errors(errors):
    '''Checks errors and returns True or Errors'''
    if all(True if err == "" else False for err in errors.values()):
        return True
    else:
        return errors

def validate_signup(username, email, password, verify):
    errors = {'username_err':"",'email_err':"",'password_err':"",'verify_err':""}
    
    # Validate Username
    if is_empty(username):
        errors['username_err'] = "You must enter a username"
    elif has_space(username):
        errors['username_err'] = "Your username cannot contain spaces"
    elif not valid_len(username):
        errors['username_err'] = "That's not a valid email length (3-20 characters)"

    # Validate Emails
    if is_empty(email):
        errors['email_err'] = "You must enter an email"
    elif has_space(email):
        errors['email_err'] = "Your email cannot contain spaces"
    elif not valid_email(email):
        errors['email_err'] = "That's not a valid email (hello@gmail.com)"

    # Validate Passwords
    if is_empty(password) or is_empty(verify):
        if is_empty(password):
            errors['password_err'] = "You must enter a password"
        if is_empty(verify):
            errors['verify_err'] = "You must enter a verification password"
    elif has_space(password) or has_space(verify):
        errors['password_err'] = "Your password cannot contain spaces"
    elif not valid_len(password):
        errors['password_err'] = "That's not a valid password length (3-20 characters)"
    elif not valid_pass(password, verify):
        errors['password_err'] = "Passwords don't match"

    return check_errors(errors)

def validate_login(user, password):
    errors = {'username_err':"",'password_err':""}

    # Validate User
    if not user:
        errors['username_err'] = "Username not found, please try again or signup"

    # Validate Passwords
    if user and password == "":
        errors['password_err'] = "Please enter your password"
    elif user and not check_hash(user.password, password):
        errors['password_err'] = "Incorrect password, please try again"
    
    return check_errors(errors)

def validate_post(title, body):
    errors={'title_err':"",'body_err':""}

    if is_empty(title):
        errors['title_err'] = "You must enter a title"
    if is_empty(body):
        errors['title_err'] = "You must enter a title"
    
    return check_errors(errors)