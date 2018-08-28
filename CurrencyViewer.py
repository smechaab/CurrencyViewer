# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 19:21:28 2017

@author: smechaab

 Prints the account balance and will in future send it via email,
 with obvisouly your own email adress (SOON).
 
 Please fill and copy your kraken.key file in the same directory.
 
 If you have any questions or suggestions, please email me at 
 s.mechaab@gmail.com.
 
 And please, don't hesitate to feedback !
 
v0.1.2
Fixing bugs and cleaning code

1. Displays the different amount of crypto currencies you own on your Kraken wallet.
2. Displays the total crypto money you own in equivalent fiat money.
3. Adapted to the crypto and fiat currencies you already own.
4. If you don't own any fiat money on your Kraken wallet, it will be displayed the equivalent in USD.
(The fiat money can be easily modified but be aware that some markets doesn't allow it,
DASHUSD -> DASHJPY for example, can't be done because the market doesn't exist on Kraken.
Check k.query_public('Ticker',{'pair': 'YOURMARKET',}) inline to know if it exist.
5. Works with multi-fiat currencies wallets.

NOTE: Fiat currencies like JPY doesn't have as many markets as USD on Krakenex.
Crypto currencies that doesn't cover these markets, with JPY for example, aren't converted yet
Only markets with JPY are counted in the total sum values
This issue will be fixed with the next commit

NOTE2: Please be aware that only the markets with direct fiat conversion are covered yet

 
"""
#%% Includes
import krakenex
import csv
#import re
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
    
        #Header generation for data logfile
#        self.header = []
#        self.header.append("Date")
#        assets = self.k.query_public('Assets')
#        #Generating the first row (columns titles)
#        self.header = self.header + list(assets['result'].keys())
#        self.header.append("Total")
#        self.header.append("Var(%)")
        
        self.debugmode = False #Change to switch to debugmode 
        
#%% Main purpose of this script
# It calls every function in order, it allows to get the full data for user
    def processCViewer(self,log=True):
        
        data, c, f = self.collectData()
        price = self.getMarketPrice(data,c)
        self.processingConversion(price,c,f)
#a        self.displayResults(f)
        if(log==True):
            self.writeLog(self.values, currency = "EUR")
        
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
        #print (fiat_index)
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
        #We prepare our list of markets exchange we are interested in
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
            #print(data_price)
            #We extract 
            index=list(data_price['result'].keys())[0]
        return data_price['result'][index]['c'][0]

#%%
    def getMarketPrice(self, data, crypto_index):
        #We prepare our list of markets exchange we are interested in
        
        for i in crypto_index:
            if(i != "XBT"):
                self.market.append(i+"XBT")
                
        print("Markets concerned : ",self.market) #This is optionnal
        #Add more currencies if needed but it's done automatically
        
        #Extracts price of every currencies user is involved onto
        # Also removing markets which doesn't exist on Kraken
        
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
                        
                        #We don't want to increment when we have a false pair
                        #In a next version, we gonna jump to token/BTC then BTC/fiat \
                        #(e.g : EOS/BTC then BTC/USD to get an estimation of the token's value)
                else:
                    # We leave the program if this is not an Invalid asset pair error
                    sys.exit("Can't continue with error")
            else:
                #print(data_price)
                #We extract 
                index=list(data_price['result'].keys())[0]
                p = data_price['result'][index]['c'][0]
                price.append(p)
                print("Price of ",self.market[i]," added")
                price[i] = float(price[i])
                #(Thanks to plguhur)
                
                i+=1
                #price is a list of str -> cast to float
        return price
                

#%%
    def processingConversion(self, price, crypto_index, fiat_index):
        #Finally multiplying balance of crypto of user wallet BY actual real-time price of market
        # price of coin in FIAT * amount of coin = Estimated value of currencies in FIAT MONEY
        self.values = {}
        self.total = {}
        self.fiatbtc_pair = {}
        
        btc_total = 0
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
            #We find the index of the crypto in crypto_tmp and extract its balance
            print(self.market[i], self.balance[self.currencies.index(crypto_tmp)], price[i])
            
            if(self.market[i][0]=='D'): fiat_tmp = self.market[i][4:7]    
            else: fiat_tmp = self.market[i][3:6]
            
            btc_total += self.values[self.market[i]]
            print("btc_total =",btc_total)
            
        for i in fiat_index:
            xbtfiat = self.getXBTtoFiatPrice(i)
            self.fiatbtc_pair.update({i : xbtfiat})
            self.total[i] = btc_total * float(xbtfiat)

            
        for n in range(len(fiat_index)):
            self.values.update({self.currencies[len(crypto_index)+n] : self.balance[len(crypto_index)+n]})
        #For each market, we calculate the price for each fiat money involved in
        #One exception : when i-n < 0, we need to fix balance index because 
        #len(price) and len(market) is not equal to len(balance)        
            
            #self.totals[n] += self.balance[len(crypto_index)+n]
            
#        for f_curr in fiat_index:
#            data_price = self.k.query_public('Ticker',{'pair': "XBT"+f_curr,})
#            self.totals.append(data_price)#debug
        
#%% Displaying
    def displayResults(self, fiat_index):
        for i in range(len(fiat_index)):
            self.total.update({list(self.total.keys())[i] : self.totals[i]})      
        self.values.update({'Total' : self.total})
        print(self.values)

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
    def writeLog(self, data, filename="data.csv", writeFiat=False, currency="USD"):
        assets = self.k.query_public('Assets')
        if(os.path.exists(os.path.join(os.getcwd(),filename)) == False):
            self.createLogFile(filename, assets, writeFiat)
            var = 0 #Var (%) is set to 0 when creating file
            
        else: # If file already exists :
            with open(filename,'r') as f:
                for row in reversed(list(csv.reader(f))):
                    lastLine = row
                    break
    
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
        row.append(tmp['result']['unixtime'])
        tmp = list(data.items())
        #row = csv.DictWriter(log_file, delimiter=',', lineterminator='\n', fieldnames=tmp)
        
        for asset in list(assets['result']):
            print(str(str(assets['result'][asset]['altname']))) #debug
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
        
    
    
#    def writeLog(self, data, filename="data.csv", writeFiat=False, currency="USD"):
#        assets = self.k.query_public('Assets')
#        if(os.path.exists(os.path.join(os.getcwd(),filename)) == False):
#            self.createLogFile(filename, assets, writeFiat)
#            var = 0 #Var (%) is set to 0 when creating file
#            
#        else: # If file already exists :
#            with open(filename,'r') as f:
#                for row in reversed(list(csv.reader(f))):
#                    lastLine = row
#                    break
#    
#                if(lastLine[-1] == currency and float(lastLine[-3]) != 0):
#                    lastTotal = float(lastLine[-3])
#                    var = float((abs(self.total[currency] - lastTotal)) / lastTotal)*100
#                else:
#                    var = 0
#                
#                #We prepare the Var(%) by checking last Total value and currency
#            print ("Accumulating data...")
#            
#        if(writeFiat==False):
#            for fiat in list(assets['result']):
#                if(fiat.startswith("Z")):
#                    assets['result'].pop(fiat)
#        #We remove the fiat currencies in header dynamically if the user still wants to not write it
#        #If one day or suddenly the user decides to add Fiat writing in data logs, it will try to adapt
#        
#        log_file = open(filename, "a", newline='')
#        wr = csv.writer(log_file)
#    
#        row = []
#        tmp = self.k.query_public('Time')
#        row.append(tmp['result']['unixtime'])
#        tmp = list(data.items())
#        #row = csv.DictWriter(log_file, delimiter=',', lineterminator='\n', fieldnames=tmp)
#        
#        for asset in list(assets['result']):
#            if(str(assets['result'][asset]['altname'] + currency) in self.values.keys()):
#                assertValue = self.values[str(assets['result'][asset]['altname']) + currency]
#                row.append("{0:.5f}".format(assertValue))
#            else:
#                row.append("0")
#            
#        row.append("{0:.2f}".format(self.total[currency]))    
#        row.append("+{0:.2f}".format(var))
#        row.append(currency)
#    
#        wr.writerow(row)
#        log_file.close()
    
#    def writelog(self,data):
#        if(os.path.exists(os.path.join(os.getcwd(),"data.csv")) == False):
#            log_file = open("data.csv", 'w') 
#            wr = csv.writer(log_file)
#            print ("Creating a log file \"data.csv\"")
#    #        header = []
#    #        #Generating the first row (columns titles)
#    #        header.append("Date")
#    #        assets = k.query_public('Assets')
#    #        header = header + list(assets['result'].keys())
#    #        header.append("Total")
#    #        header.append("Var(%)")
#            wr.writerow(self.header)
#        else:
#            log_file = open("data.csv")
#            rd = csv.reader(log_file)
#            self.header = rd[0]
#            wr = csv.writer(log_file)
#            print ("Accumulating data...")
#            
#        row = []
#        tmp = self.k.query_public('Time')
#        row.append(tmp['result']['unixtime'])
#        tmp = list(data.items())
#        #row = csv.DictWriter(log_file, delimiter=',', lineterminator='\n', fieldnames=tmp)
#        row.append()
#        wr.writerow(row)
#        log_file.close()
#
