import time
import json
import config
import datetime
import os
import redis
import threading
from zoneinfo import ZoneInfo
from flask import Flask, request, render_template
from binance.client import Client
from binance.enums import *
app = Flask(__name__)
db = redis.from_url(os.environ['REDIS_URL'])
###################################################################################################

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol="ETHUSDT", order_type=ORDER_TYPE_MARKET):
    '''
    This function send the order to the webhook which will be placed immediately on the exchange.

    :param side: str
        Declare whether it is a 'BUY' or 'SELL' signal
    :param quantity: float
        The amount to be traded, expressed in USD
    :param symbol: str
        The cryptocurrency trading pair
    :param order_type: str
        Declare whether it is a market or limit order
    :return: str or None
        If unsuccessful, prints 'an exception occurred' along with the error
    '''
    try:
        print(f"sending order {order_type} - {side} {quantity} {symbol}")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occurred - {}".format(e))
        return False

    return True

##################################################################################################
def getQuantity(symbol):
    '''
    This function returns the available amount of given cryptocurrency symbol in the user's wallet,
    minus 0.1% of the amount for gas & exchange fees.

    :param symbol: str
        Takes a string as an argument that is a 2-4 letter cryptocurrency symbol
    :return: float
        Returns the quantity of the given cryptocurrency symbol used available multiplied by 0.999
        and rounded to 6 decimal places to be accepted on the Binance exchange
    '''
    try:
        available_balance = client.get_asset_balance(asset=symbol)
        asset_total = float(available_balance['free'])
        asset_total = (asset_total * (0.999))
        asset_total = round(asset_total, 6)
        return asset_total
    except Exception as e:
        print("an exception occured {}".format(e))
        return False


def getQuantity2(symbol):
    '''
    This function calculates the available amount of USD in a wallet and converts it in terms of
    the given cryptocurrency value, in this case, USD is being converted to ETH.

    :param symbol: str
        Takes a string as an argument that is a 2-4 letter cryptocurrency symbol
    :return: float
        Returns the quantity of the given cryptocurrency symbol used available multiplied by 0.999
        and rounded to 6 decimal places to be accepted on the Binance exchange
    '''
    try:
        availableUSDT = client.get_asset_balance(asset=symbol)
        ETH_info = client.get_symbol_ticker(symbol="ETHUSDT")
        ETH_price = float(ETH_info['price'])
        USDT2ETH = float(availableUSDT['free']) / ETH_price
        USDT2ETH = (USDT2ETH * (0.999))
        USDT2ETH = round(USDT2ETH, 6)
        return USDT2ETH
    except Exception as e:
        print("an exception occured {}".format(e))
        return False

def sell():
    '''
    This function calculates an acceptable decimal to be accepted by the Binance exchange.

    :return: None
    '''
    info = client.get_symbol_info(symbol="ETHUSDT")
    f = [i["stepSize"] for i in info["filters"] if i["filterType"] == "LOT_SIZE"][0]
    qty = round(getQuantity("ETH"), f.index("1") - 1)
    return qty

def buy():
    '''
    This function calculates an acceptable decimal to be accepted by the Binance exchange.

    :return: None
    '''
    info = client.get_symbol_info(symbol="ETHUSDT")
    f = [i["stepSize"] for i in info["filters"] if i["filterType"] == "LOT_SIZE"][0]
    qty = round(getQuantity2("USDT"), f.index("1") - 1)
    return qty

###################################################################################################

@app.route("/")
def welcome():
    '''
    This function initializes the landing page for the web server made with Flask.

    :return: None
    '''
    return render_template('index.html')

