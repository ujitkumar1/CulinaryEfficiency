from datetime import datetime, date

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from flask import make_response, render_template
from flask_login import login_required
from flask_restful import Resource

from src import db
from src.helperFunctions import Help
from src.models import Orders


class todayAnalysis(Resource):
    @login_required
    def get(self):
        today = date.today().strftime("%B %d, %Y")

        grouped_ordersDateQty = db.session.query(Orders.date, db.func.sum(Orders.qty)).filter(
            Orders.date == today).group_by(Orders.date).all()
        grouped_ordersDatePrice = db.session.query(Orders.date, db.func.sum(Orders.price)).filter(
            Orders.date == today).group_by(Orders.date).all()
        grouped_ordersItemQty = db.session.query(Orders.item, db.func.sum(Orders.qty)).filter(
            Orders.date == today).group_by(Orders.item).all()
        grouped_ordersItemPrice = db.session.query(Orders.item, db.func.sum(Orders.price)).filter(
            Orders.date == today).group_by(Orders.item).all()

        if not grouped_ordersDateQty or not grouped_ordersDatePrice:
            return make_response("No data available for today's date", 200)

        price = grouped_ordersDatePrice[0][1]
        qty = grouped_ordersDateQty[0][1]

        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%B %d, %Y"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        dateQty = [[today.split(" ")[0], qty]]
        datePrice = [[today.split(" ")[0], "Rs. " + str(price)]]

        Dprice, Dqty = {}, {}
        for oneData in range(len(grouped_ordersItemQty)):
            Dqty[grouped_ordersItemQty[oneData][0]] = grouped_ordersItemQty[oneData][1]

        for oneData in range(len(grouped_ordersItemPrice)):
            Dprice[grouped_ordersItemQty[oneData][0]] = grouped_ordersItemPrice[oneData][1]

        Dqty = dict(sorted(Dqty.items(), key=lambda x: x[1], reverse=True))
        Dprice = dict(sorted(Dprice.items(), key=lambda x: x[1], reverse=True))

        fnameItemPrice = Help.plotItemGraph(X=Dprice.keys(), Y=Dprice.values(), title="Item vs Price", size=False)
        fnameItemQty = Help.plotItemGraph(X=Dqty.keys(), Y=Dqty.values(), title="Item vs Qty", size=False)

        filename = [fnameItemPrice + ".png", fnameItemQty + ".png"]
        title = ["Item vs Price", "Item vs Qty", "Price Table", "Qty. Table"]

        itemPrice = []
        itemQty = []

        for oneData in Dprice.keys():
            itemPrice.append([oneData, "Rs. " + str(Dprice[oneData])])

        for oneData in Dqty.keys():
            itemQty.append([oneData, Dqty[oneData]])

        return make_response(
            render_template('analysis-today.html', filename=filename, title=title, DatePrice=datePrice, DateQty=dateQty,
                            ItemPriceData=itemPrice, ItemQty=itemQty, date=str(datetime.now().strftime('%B %d, %Y'))),
            200)
