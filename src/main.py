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

    dateQty = []
    datePrice = []
    for oneData in range(len(dates)):
        dateQty.append([str(dates[oneData]).split(" ")[0], qty[oneData]])
        datePrice.append([str(dates[oneData]).split(" ")[0], "Rs. " + str(price[oneData])])

    Dprice, Dqty = {}, {}
    for oneData in range(len(grouped_ordersItemQty)):
        Dqty[grouped_ordersItemQty[oneData][0]] = grouped_ordersItemQty[oneData][1]

    for oneData in range(len(grouped_ordersItemPrice)):
        Dprice[grouped_ordersItemQty[oneData][0]] = grouped_ordersItemPrice[oneData][1]

    Dqty = dict(sorted(Dqty.items(), key=lambda x: x[1], reverse=True))
    Dprice = dict(sorted(Dprice.items(), key=lambda x: x[1], reverse=True))

    fnameItemPrice = plotItemGraph(Dprice.keys(), Dprice.values(), "Item vs Price")
    fnameItemQty = plotItemGraph(Dqty.keys(), Dqty.values(), "Item vs Qty")

    filename = [fnameItemPrice, fnameItemQty, fnameDatePrice, fnameDateQty]
    title = ["Item vs Price", "Item vs Qty", "Date vs Price", "Date vs Qty"]

    itemPrice = []
    itemQty = []

    for oneData in Dprice.keys():
        itemPrice.append([oneData, "Rs. " + str(Dprice[oneData])])

    for oneData in Dqty.keys():
        itemQty.append([oneData, Dqty[oneData]])

    return make_response(
        render_template('analysis-daily.html', filename=filename, title=title, DatePrice=datePrice, DateQty=dateQty,
                        ItemPriceData=itemPrice, ItemQty=itemQty), 200)


@app.route("/weekly-analysis")
@login_required
def weeklyAnalysis():
    orders = db.session.query(Orders).all()

    grouped_qty = {}
    grouped_price = {}

    for order in orders:
        date_obj = datetime.strptime(order.date, "%B %d, %Y")
        day_of_week = date_obj.weekday()

        if day_of_week in grouped_qty:
            grouped_qty[day_of_week] += order.qty
            grouped_price[day_of_week] += order.price
        else:
            grouped_qty[day_of_week] = order.qty
            grouped_price[day_of_week] = order.price

    sorted_qty = sorted(grouped_qty.items())
    sorted_price = sorted(grouped_price.items())

    days_of_week, quantities = zip(*sorted_qty)
    _, prices = zip(*sorted_price)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(days_of_week, prices, color="#FF8C00")
    ax1.set_title("Days of Week vs Price")
    ax1.set_xlabel("Days of Week")
    ax1.set_ylabel("Price (Rs.)")
    filename_price = str(datetime.now().strftime('%B %d, %Y')).replace(" ", "") + "_price.png"
    plt.savefig(f"./static/graphs/{filename_price}", bbox_inches='tight')
    plt.close()

    fig, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(days_of_week, quantities, color="#FF1493")
    ax2.set_title("Days of Week vs Qty")
    ax2.set_xlabel("Days of Week")
    ax2.set_ylabel("Quantity")
    filename_qty = str(datetime.now().strftime('%B %d, %Y')).replace(" ", "") + "_qty.png"
    plt.savefig(f"./static/graphs/{filename_qty}", bbox_inches='tight')
    plt.close()

    title = ["Days of Week vs Qty", "Days of Week vs Price"]
    filename = [f"./static/graphs/{filename_qty}", f"./static/graphs/{filename_price}"]

    weekQty, weekSales = [], []
    for oneData in range(len(days_of_week)):
        weekQty.append([days_of_week[oneData], quantities[oneData]])
        weekSales.append([days_of_week[oneData], prices[oneData]])

    return make_response(
        render_template('analysis-weekly.html', filename=filename, title=title, weekQty=weekQty, weekSales=weekSales),
        200)


def fetchOrderData(form):
    foodMenu = fetchMenu()
    orderData = []
    Sno = 1
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
    plt.figure(figsize=(40, 20))
    plt.plot(X, Y, marker='o', color="red")
    ytick = range(int(min(Y)), int(max(Y)), 60)

    label = title.split(" vs ")
    xlabel = label[0]
    ylabel = label[1]

    if 'Price' in title:
        ytick = range(int(min(Y)), int(max(Y)), 300)
        ylabel += " (Rs.)"

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.yticks(ytick)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    filename = f"{title}-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "")
    plt.savefig(f"./static/graphs/{filename}.png")
    return f"./static/graphs/{filename}.png"


def plotDateGraph(X, Y, title):
    plt.figure(figsize=(10, 5))
    plt.plot(X, Y, marker='o', color="green")

    label = title.split(" vs ")
    xlabel = label[0]
    ylabel = label[1]

    if 'Price' in title:
        ytick = range(int(min(Y)), int(max(Y)), 250)
        ylabel += " (Rs.)"
    else:
        ytick = range(int(min(Y)), int(max(Y)), 10)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.yticks(ytick)
    plt.title(title)
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    filename = f"{title}-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "")
    plt.savefig(f"./static/graphs/{filename}.png")
    return f"./static/graphs/{filename}.png"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
