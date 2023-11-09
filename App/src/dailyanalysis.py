from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from flask import make_response, render_template
from flask_login import login_required
from flask_restful import Resource

from src import db
from src.helperFunctions import Help
from src.models import Orders


class dailyAnalysis(Resource):
    @login_required
    def get(self):
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

        fnameDatePrice = Help.plotDateGraph(dates, price, "Date vs Price")
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%B %d, %Y"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fnameDateQty = Help.plotDateGraph(dates, qty, "Date vs Qty")

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

        fnameItemPrice = Help.plotItemGraph(Dprice.keys(), Dprice.values(), "Item vs Price", size=True)
        fnameItemQty = Help.plotItemGraph(Dqty.keys(), Dqty.values(), "Item vs Qty", size=True)

        filename = [fnameItemPrice, fnameItemQty, fnameDatePrice, fnameDateQty]
        title = ["Item vs Price", "Item vs Qty", "Date vs Price", "Date vs Qty"]

        itemPrice = []
        itemQty = []

        sumSalesPrice = sum(Dprice.values())
        for oneData in Dprice.keys():
            itemPrice.append(
                [oneData, "Rs. " + str(Dprice[oneData]), str(round((Dprice[oneData] / sumSalesPrice) * 100, 3)) + " %"])

        sumSalesQty = sum(Dqty.values())
        for oneData in Dqty.keys():
            itemQty.append([oneData, Dqty[oneData], str(round((Dqty[oneData] / sumSalesQty) * 100, 3)) + " %"])

        return make_response(
            render_template('analysis-daily.html', filename=filename, title=title, DatePrice=datePrice, DateQty=dateQty,
                            ItemPriceData=itemPrice, ItemQty=itemQty), 200)
