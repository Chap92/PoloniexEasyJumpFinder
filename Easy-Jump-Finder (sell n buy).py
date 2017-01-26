import urllib.request, urllib.parse, urllib.error
import json
import time
import hmac,hashlib
import winsound
import datetime

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))
 
class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret
 
    def post_process(self, before):
        after = before
 
        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in range(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                           
        return after
 
    def api_query(self, command, req={}):
 
        if(command == "returnTicker" or command == "return24hVolume"):
            ret = urllib.request.urlopen(urllib.request.Request('https://poloniex.com/public?command=' + command))
            str_response = ret.readall().decode('utf-8')
            return json.loads(str_response)
        elif(command == "returnOrderBook"):
            ret = urllib.request.urlopen(urllib.request.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            str_response = ret.readall().decode('utf-8')
            return json.loads(str_response)
        elif(command == "returnMarketTradeHistory"):
            ret = urllib.request.urlopen(urllib.request.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            str_response = ret.readall().decode('utf-8')
            return json.loads(str_response)
        elif (command == "returnLoanOrders"):
            ret = urllib.request.urlopen(urllib.request.Request('https://poloniex.com/public?command=' + "returnLoanOrders" + '&currency=' + str(req['currency'])))
            str_response = ret.readall().decode('utf-8')
            return json.loads(str_response)
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.parse.urlencode(req).encode('ASCII')
 
            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }
 
            ret = urllib.request.urlopen(urllib.request.Request('https://poloniex.com/tradingApi', post_data, headers))
            str_response = ret.readall().decode('utf-8')
            jsonRet = json.loads(str_response)
            return self.post_process(jsonRet)
 
 
    def returnTicker(self):
        return self.api_query("returnTicker")
 
    def return24Volume(self):
        return self.api_query("return24hVolume")
 
    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})
 
    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})
 
 
    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')
 
    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})
 
 
    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})
 
    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})
 
    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})
 
    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})
 
    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})

    def returnMarginAccountSummary(self):
        return self.api_query('returnMarginAccountSummary')

    def returnLoanOrders (self, currency):
        return self.api_query('returnLoanOrders', {"currency":currency})

    def marginSell (self, currencyPair,rate,amount,lendingRate):
        return self.api_query('marginSell',{"currencyPair":currencyPair,"rate":rate,"amount":amount, "lendingRate":lendingRate})
        
    def marginBuy (self, currencyPair,rate,amount,lendingRate):
        return self.api_query('marginBuy',{"currencyPair":currencyPair,"rate":rate,"amount":amount, "lendingRate":lendingRate})

    def getMarginPosition(self, currencyPair):
        return self.api_query('getMarginPosition',{"currencyPair":currencyPair})
    
    def closeMarginPosition (self, currencyPair):
        return self.api_query('closeMarginPosition',{"currencyPair":currencyPair})
    
                              

myAccountKey = None #Substitute your account key
myAccountSecret = None #Substitute your account secret
myByteKey = myAccountKey.encode('utf-8')
myByteSecret = myAccountSecret.encode('utf-8')
myMasterClass = poloniex (myByteKey, myByteSecret)

allCoins = ['BTC_XMR', 'BTC_ETH', 'BTC_FCT', 'BTC_BURST', 'BTC_LSK', 'BTC_SDC', 'BTC_ETC', 'BTC_BBR', 'BTC_SJCX', 'BTC_DASH', 'BTC_DGB', 'BTC_MAID', 'BTC_QORA', 'BTC_NAV', 'BTC_BTS', 'BTC_AMP', 'BTC_XRP', 'BTC_VTC', 'BTC_EXP', 'BTC_STEEM', 'BTC_BCY', 'BTC_NSR', 'BTC_XCP', 'BTC_NXT', 'BTC_CLAM', 'BTC_LBC', 'BTC_LTC', 'BTC_GRC', 'BTC_FLDC', 'BTC_HUC', 'BTC_SC', 'BTC_IOC', 'BTC_OMNI', 'BTC_NAUT', 'BTC_GAME', 'BTC_SYS', 'BTC_STR', 'BTC_XEM', 'BTC_XVC', 'BTC_BLK', 'BTC_FLO', 'BTC_QTL', 'BTC_SBD', 'BTC_RADS', 'BTC_VOX', 'BTC_DOGE', 'BTC_XMG', 'BTC_DCR', 'BTC_CURE', 'BTC_NEOS', 'BTC_NOBL', 'BTC_EMC2', 'BTC_BCN', 'BTC_BITS', 'BTC_MYR', 'BTC_BELA', 'BTC_PPC', 'BTC_HZ', 'BTC_NOTE', 'BTC_VIA', 'BTC_QBK', 'BTC_VRC', 'BTC_XPM', 'BTC_UNITY', 'BTC_RBY', 'BTC_BTCD', 'BTC_XBC', 'BTC_POT', 'BTC_RIC', 'BTC_NMC', 'BTC_C2', 'BTC_BTM']
minPcentChnge = -0.01
minBTCVol = 1

