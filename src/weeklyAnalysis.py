import os
from datetime import datetime

import matplotlib.pyplot as plt
from flask import make_response, render_template, url_for
from flask_login import login_required
from flask_restful import Resource

from src import db, app
from src.models import Orders


class weeklyAnalysis(Resource):
    @login_required
    def get(self):
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

        filename = f"Days of Week vs Price-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "").replace(",",
                                                                                                                 "")

        static_folder = app.static_folder

        graphs_folder = os.path.join(static_folder, 'graphs')
        os.makedirs(graphs_folder, exist_ok=True)

        filepath = os.path.join(graphs_folder, filename)

        plt.savefig(filepath)
        static_url = url_for('static', filename='')
        url1 = f"{static_url}graphs/{filename}"

        fig, ax2 = plt.subplots(figsize=(8, 5))
        ax2.bar(days_of_week, quantities, color="#FF1493")
        ax2.set_title("Days of Week vs Qty")
        ax2.set_xlabel("Days of Week")
        ax2.set_ylabel("Quantity")

        filename = f"Days of Week vs Price-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "").replace(",",
                                                                                                                 "")

        static_folder = app.static_folder

        graphs_folder = os.path.join(static_folder, 'graphs')
        os.makedirs(graphs_folder, exist_ok=True)

        filepath = os.path.join(graphs_folder, filename)

        plt.savefig(filepath)
        static_url = url_for('static', filename='')
        url2 = f"{static_url}graphs/{filename}"

        title = ["Days of Week vs Qty", "Days of Week vs Price"]
        filename = [url1, url2]

        weekQty, weekSales = [], []
        for oneData in range(len(days_of_week)):
            weekQty.append([days_of_week[oneData], quantities[oneData]])
            weekSales.append([days_of_week[oneData], prices[oneData]])

        return make_response(
            render_template('analysis-weekly.html', filename=filename, title=title, weekQty=weekQty,
                            weekSales=weekSales),
            200)
