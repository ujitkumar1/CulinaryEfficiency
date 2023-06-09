import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
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
    date = db.Column(db.String(20), default=datetime.now().strftime("%B %d, %Y"))


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
    grouped_ordersDateQty = db.session.query(Orders.date, db.func.sum(Orders.qty)).group_by(Orders.date).all()
    grouped_ordersDatePrice = db.session.query(Orders.date, db.func.sum(Orders.price)).group_by(Orders.date).all()
    grouped_ordersItemQty = db.session.query(Orders.item, db.func.sum(Orders.qty)).group_by(Orders.item).all()
    grouped_ordersItemPrice = db.session.query(Orders.item, db.func.sum(Orders.price)).group_by(Orders.item).all()

    dates, price, qty = [], [], []
    for oneData in range(len(grouped_ordersDateQty)):
        date_str = grouped_ordersDateQty[oneData][0]
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        dates.append(date_obj)
        price.append(grouped_ordersDatePrice[oneData][1])
        qty.append(grouped_ordersDateQty[oneData][1])

    sorted_data = sorted(zip(dates, price, qty), key=lambda x: x[0])
    dates, price, qty = zip(*sorted_data)

    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%B %d, %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    fnameDatePrice = plotDateGraph(dates, price, "Date vs Price")
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%B %d, %Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fnameDateQty = plotDateGraph(dates, qty, "Date vs Qty")

    items, price, qty = [], [], []
    for oneData in range(len(grouped_ordersItemQty)):
        items.append(grouped_ordersItemQty[oneData][0])
        qty.append(grouped_ordersItemQty[oneData][1])

    for oneData in range(len(grouped_ordersItemPrice)):
        price.append(grouped_ordersItemPrice[oneData][1])

    fnameItemPrice = plotItemGraph(items, price, "Item vs Price")
    fnameItemQty = plotItemGraph(items, qty, "Item vs Qty")

    filename = [fnameItemPrice, fnameItemQty, fnameDatePrice, fnameDateQty]
    return make_response(render_template('analysis-data.html', filename=filename), 200)


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


def plotItemGraph(X, Y, title):
    plt.figure(figsize=(40, 15))
    plt.plot(X, Y)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    filename = f"{title}-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "")
    plt.savefig(f"./static/graphs/{filename}.png")
    return f"./static/graphs/{filename}.png"


def plotDateGraph(X, Y, title):
    plt.figure(figsize=(10, 5))
    plt.plot(X, Y)
    plt.title(title)
    plt.gcf().autofmt_xdate()
    filename = f"{title}-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "")
    plt.savefig(f"./static/graphs/{filename}.png")
    return f"./static/graphs/{filename}.png"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