coinPosArray = []
#print(myMasterClass.returnOrderBook('BTC_1CR'))
def main(coinPosArray):
       print("Started...")
       coinTicker = myMasterClass.returnTicker()
       counter = 0
       for theCoin in allCoins:
           if (float(coinTicker[theCoin]['percentChange']) > minPcentChnge):
               if (float(coinTicker[theCoin]['baseVolume']) > minBTCVol):
                   coinOrderBook = myMasterClass.returnOrderBook(theCoin)

                   # [percentage change per BTC, BTC number, percentage change]
                   askCoinData = getAskChangePerBTC (theCoin, coinOrderBook)
                   bidCoinData = getBidChangePerBTC (theCoin, coinOrderBook)

                   askBidDiff = round((askCoinData[0] - bidCoinData[0]),2)


                   #[coin string, 'ask-bid change per BTC' difference, ask change per BTC, bid change per BTC, number of BTC, percentage change]
                   coinPosArray = insertToIndexedArray(coinPosArray, [theCoin, askBidDiff, askCoinData[0], bidCoinData[0], round(askCoinData[1],5), round(askCoinData[2],2)])
                   time.sleep(3)
           counter += 1
           print(str(counter) + "/" + str(len(allCoins)) +  " analyzed...")
       print('\n\n\n')

       for eachCoin in coinPosArray:
           print(eachCoin[0] + ": Ask-Bid Diff: " + str(eachCoin[1]) + ", Ask Change/BTC= " + str(eachCoin[2]) + ", Bid Change/BTC= " + str(eachCoin[3]) + ", BTC= " + str(eachCoin[4]) + ", Percent Change= " + str(eachCoin[5]) + ", Vol.= " + str(coinTicker[eachCoin[0]]['baseVolume']))
    

def getAskChangePerBTC (cPair, coinBook):
    sellOrders = coinBook['asks']
    firstAskPrice = float(sellOrders[0][0])
    lastAskPrice = float(sellOrders[len(sellOrders)-1][0])
    percentChnge = ((lastAskPrice - firstAskPrice)/ firstAskPrice) * 100

    numBTC = 0
    for eachOrder in sellOrders:
        numBTC += (float(eachOrder[0]) * eachOrder[1])

    # [percentage change per BTC, BTC number, percentage change]
    coinData = [round((percentChnge/numBTC),2), numBTC, percentChnge]
    return coinData


def getBidChangePerBTC (cPair, coinBook):
    buyOrders = coinBook['bids']
    firstBuyPrice = float(buyOrders[0][0])
    lastBuyPrice = float(buyOrders[len(buyOrders)-1][0])
    percentChnge = ((firstBuyPrice -lastBuyPrice)/ firstBuyPrice) * 100

    numBTC = 0
    for eachOrder in buyOrders:
        numBTC += (float(eachOrder[0]) * eachOrder[1])

    # [percentage change per BTC, BTC number, percentage change]
    coinData = [round((percentChnge/numBTC),2), numBTC, percentChnge]
    return coinData

def insertToIndexedArray(allCoinVolChangeArray, curCoinArray):
# This function accepts an array of coin-pair values(array of arrays) and a new
# coin-pair value as its parameters. It inserts the new coin-pair value into
# the correct index of the array (decending order) and returns it.
    if (len(allCoinVolChangeArray) == 0):
        return [curCoinArray]
    valIndex = findCoinValFitIndex (allCoinVolChangeArray, curCoinArray[1])
    firstPart = allCoinVolChangeArray[0:valIndex]
    lastPart =  allCoinVolChangeArray[valIndex:]
    return firstPart + [curCoinArray] + lastPart

    

def findCoinValFitIndex (manyCoinVolArray, curCoinVal):
# Recursive helper function to "insertToIndexedArray". Returns the index at
# which the coin-pair value should be inserted.

    if len(manyCoinVolArray) == 1:
        if curCoinVal > manyCoinVolArray[0][1]:
            return 0
        else:
            return 1
    else:
        midIndex = round(len(manyCoinVolArray)/2)
        if curCoinVal > manyCoinVolArray[midIndex][1]:
            return findCoinValFitIndex (manyCoinVolArray[0:midIndex], curCoinVal)
        else:
            return midIndex + findCoinValFitIndex (manyCoinVolArray[midIndex:], curCoinVal)                                         

main(coinPosArray)
