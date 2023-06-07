from flask import Flask, make_response, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "IITMBS21"
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'database.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

@app.route("/")
def main():
    return make_response(render_template('index.html'), 200)

@app.route("/login",methods =["GET","POST"])
def login():
    if request.method =="GET":
        return make_response(render_template('login.html'), 200)

    elif request.method =="POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            session['user_id'] = user.id
            return redirect('/home')# change this
        else:
            return 'Invalid username/password combination', 400



if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)