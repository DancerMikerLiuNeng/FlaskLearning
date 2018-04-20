from flask import Flask,render_template,session,redirect,url_for,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from datetime import datetime
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Message,Mail
from threading import Thread
import os

basedir  = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SECRET_KEY'] = 'guess'

app.config['SQLALCHEMY_DATABASE_URI']=\
'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASK_ADMIN'] = os.environ.get('FLASK_ADMIN')

app.config['FLASKLEARNING_MAIL_SUBJECT_PREFIX'] = '[FLask]'
app.config['FLASK_MAIL_SENDER'] = 'dachuan.chengdu@hotmail.com'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
mement = Moment(app)
manager = Manager(app)
mail = Mail(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET','POST'])
def index():
    # name = None
    form = NameForm()
    if form.validate_on_submit():
        # old_name = session.get('name')
        # if old_name is not None and old_name != form.name.data:
        #     flash('Looks like you have changed your name!')
        # session['name'] = form.name.data
        # return redirect(url_for('index'))
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            flash('Looks like you have changed your name!')
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASK_ADMIN']:
                send_email(app.config['FLASK_ADMIN'],'New User',
                           'mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           name=session.get('name'),
                           known=session.get('known',False))

@app.errorhandler(404)
def pag_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKLEARNING_MAIL_SUBJECT_PREFIX']+subject,
                  sender=app.config['FLASK_MAIL_SENDER'],recipients=[to])

    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app,msg])
    thr.start()
    return thr
    # mail.send(msg)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

migrate = Migrate(app, db)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
if __name__=='__main__':
    app.run(debug=True)
    # manager.run()
