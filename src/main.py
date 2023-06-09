import os
from datetime import datetime

from flask import Flask, make_response, render_template, request, redirect, flash
from flask_login import login_required, UserMixin, LoginManager, login_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "IITMBS21"
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'database.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    price = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(70), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def main():
    return make_response(render_template('index.html'), 200)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return make_response(render_template('login.html'), 200)

    elif request.method == "POST":
        print("ok")
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        print(user)
        if user and user.password == password:
            login_user(user)
            return redirect('/home')  # change this
        else:
            return 'Invalid username/password combination', 400


@app.route("/home")
def home():
    return make_response(render_template('home.html'), 200)


@app.route("/order")
@login_required
def order():
    food = fetchMenu()
    return make_response(render_template('order-page.html', menu=food), 200)


@app.route("/place-order", methods=["GET", "POST"])
@login_required
def placeOrder():
    if request.method == "POST":
        orders = fetchOrderData(request.form)
        # print()
        for oneOrder in orders:
            placeorder = Orders(item=oneOrder[1], qty=oneOrder[3], price=(oneOrder[3] * oneOrder[2]))
            db.session.add(placeorder)
            db.session.commit()
        flash('Order Placed successfully')
        return make_response(render_template('after-order.html', orderItems=orders), 200)


@app.route("/analysis")
@login_required
def analysis():
    return make_response(render_template('analysis.html'), 200)


@app.route("/daily-analysis")
@login_required
def dailyAnalysis():
    return make_response(render_template('analysis.html'), 200)


@app.route("/monthly-analysis")
@login_required
def monthlyAnalysis():
    return make_response(render_template('analysis.html'), 200)


@app.route("/weekly-analysis")
@login_required
def weeklyAnalysis():
    return make_response(render_template('analysis.html'), 200)


def fetchOrderData(form):
    foodMenu = fetchMenu()
    orderData = []
    Sno = 1
    # print(form)
    for item in form:
        if form[item] != "0":
            index = int(item.split("_")[1])
            qty = int(form[item])
            orderItem = foodMenu[index].split(' - ')
            item = orderItem[0]
            price = float(orderItem[1].split(" ")[1])
            data = [Sno, item, price, qty]
            orderData.append(data)
            Sno += 1
    return orderData


def fetchMenu():
    menu = Menu.query.all()
    menuDict = {}
    for i in menu:
        menuDict[i.id] = i.name + " - Rs. " + str(i.price)
    return (menuDict)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
