from  flask import Flask,url_for,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,UserMixin,LoginManager,login_user,logout_user,current_user
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user



app=Flask(__name__)
app.config['SECRET_KEY']='christian'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.init_app(app)
all_activity=[]

class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, unique=True, nullable=False)
    email=db.Column(db.String, unique=True, nullable=False)
    bdate=db.Column(db.String,  nullable=False)
    password=db.Column(db.String, nullable=False)

class Todo(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    activity=db.Column(db.String, unique=True, nullable=False)
    todo_id=db.Column(db.Integer)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home',methods=['POST','GET'])
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method=='POST':
        hashed_password=generate_password_hash(
            password=request.form['password'],
            method="pbkdf2:sha256",
            salt_length=6
        )
        fullname=request.form['fname']+ request.form['lname']
        new_user=User(
            name=fullname,
            email=request.form['email'],
            password=hashed_password,
            bdate=request.form['bdate']
        )
        check_user=request.form['email']
        used_passord=request.form['cpassword']
        cused_passord=request.form['password']
        check_user=User.query.filter_by(email=check_user).first()
        if check_user:  
            flash('Email already exist!')
            return redirect('register')
        elif used_passord!=cused_passord:
            flash("password doesn't match!")
            return redirect('register')
        else:
            flash('account successful created!')
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            return redirect('login')
        
    return render_template('register.html')
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        usermail=request.form['email']
        userpassword=request.form['password']
        usertolog=User.query.filter_by(email=usermail).first()
        if not usertolog:
            flash("Email address doesn't exist!")
            return redirect('login')
        elif not check_password_hash(usertolog.password,userpassword):
            flash("Wrong password, check again!")
            return redirect('login')
        else:
            login_user(usertolog)
            flash('successful signed in!')
            return redirect(url_for('all'))
    return render_template('login.html')
@app.route('/logout')
def logout():
    logout_user()
    return redirect('home')
@app.route('/add', methods=['POST','GET'])
def add():
    this_user=current_user.id
    if request.method=='POST':
        new_activity=Todo(
            activity=request.form['activity'],
            todo_id=this_user
        )
        with app.app_context():
            db.session.add(new_activity)
            db.session.commit()
        return redirect(url_for('add'))
    
    return render_template('add.html', activities=all_activity)
@app.route('/My Work', methods=['POST', 'GET'])
def all():
    all_activity=Todo.query.all()
    return render_template('home.html', activities=all_activity)
@app.route('/delete/<id>')
def delete(id):
    delete_active=Todo.query.get(id)
    db.session.delete(delete_active)
    db.session.commit()
    return redirect(url_for('all'))
    
if __name__=='__main__':
    app.run(debug=True)