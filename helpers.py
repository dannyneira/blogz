from flask import Markup
from re import match
from hashlib import sha256
from random import choice
import string

def gen_hash(password, seed=None):
    if not seed:
        seed = "".join(choice(string.ascii_letters) for i in range(5))
    return "{0},{1}".format(sha256(str.encode(password+seed)).hexdigest(),seed)

def check_hash(hash, password):
    hash,seed = hash.split(',')
    return True if hash[0] == sha256(str.encode(password+hash[1])).hexdigest() else False

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

def validate_signup(email, password, verify):
    errors = {'email':"",'email_err':"",'password_err':"",'verify_err':""}
    
    # Validate Emails
    if not is_empty(email):
        if has_space(email):
            errors['email_err'] = "Your email cannot contain spaces"
        elif not valid_len(email):
            errors['email_err'] = "That's not a valid email length (3-20 characters)"
        elif not valid_email(email):
            errors['email_err'] = "That's not a valid email (hello@gmail.com)"

    # Validate Passwords
    if is_empty(password) or is_empty(verify):
        errors['password_err'] = "You must enter a password"
        errors['verify_err'] = "You must enter a verification password"
    elif has_space(password):
        errors['password_err'] = "Your password cannot contain spaces"
    elif not valid_len(password):
        errors['password_err'] = "That's not a valid password length (3-20 characters)"
    elif not valid_pass(password, verify):
        errors['password_err'] = "Passwords don't match"

    # Check for errors
    if any(True if val != "" else False for val in errors.values()):
        if errors['email_err'] == "":
            errors['email'] = email
        return errors
    else:
        return True

def validate_login(user, password):
    errors = {'email':"",'email_err':"",'password_err':""}

    # Validate Emails
    if user == None:
        errors['email_err'] = "Email not found, please try again or signup"
    # Validate Passwords
    if user and password == "":
        errors['email'] = user.email
        errors['password_err'] = "Please enter your password"
    elif user and not check_pw_hash(password, user.password):
        errors['email'] = user.email
        errors['password_err'] = "Incorrect password, please try again"
    
    # Return True is there are no Errors
    if any(True if val != "" else False for val in errors.values()):
        return errors
    else:
        return True