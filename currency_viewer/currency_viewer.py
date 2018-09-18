# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 19:21:28 2017

@author: smechaab

 Prints the account balance and will in future send it via email,
 with obvisouly your own email adress (SOON).
 
 Please fill and copy your kraken.key file in the same directory.
 
 If you have any questions or suggestions, please email me at 
 s.mechaab@protonmail.com.
 
 And please, don't hesitate to feedback !
 
v0.2.1
Extracts data and store them in "data.csv"

1. Displays the different amount of crypto currencies you own on your Kraken wallet.
2. Displays the total crypto money you own in equivalent fiat money.
3. Adapted to the crypto and fiat currencies you already own.
4. If you don't own any fiat money on your Kraken wallet, it will be displayed the equivalent in USD.
5. Works with multi-fiat currencies wallets.
6. Writes data in a csv file located in the project folder (default : data.csv).

NOTE: Some bugs need to be fixed with fiat currencies other than EUR or USD,
it will be patched in the next one.


 
"""
#%% Includes
import krakenex
import csv
import sys
import os

#%% Class init
class CurrencyViewer:
    def __init__(self):
        self.k = krakenex.API()
        self.k.load_key('kraken.key')
        self.currencies = [] #List of differents currencies owned by user
        self.market = []     #List of markets concerned by currencies in user's wallet
        self.balance = []    #List of the differents amount of crypto currencies owned by user
        
        self.debugmode = False #Change to switch to debugmode 
        
#%% Main purpose of this script
# It calls every function in order, it allows to get the full data for user
    def processCViewer(self, log=True, currency="USD", time="rfc1123"):
        
        data, c, f = self.collectData()
        price = self.getMarketPrice(c)
        self.processingConversion(price,c,f)
        self.displayResults()
        if(log==True):
            self.writeLog(self.values, currency = currency, time = time)
        
#%% Exit error handling function
    def _exitError(self):
        sys.exit("Can't continue with error")

#%% Collecting data
    def collectData(self):
        data = self.k.query_private('Balance')
        if (data['error']) : 
                print("Error : ",data['error'])
                self._exitError()
                
        #We find currencies concerned by the user wallet
        if (self.debugmode == True):
            #DEBUG, examples
            data['result']["ZUSD"] = data['result']["XZEC"]
            del data['result']["XZEC"]
            #Can be used to test if others currencies (e.g ZPJY) are compatibles with others market pairs you are into. 
        
        
        #Exctracts crypto currencies
        crypto_index = [c for c in data['result'] if(not c.startswith("Z"))]
        #We get every symbols except the ones which starts with "Z" (these are fiat currencies)
        #print (crypto_index)
        if crypto_index == [] : sys.exit("Can't find any crypto currency on your wallet yet.")
        for i in crypto_index:
            self.currencies.append(i)
        
        #Extracts fiat currencies
        fiat_index = [c for c in data['result'] if (c.startswith("Z"))]
        if fiat_index == [] :
            print("Currencies will be converted in USD by default")
            fiat_index.append(0)
            self.currencies.append('ZUSD')
        else:
            self.currencies = self.currencies + fiat_index
        
        print("Currencies on your wallet : ",self.currencies)

        #Here we get our current currency situation
        #raw currency values to be extracted
        for i in crypto_index:
            self.balance.append(data['result'][i])
        
        for i in fiat_index:
            self.balance.append(data['result'][i])
        #We extract what we need

        #Converting balance to float (needed for operations)
        self.balance = [float(i) for i in self.balance]
        print("Current balance you own : ",self.balance)
        #Casting current balance to float
        
        print (crypto_index, fiat_index)
        crypto_index = [i[1:] if(i.startswith("X")) else i for i in crypto_index]
        fiat_index = [i[1:] if(i.startswith("Z")) else i for i in fiat_index]
        #We remove the first char in purpose to get the correct acrynom for market ask \
        #(e.g : XXBT -> XBT, ZEUR -> EUR)
        return data, crypto_index, fiat_index

#%% Get XBT to FIAT price
    def getXBTtoFiatPrice(self, fiat):
        data_price = self.k.query_public('Ticker',{'pair': "XBT"+fiat,})
        print("XBT"+fiat)
        #Error ?
        if (data_price['error']) :
            
            print(data_price['error'][0])
            if (data_price['error'][0] == "EQuery:Invalid asset pair" or "EQuery:Unknown asset pair"):
                    print("Check market list, ","XBT"+fiat," pair doesn't exist on kraken exchange. Erasing from market list.")
                    #So we get the currency on BTC market and we will convert it later
                    #TODO
            else:
                # We leave the program if this is not an Invalid asset pair error
                sys.exit("Can't continue with error")
        else:
            index=list(data_price['result'].keys())[0]
        return data_price['result'][index]['c'][0]

#%% getMarketPrice
    def getMarketPrice(self, crypto_index):
        #We prepare our list of markets exchange we are interested in
        
        for i in crypto_index:
            if(i != "XBT"):
                self.market.append(i+"XBT")
                
        print("Markets concerned : ",self.market) #This is optionnal
        
        #Extracts price of every currencies user is involved onto
        
        price = []
        i=0
        while(i < len(self.market)):  #We use a while loop because the for loop doesn't allow us to modifiy i index during iteration
            data_price = self.k.query_public('Ticker',{'pair': self.market[i],})
            print(self.market[i])
        #Error ?
            if (data_price['error']) :
                
                print(data_price['error'][0])
                if (data_price['error'][0] == "EQuery:Invalid asset pair" or "EQuery:Unknown asset pair"):
                        print("Check market list, ",self.market[i]," pair doesn't exist on kraken exchange. Erasing from market list.")
                        #So we get the currency on BTC market and we will convert it later
                        self.market.append(self.market[i].replace("EUR","XBT"))
                        self.market.remove(self.market[i])

                else:
                    # We leave the program if this is not an Invalid asset pair error
                    sys.exit("Can't continue with error")
            else:
                index=list(data_price['result'].keys())[0]
                p = data_price['result'][index]['c'][0]
                price.append(p)
                print("Price of ",self.market[i]," added")
                price[i] = float(price[i])
                #(Thanks to plguhur)
                i+=1
                #price is a list of str -> cast to float
        return price
                
#%% updateFiatInTotal
    def updateFiatInTotal(self, fiat):
        xbtfiat = self.getXBTtoFiatPrice(fiat)
        self.fiatbtc_pair.update({fiat: xbtfiat})
        self.total[fiat] = self.btc_total * float(xbtfiat)

#%% processingConversion
    def processingConversion(self, price, crypto_index, fiat_index):
        #Finally multiplying balance of crypto of user wallet BY actual real-time price of market
        # price of coin in FIAT * amount of coin = Estimated value of currencies in FIAT MONEY
        self.values = {}
        self.total = {}
        self.fiatbtc_pair = {}

        self.btc_total = 0
        self.totals = []
        for i in fiat_index:
            self.total.update({i : ''})
            self.totals.append(0)
        #Initializing in case we never get the market data    
            
        """
        #Converting data from each fiat to their corresponding market in XBT (XRP with XRPXBT, ETHXBT,... \
        # via string recognition
        """
        for i in range(len(self.market)):
            if(self.market[i][0:3] in self.currencies):
                crypto_tmp = self.market[i][0:3]
            elif(self.market[i][0:4] in self.currencies):
                crypto_tmp = self.market[i][0:4]
                
            elif('X'+self.market[i][0:3] in self.currencies):
                crypto_tmp = 'X'+self.market[i][0:3]
        
            self.values.update({self.market[i] : self.balance[self.currencies.index(crypto_tmp)] * price[i]})
            print(self.market[i], self.balance[self.currencies.index(crypto_tmp)], price[i])
            
            if(self.market[i][0]=='D'): fiat_tmp = self.market[i][4:7]    
            else: fiat_tmp = self.market[i][3:6]
            
            self.btc_total += self.values[self.market[i]]
            print("btc_total =",self.btc_total)
            
        for i in fiat_index:
            self.updateFiatInTotal(i)
            
        for n in range(len(fiat_index)):
            self.values.update({self.currencies[len(crypto_index)+n] : self.balance[len(crypto_index)+n]})
        
#%% Displaying
    def displayResults(self):
        print(self.values)
        print(self.total)

#%% Log file writer
    def createLogFile(self, filename, assets, writeFiat):
        log_file = open(filename, 'w', newline='') 
        wr = csv.writer(log_file)
        print ("Creating a log file ", filename)
        header = []
        #Generating the first row (columns titles)
        header.append("Date")
        
        dict_assets = assets
        
        if(writeFiat==False):
            for fiat in list(dict_assets['result']):
                if(fiat.startswith("Z")):
                    dict_assets['result'].pop(fiat)
            
        header = header + list(dict_assets['result'].keys())
        header.append("Total")
        header.append("Var(%)")
        header.append("Currency")
        wr.writerow(header)
        log_file.close()
        
#%% writing log
    def writeLog(self, data, filename="data.csv", writeFiat=False, currency="USD", time='rfc1123'):
        assets = self.k.query_public('Assets')
        if(os.path.exists(os.path.join(os.getcwd(),filename)) == False):
            self.createLogFile(filename, assets, writeFiat)
            var = 0 #Var (%) is set to 0 when creating file
            
        else: # If file already exists :
            with open(filename,'r') as f:
                for row in reversed(list(csv.reader(f))):
                    lastLine = row
                    break

                if currency not in self.total: self.updateFiatInTotal(currency)
                #If user wants a fiat conversion not in his kraken wallet

                if(lastLine[-1] == currency):
                    lastTotal = float(lastLine[-3])
                    var = float((self.total[currency] - lastTotal) / lastTotal)*100
                else:
                    var = 0
                
                #We prepare the Var(%) by checking last Total value and currency
            print ("Accumulating data...")
            
        if(writeFiat==False):
            for fiat in list(assets['result']):
                if(fiat.startswith("Z")):
                    assets['result'].pop(fiat)
        #We remove the fiat currencies in header dynamically if the user still wants to not write it
        #If one day or suddenly the user decides to add Fiat writing in data logs, it will try to adapt
        
        log_file = open(filename, "a", newline='')
        wr = csv.writer(log_file)
    
        row = []
        tmp = self.k.query_public('Time')
        row.append(tmp['result'][time])
        tmp = list(data.items())
        
        for asset in list(assets['result']):
            if(str(assets['result'][asset]['altname'] + "XBT") in self.values.keys()):
                assertValue = self.values[str(assets['result'][asset]['altname']) + "XBT"] * float(self.fiatbtc_pair[currency])
                row.append("{0:.5f}".format(assertValue))
            else:
                row.append("0")

        row.append("{0:.2f}".format(self.total[currency]))  
        row.append("{0:.2f}".format(var))
        row.append(currency)
    
        wr.writerow(row)
        log_file.close()
