#!/usr/bin/python

# Monitors all cryptocurrencies on the Crypsty marketplace until one drop in price relative to another, at which point buys that currency and then
# issues a sell order at the original price. Outdated.

import fetcher
import operator
import sys
import time
import crypstyID
import cPickle as pickle
import requests
import json
import time
import testing

FEE_ESTIMATE = -0.8 # 4% fee estimate. Very pessimistic
TRADE_SIZE = 0.01 # Size of each trade (BTC)
MAX_ORDER_TIME = 120 # Time to wait for order to go through before abandoning


#ordersfile = open("activeOrders.pkl", "wb")
# Maybe needs to be read?
#active_orders = pickle.load(ordersfile)
############################################################33
# Get the market info
try:
    r = requests.get("http://pubapi.cryptsy.com/api.php?method=marketdatav2")
    m = r.json()['return']['markets']
    marketInfo = dict([(k, int(v['marketid'])) for k, v in m.iteritems()])
except:
    sys.exit("ERROR: Could not fetch market IDs")


 

while 1:
    # Dictionary for keeping track of coin prices
    pricehistory = {}

    try:
        print "Fetching market data...",
        data = testing.getInfo2()
        print "done"

    except:
        sys.exit("ERROR: Could not fetch market data.")

    print "Getting wallet balances...",
    
    balances = testing.getBalances()

    print "done"
    
    for marketName in data.keys():
        print marketName
        # Set the current price as the base price, ie the price we will compare
        try:
            price = data[marketName]["sellorders"][0]["price"]
            pricehistory[marketName] = {}
            pricehistory[marketName]["price"] = price
        except:
            print "Couldn't get price.."

    orders = fetcher.getAllOrders()

    failCount = 0
    tradeFound = 0
    while not tradeFound:
        # If we get the data, set flag
        print "No trade found, getting latest prices...",
        try:
            data = testing.getInfo2()
        except:
            "Failed to fetch data"
        print "done"
        fetched = 1
        if fetched:
            maxDiff = 0.00
            maxDiffCoin = "None"
            for marketName in data.keys():
                if "BTC" in marketName and data[marketName]["sellorders"]:
                    print marketName
                    # Get new price of the coin
                    curr_price = data[marketName]["sellorders"][0]["price"]
                    pricehistory[marketName]["newprice"] = curr_price
                    initialprice = pricehistory[marketName]["price"]
                    print curr_price
                    print "Initial price: " + initialprice
                    print "Current price: " + curr_price
                    difference = float(curr_price) - float(initialprice)
                    #print float(curr_price)
                    #print float(initialprice)
                    if difference < 0:
                        # If the price has dropped
                        percentage = ((difference) / float(initialprice)) * 100
                        # Put the difference in the dictionary
                        pricehistory[marketName]["diff"] = difference   
                        if maxDiff > percentage:
                            maxDiff = percentage
                            maxDiffCoin = marketName
        if (maxDiff < FEE_ESTIMATE):
            #active_orders.append(maxDiffCoin)
            ##################################################33
            #pkl.dump(hahahahahha) ## <<
            tradeFound = 1

    BTCPrice = (1/float(pricehistory[maxDiffCoin]["newprice"]))

    # How many of the coin we can buy
    amountWeCanBuy = BTCPrice * (TRADE_SIZE)
                                    

    print balances["BTC"]
    print "Trading..."
    print "Max difference was %f, with market %s" % (float(maxDiff), maxDiffCoin)
    # Make order, sell all litecoins we have for the coin that went down the most
    print "Placing order: selling %f litecoins for %f" % (float(balances["BTC"]), float(pricehistory[maxDiffCoin]["newprice"]))
    try:
        order = testing.placeOrder(marketInfo[maxDiffCoin], "buy", amountWeCanBuy, float(pricehistory[maxDiffCoin]["newprice"]))
        print order
    except:
        sys.exit("Order failed (BTC >> coin)...")

    # Get orders
    try:
        orders = testing.getAllOrders()
        print orders["return"]
    except:
        print "No orders"

    # Wait until our previous order has completed
    currentOrderActive = 1
    timeOrderPlaced = time.time() # Time the order was placed
    needBreak = 0
    while currentOrderActive:
        try:
            orders = testing.getAllOrders()
            print orders
        except:
            print "Couldn't fetch wallet status...retrying"
        found = 0
        for each in orders:
            # if we have an order for the current coin being traded
            if int(each[u'marketid']) == int(marketInfo[maxDiffCoin]):
                print "+++++++++" + str(marketInfo[maxDiffCoin])
                orderid = each[u'orderid']
                found = 1
        timeElapsed = time.time() - timeOrderPlaced
        if timeElapsed > MAX_ORDER_TIME and found:
            amountWeCanBuy = float(each[u'orig_quantity']) - float(each[u'quantity'])
            testing.cancelOrder(orderid)
            needBreak = 1 # Order taking too long, so need to restart whole program
            break
        if found == 1:
            continue
        currentOrderActive = 0
    if needBreak == 1:
        print "Order took too long (120 seconds), selling what we have"
    print "ORDER COMPLETE --------------------------------------"

    # Now make the order back to BTC

    # Last trade has gone through, do reverse order
    newCoinBalance = amountWeCanBuy
    try:
        order = testing.placeOrder(marketInfo[maxDiffCoin], "sell", newCoinBalance, pricehistory[maxDiffCoin]["price"])
        print order
        expectedProfit = (float(pricehistory[maxDiffCoin]["price"]) - (float(pricehistory[maxDiffCoin]["newprice"]) * 0.99)) * newCoinBalance
        print "EXPECTED PROFIT: %f" % expectedProfit
    except:
        print "couldnt place 2nd order"
    # Trade done. no longer active order so remove from list
    #active_orders.delete(maxDiffCoin)
    #Done
        

    
