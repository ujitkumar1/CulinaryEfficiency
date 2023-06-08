from flask import Flask, make_response, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import login_required
from datetime import datetime


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

class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70),nullable=False)
    price = db.Column(db.Integer,nullable=False)

class Orders(db.Model):
    __tablename__= 'order'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(70),nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/")
def main():
    return make_response(render_template('index.html'), 200)

@app.route("/login",methods =["GET","POST"])
def login():
    if request.method =="GET":
        return make_response(render_template('login.html'), 200)

    elif request.method =="POST":
        print("ok")
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        print(user)
        if user and user.password == password:
            session['username'] = username
            session['user_id'] = user.id
            print("ok")
            return redirect('/home')# change this
        else:
            return 'Invalid username/password combination', 400

@login_required
@app.route("/home")
def home():
    food = fetchMenu()
    return make_response(render_template('home.html',menu = food), 200)

@login_required
@app.route("/place-order",methods =["GET","POST"])
def placeOrder():
    if request.method == "POST":
        orders = fetchOrderData(request.form)
        # print()
        for oneOrder in orders:
            placeorder = Orders(item=oneOrder[0],qty=oneOrder[2],price=(oneOrder[2]*oneOrder[1]))
            db.session.add(placeorder)
            db.session.commit()
        return str(orders)

def fetchOrderData(form):
    foodMenu = fetchMenu()
    orderData = []
    # print(form)
    for item in form:
        if form[item] != "":
            index = int(item.split("_")[1])
            qty = int(form[item])
            orderItem = foodMenu[index].split(' - ')
            item = orderItem[0]
            price = float(orderItem[1].split(" ")[1])
            data = [item, price, qty]
            orderData.append(data)
    return orderData

def fetchMenu():
    menu = Menu.query.all()
    menuDict = {}
    for i in menu:
        menuDict[i.id] = i.name+" - Rs. "+str(i.price)
    return (menuDict)

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)