@app.route("/webhook", methods=['POST'])
def webhook():
    '''
    This function sends signals as POST requests to the Flask web app.

    :return: str
        Prints whether or not the order was successful
    '''
    leaveloop = False
    data = json.loads(request.data)

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        leaveloop = True
        db.set("leaveloop", 'true')
        print("leave Loop set to true")
    else:
        db.set("leaveloop", 'false')
        print("leave Loop set to false")
    print(data['ticker'])
    side = data['strategy']['order_action']
    print(side)
    print(datetime.datetime.now(ZoneInfo("America/New_York")))
    order_response = False
    time.sleep(30)
    if side == 'BUY':
        order_response = order('BUY', buy())
    elif side == 'SELL':
        order_response = order('SELL', sell())

    flag = order_response
    threading.Thread(target=loop_thread, args=(data, order_response, flag, leaveloop, side)).start()
    if order_response:
        print('order executed')
        return {
            "code": "success",
            "message": "order executed"

        }
    else:
        print("order failed")
        return {
            "code": "error",
            "message": "order failed"
        }

def loop_thread(data, order_response, flag, leaveloop, side):
    '''
    This function will wait to see if there is a reversal occuring in the market (currency suddenly sytarted going or down after a signal is sent)
    and will revert the order. Ex: a buy signal will then be a sell signal and vice versa.

    :param data: str
        JSON format that confirms a passowrd for security
    :param order_response: bool
        Enters while loop if an order has been placed (order_response == True)
    :param flag: bool
        A mirror of order_response (This was only for debugging purposes)
    :param leaveloop: bool
        Leaves the while loop once successful (This was only for debugging purposes)
    :param side: str
        Declare whether it is a 'BUY' or 'SELL' signal
    :return: str
        prints if the loop has been exited (This was only for debugging purposes)
    '''
    date1 = str(datetime.datetime.now(ZoneInfo("America/New_York")))
    while flag and not leaveloop:
        leaveloop = (db.get("leaveloop").decode() == 'true')
        if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
            break
        if order_response == True:
            now = str(datetime.datetime.now(ZoneInfo("America/New_York")))
            date = date1[0:10]
            nextOddHour = next_odd_hour(date1[11:16])
            if nextOddHour == "01:00":
                nextdate = nextDate(date)
                if (now[0:10] == nextdate) and (now[11:16] == nextOddHour) and (order_response == True):
                    if side == 'BUY':
                        order('SELL', sell())
                        flag = False
                    elif side == 'SELL':
                        order('BUY', buy())
                        flag = False
            else:
                now = str(datetime.datetime.now(ZoneInfo("America/New_York")))
                date = date1[0:10]
                nextOddHour = next_odd_hour(date1[11:16])
                if (now[0:10] == date) and (now[11:16] == nextOddHour) and (order_response == True):
                    if side == 'BUY':
                        order('SELL', sell())
                        flag = False
                    elif side == 'SELL':
                        order('BUY', buy())
                        flag = False
    print(f"Leaving loop - {data['passphrase']}")


def next_odd_hour(time):
    '''
    This function returns the next odd hour based on the input. Ex: 15:00 will return 17:00,
    and 16:00 will return 17:00.

    :param time: str
        Current time
    :return: str
        Next odd hour of the current time
    '''
    hour = int(time[:2])
    minute = int(time[3:])
    if minute % 30 == 0:
        if hour % 2 == 0:
            hour += 1
        else:
            hour += 2
    else:
        if hour % 2 == 0:
            hour += 1
        else:
            hour += 2
    if hour > 23:
        hour = hour - 24
    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)
    if minute < 10:
        minute = '0' + str(minute)
    else:
        minute = str(minute)
    minute = "01"
    return hour + ':' + minute


def nextDate(date):
    '''
    This function calculates the date, if nextOddHour returns 23:00 (11 P.M.)
    while taking into consideration that the next date could be in a different month, year or even
    occur in a leap year, where February has 29 days instead of 28.

    :param date: str
        Current Date
    :return: str
        Returns the day after the input argument
    '''
    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:])
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        if day == 31:
            day = 1
            month += 1
            if month == 13:
                month = 1
                year += 1
        else:
            day += 1
    elif month == 2:
        if year % 4 == 0:
            if day == 29:
                day = 1
                month += 1
            else:
                day += 1
        else:
            if day == 28:
                day = 1
                month += 1
            else:
                day += 1
    else:
        if day == 30:
            day = 1
            month += 1
        else:
            day += 1
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)
    if day < 10:
        day = '0' + str(day)
    else:
        day = str(day)
    return str(year) + '-' + month + '-' + day
