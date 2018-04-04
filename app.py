#Credits to tutorial that introduced all this - Pretty printed on youtube

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf  import FlaskForm
from flask_sqlalchemy  import SQLAlchemy
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'lastassignmentsecretdonttellprof'

Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#tables for the database
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(60),unique=True)
    password = db.Column(db.String(30))

class Task(db.Model):
        taskid = db.Column(db.Integer, primary_key=True)
        id = db.Column(db.Integer)
        title = db.Column(db.String(40), unique=False)
        description = db.Column(db.String(200), unique=False)
        status = db.Column(db.String(10), unique=False)
        created = db.Column(db.Date, unique=False)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#clasess for the forms
class Loginform(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(min=3, max = 20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=30)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Enter a valid email'),Length(max=60)])
    username = StringField('username',validators=[InputRequired(), Length(min=3, max = 20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return '<h2> Either your username/password is wrong</h2>'
    return render_template('login.html', form = form)

@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_pass = generate_password_hash(form.password.data, method='sha256')
        new_member = User(username = form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(new_member)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    todo = Task.query.filter_by(status='todo', id=current_user.id).all()
    doing = Task.query.filter_by(status='doing', id=current_user.id).all()
    done = Task.query.filter_by(status='done',id=current_user.id).all()
    return render_template('kanban-board.html', name = current_user.username, todo = todo, doing=doing, done=done)

@app.route('/addtask', methods=['GET','POST'])
def addtask():
    new_item = Task(id=current_user.id, title=request.form['title'], description=request.form['description'],status=request.form['status'],created=datetime.now().date())
    db.session.add(new_item)
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/markdoing/<taskid>', methods=['GET','POST'])
def markdoing(taskid):
    move_doing = Task.query.filter_by(taskid=int(taskid)).first()
    move_doing.status ='doing'
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/markdone/<taskid>', methods=['GET','POST'])
def markdone(taskid):
    move_done = Task.query.filter_by(taskid=int(taskid)).first()
    move_done.status ='done'
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/delete/<taskid>', methods=['GET','POST'])
def delete(taskid):
    deleted = Task.query.filter_by(taskid=int(taskid)).first()
    db.session.delete(deleted)
    db.session.commit()

    return redirect(url_for('dashboard'))




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ =="__main__":
    app.run(debug=True)
