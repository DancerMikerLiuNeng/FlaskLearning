from flask import Flask,render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap


app = Flask(__name__)
bootstrap = Bootstrap(app)
manager = Manager(app)
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def pag_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__=='__main__':
    manager.run()
