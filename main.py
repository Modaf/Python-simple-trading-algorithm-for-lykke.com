import json
import urllib3
import time
urllib3.disable_warnings()
http = urllib3.PoolManager()
APIKEY = 0


def assetPairs() :
    r = http.request('GET', 'https://hft-service-dev.lykkex.net/api/AssetPairs')
    liste = json.loads(r.data)
    for k in liste :
        print(k["Name"], end = " -- ")
    return liste

def assetPairsId(id) :
    r = http.request('GET', 'https://hft-service-dev.lykkex.net/api/AssetPairs/'+str(id))
    liste = json.loads(r.data)
    print(liste["Name"])
    return liste

def isAlive() :
    r = http.request('GET', 'https://hft-service-dev.lykkex.net/api/IsAlive')
    liste = json.loads(r.data)
    try :
        print("Server is alive, version :", liste["Version"])
        if liste["IssueIndicators"] != [] :
            print("Issues indicators :")
            for k in liste["IssueIndicators"] :
                print(k)
        else :
            print("Without issue indicators x)")
        return True
    except :
        print("Server is dead, due to :", liste["ErrorMessage"])
        return False

def getBalance() : #untested coz no api key given
    r = http.request('GET', 'https://hft-service-dev.lykkex.net/api/Wallets', fields = {'api-key' : APIKEY})
    liste = json.loads(r.data)
    for k in liste :
        print(k["Balance"], "of", k["AssetId"], "including", k["Reserved"], "reserved")
    return liste

def marketOrder(assetId, buyorsell, volume) : #untested coz no api key given
    order = {"AssetPairId": assetId, "OrderAction": buyorsell, "Volume": volume}
    order = json.dumps(order)
    r = http.request('POST', 'https://hft-service-dev.lykkex.net/api/Orders/market', fields = {'order' : order, 'api-key' : APIKEY})
    try :
        liste = json.loads(r.data)
        try :
            print(liste["Error"])
            return False
        except :
            print("Executed market order", str(buyorsell), "volume :", volume, "on asset", str(assetId))
            return True
    except :
        return #print("Something went wrong :/")

def limitOrder(assetId, buyorsell, volume) : #untested coz no api key given
    order = {"AssetPairId": assetId, "OrderAction": buyorsell, "Volume": volume}
    order = json.dumps(order)
    r = http.request('POST', 'https://hft-service-dev.lykkex.net/api/Orders/limit', fields = {'order' : order, 'api-key' : APIKEY})
    try :
        liste = json.loads(r.data)
        try :
            print(liste["Error"])
            return False
        except :
            print("Executed limit order", str(buyorsell), "volume :", volume, "on asset", str(assetId))
            return True
    except :
        return #print("Something went wrong :/")

def cancelOrder(id) : #untested coz no api key given
    r = http.request('POST', 'https://hft-service-dev.lykkex.net/api/Orders/'+str(id)+'/Cancel', fields = {'id' : id, 'api-key' : APIKEY})
    if r.status == 20 :
        print("Order", id, "canceled")
        return True
    else :
        print("Order not canceled")
        return False

def infoOrder(id) : #untested coz no api key given
    r = http.request('GET', 'https://hft-service-dev.lykkex.net/api/Orders/'+str(id), fields = {'id' : id, 'api-key' : APIKEY})
    liste = json.loads(r.data)
    print("Status", liste["Status"])
    print("Remaining volume", liste["RemainingVolume"])
    print("Price", liste["Price"], "on assets id", liste["AssetPairId"])
    return liste

def allOrder() : #untested coz no api key given
    status = ["Pending", "InOrderBook", "Processing", "Matched", "NotEnoughFunds", "NoLiquidity", "UnknownAsset", "Cancelled", "LeadToNegativeSpread"]
    for s in status :
        r = http.request('GET', 'https://hft-service-dev.lykkex.net/api/Orders?status='+s, fields = {'api-key' : APIKEY})
        liste = json.loads(r.data)
        print("Order", s)
        for k in liste :
            print("Remaining volume", k["RemainingVolume"])
            print("Price", k["Price"], "on assets id", k["AssetPairId"])
        print("")

def orderBookAsset(id) :
    r = http.request('GET', 'https://hft-service-dev.lykkex.net/api/OrderBooks/'+str(id))
    #isBuy looks like useless coz false => negative value of volume
    liste = json.loads(r.data)
    buy = []
    sell = []
    for k in liste :
        if k["IsBuy"] :
            buy.extend(k["Prices"])
        else :
            sell.extend(k["Prices"])
    return (buy, sell)

#End of API no need of full order book for all assets


#Buy low sell high, low level => we dont look at volume
volumeTraded = 50
assetTraded = "AUDUSD"
frequency = 0.5

#End of parameters
miniBuy = 99999999999
maxiSell = 0
notBuyYet = True
notSellYet = True

while True :
    time.sleep(1/frequency)
    #First we uptade miniBuy and maxiSell
    buy, sell = orderBookAsset(assetTraded)
    buyAvalable = min([i["Price"] for i in buy])
    sellAvalable = max([i["Price"] for i in sell])
    
    miniBuy = min(miniBuy, buyAvalable)
    maxiSell = max(maxiSell, sellAvalable)
    print("Order book analysed // min buy :", miniBuy, " // top sell :", maxiSell, "// spread :", maxiSell-miniBuy)
    
    #We then look if we can buy lower than maxiSell or sell higher than maxiBuy
    if buyAvalable < maxiSell and notBuyYet :
        notBuyYet = not marketOrder(assetTraded, "Buy", volumeTraded)
    if sellAvalable > miniBuy and notSellYet :
        notSellYet = not marketOrder(assetTraded, "Sell", volumeTraded)

    #End of the strategy, we may loop on assets using multithreading, was asking simple strategy : it cant lose
