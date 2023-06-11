import os
from datetime import datetime

import matplotlib.pyplot as plt
from flask import url_for

from src import app
from src.models import Menu


class Help:
    @staticmethod
    def fetchMenu():
        menu = Menu.query.all()
        menuDict = {}
        for i in menu:
            menuDict[i.id] = i.name + " - Rs. " + str(i.price)
        return (menuDict)

    @staticmethod
    def fetchOrderData(form):
        foodMenu = Help.fetchMenu()
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

    @staticmethod
    def plotItemGraph(X, Y, title, size):
        if size == False:
            fig, ax = plt.subplots()  # Create a new figure and axes for each graph
            ax.plot(X, Y, marker='o', color="gold")
        else:
            fig, ax = plt.subplots(figsize=(40, 20))  # Set the desired width and height of the figure
            ax.plot(X, Y, marker='o', color="gold")
            ytick = range(int(min(Y)), int(max(Y)), 300)
            ax.set_yticks(list(ytick))

        label = title.split(" vs ")
        xlabel = label[0]
        ylabel = label[1]

        if 'Price' in title and size:
            ylabel += " (Rs.)"

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.set_title(title)
        ax.set_xticklabels(X, rotation=45, ha='right')  # Corrected method name

        ax.grid(True)

        filename = f"{title}-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "").replace(",", "")

        static_folder = app.static_folder

        graphs_folder = os.path.join(static_folder, 'graphs')
        os.makedirs(graphs_folder, exist_ok=True)

        filepath = os.path.join(graphs_folder, filename)

        plt.savefig(filepath)
        static_url = url_for('static', filename='')
        url = f"{static_url}graphs/{filename}"
        return url

    @staticmethod
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

        filename = f"{title}-{str(datetime.now().strftime('%B %d, %Y'))}".replace(" ", "").replace(",", "")

        static_folder = app.static_folder

        graphs_folder = os.path.join(static_folder, 'graphs')
        os.makedirs(graphs_folder, exist_ok=True)

        filepath = os.path.join(graphs_folder, filename)

        plt.savefig(filepath)
        static_url = url_for('static', filename='')
        url = f"{static_url}graphs/{filename}"
        return url
