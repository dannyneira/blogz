from flask import Flask, request, redirect, session, render_template, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from helpers import validate_signup, validate_login

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
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def index():
    title_header='All Blogs'
    return render_template('index.html', 
        base_title=title_header,
        header=title_header)

@app.route('/blog', methods=['GET'])
def blog():
    title_header = 'Build-A-Blog'
    post = Blog.query.filter_by(id=request.args.get('id')).first()
    if post:
        return render_template('post.html',
            base_title=title_header,
            header=post.title,
            body=post.body)
    else:
        blogs = sorted(Blog.query.all(), key=lambda x: x.id, reverse=True)
        return render_template('blog.html',
            base_title=title_header,
            header=title_header,
            blogs=blogs)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    title_header = 'Add Blog Post'
    if request.method == 'POST':
        base_title = request.form['title']
        body = request.form['body']
        errors = {'title_err':"", 'body_err':""}

        if base_title == '':
            errors['title_err'] = 'Please fill in Title'
        if body == '':            
            errors['body_err'] = 'Please fill in Body'

        if any("" != err for err in errors.values()):
            return render_template('newpost.html',
                base_title=title_header,
                header=title_header,
                title=title,
                body=body,
                base_title_err=errors['title_err'],
                body_err=errors['body_err'])
        else:
            new_blog = Blog(base_title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
    else:
        return render_template('new_post.html',
            base_title=title_header, 
            header=title_header)

@app.route('/signup', methods=['GET', 'POST'])
def register():
    title_header = 'Signup'
    if request.method== 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # validate user data
        existing_user = User.query.filter_by(email=email).first()
        validation = validate_signup(email,password,verify)

        if validation == True and not existing_user:
            new_user = User(email, make_pw_hash(password))
            db.session.add(new_user)
            db.session.commit()

            session['email'] = email
            flash("Registered as " + email, 'info')
            return redirect('/newpost')
        else:
            flash("Signup Failed!", 'error')
            return render_template('signup.html',
                base_title=title_header,
                header=title_header,
                email=validation['email'],
                email_err=validation['email_err'],
                password_err=validation['password_err'],
                verify_err=validation['verify_err'])
    else:
        return render_template('signup.html', base_title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    title_header = 'Login'
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        validation = validate_login(user, password)

        if validation == True:
            session['email'] = email
            flash("Welcome "+session['email'], 'info')
            return redirect('/newpost')
        else:
            flash("Login Failed!", 'error')
            return render_template('login.html',
                base_title=title_header,
                header=title_header,
                email=validation['email'],
                email_err=validation['email_err'],
                password_err=validation['password_err'])
    else:
        return render_template('login.html', 
            base_title=title_header,
            header=title_header)

@app.route('/logout')
def logout():
    flash("Goodbye "+session['email'], 'info')
    del session['email']
    return redirect('/')


if __name__ == "__main__":
    app.run()

# @app.route('/delpost', methods=['POST'])
# def delete_post():

#     blog_id = int(request.form['blog-id'])
#     post = Blog.query.get(blog_id)
#     db.session.remove(post)
#     db.session.commit()

#     return redirect('/blog')