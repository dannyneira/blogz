from flask import Flask, request, redirect, session, render_template, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from helpers import validate_signup, validate_login, validate_post, gen_hash, check_hash
from datetime import date

app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f72746fd810a750dbee37dc116c2aa6aaf070df82d0bd7edb42bfbb42c96e9b3'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(480))
    date = db.Column(db.Date)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.date = date.today()
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

@app.before_request
def require_login():
    blocked_routes = ['newpost', 'delpost']
    if request.endpoint in blocked_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    title_header='Bloggers'
    users = User.query.all()
    return render_template('index.html', 
        base_title=title_header,
        base_header=title_header,
        users=users)

@app.route('/blog', methods=['GET'])
def blog():
    title_header = 'Blog Posts'
    user = User.query.filter_by(name=request.args.get('username')).first()
    post = Blog.query.filter_by(id=request.args.get('id')).first()

    if user:
        blogs = Blog.query.filter_by(owner_id=user.id).order_by(Blog.id.desc()).all()
        # blogs = sorted(Blog.query.filter_by(owner_id=user.id).all(), key=lambda x: x.id, reverse=True)
        return render_template('blog.html',
            base_title=title_header,
            base_header="{0}'s {1}".format(user.name.title(),title_header),
            blogs=blogs)
    elif post:
        return render_template('post.html',
            base_title=title_header,
            base_header=post.title,
            post=post)
    else:
        blogs = Blog.query.order_by(Blog.id.desc()).all()
        # blogs = sorted(Blog.query.all(), key=lambda x: x.id, reverse=True)
        return render_template('blog.html',
            base_title=title_header,
            base_header=title_header,
            blogs=blogs)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    title_header = 'Add Blog Post'
    user = User.query.filter_by(name=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        validation = validate_post(title, body)

        if validation == True:
            new_blog = Blog(title, body, user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            return render_template('newpost.html',
                base_title=title_header,
                base_header=title_header,
                title=title,
                title_err=errors['title_err'],
                body=body,
                body_err=errors['body_err'])
    else:
        return render_template('new_post.html',
            base_title=title_header, 
            base_header=title_header)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title_header = 'Signup'
    if request.method== 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(name=username).first()
        validation = validate_signup(username, email, password, verify)

        if validation == True and not existing_user:
            new_user = User(username, email, gen_hash(password))
            db.session.add(new_user)
            db.session.commit()

            session['username'] = new_user.name
            flash("Registered as " + new_user.name, 'info')
            return redirect('/newpost')
        else:
            flash("Signup Failed!", 'error')
            return render_template('signup.html',
                base_title=title_header,
                base_header=title_header,
                username=username,
                username_err=validation['username_err'],
                email=email,
                email_err=validation['email_err'],
                password_err=validation['password_err'],
                verify_err=validation['verify_err'])
    else:
        return render_template('signup.html', base_title=title_header, base_header=title_header)

@app.route('/login', methods=['GET', 'POST'])
def login():
    title_header = 'Login'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(name=username).first()
        validation = validate_login(user, password)

        if validation == True:
            session['username'] = user.name
            flash("Welcome " + session['username'], 'info')
            return redirect('/newpost')
        else:
            flash("Login Failed!", 'error')
            return render_template('login.html',
                base_title=title_header,
                base_header=title_header,
                username=username,
                username_err=validation['username_err'],
                password_err=validation['password_err'])
    else:
        return render_template('login.html', 
            base_title=title_header,
            base_header=title_header)

@app.route('/logout')
def logout():
    if 'username' not in session:
        flash("Not logged into any User", 'error')
        return redirect('/blog')
    else:
        flash("Goodbye " + session['username'].title(), 'info')
        del session['username']
        return redirect('/blog')

if __name__ == "__main__":
    app.run()

# @app.route('/delpost', methods=['POST'])
# def delete_post():

#     blog_id = int(request.form['blog-id'])
#     post = Blog.query.get(blog_id)
#     db.session.remove(post)
#     db.session.commit()

#     return redirect('/blog')