# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 19:21:28 2017

@author: smechaab

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
 
"""
# Includes
import krakenex
import csv
import sys
import os

# Class init


class CurrencyViewer:
    DELTA = 0.0000001

    def __init__(self):
        self.k = krakenex.API()
        self.k.load_key('kraken.key')
        self.currencies = {'fiat': [], 'crypto': []} #List of differents currencies owned by user
        self.market = []     #List of markets concerned by currencies in user's wallet
        self.balance = {'fiat': [], 'crypto': []}

        self.values = {} #Context variables
        self.total = {}
        self.fiatbtc_pair = {}

        self.btc_total = 0
        self.totals = []
        self.default_currency = "USD"

        self.debugmode = False #Change to switch to debugmode 
        
# Main purpose of this script
# It calls every function in order, it allows to get the full data for user
    def processCViewer(self, log=True, currency="USD", time="rfc1123"):
        self.default_currency = "USD"
        balance_result = self.request_balance()
        self.extract_balances(balance_result)
        price = self.get_crypto_price_in_btc(self.currencies['crypto'])
        self.process_conversion(price, self.currencies['crypto'], self.currencies['fiat'])
        self.displayResults()
        if log:
            self.writeLog(self.values, currency = currency, time = time)
        
# Exit error handling functions
    def _exit_error(self):
        sys.exit("Can't continue with error")

    def _public_query_error(self, response_with_error):
        print(response_with_error['error'][0])

        if response_with_error['error'][0] == "EQuery:Invalid asset pair" or "EQuery:Unknown asset pair":
            print("Check market list, this pair doesn't exist on Kraken exchange."
                  " This market won't be added in market data.")
        else:
            # We leave the program if this is not an Invalid asset pair error
            self._exit_error()

    def _empty_wallet_error(self):
        sys.exit("Your wallet seem empty, please check your API keys or your Kraken dashboard.")

#%% Collecting data
    def request_balance(self):
        raw_balance_result = self.k.query_private('Balance')

        if raw_balance_result['error'] :
                print("Error : ", raw_balance_result['error'])
                self._exit_error()
                
        #We find currencies concerned by the user wallet
        if self.debugmode:
            #DEBUG, examples
            raw_balance_result['result']["ZUSD"] = raw_balance_result['result']["XZEC"]
            del raw_balance_result['result']["XZEC"]
            #Can be used to test if others currencies (e.g ZPJY) are compatibles with others market pairs you are into.
        
        return raw_balance_result['result']

    def extract_fiat_balance(self, balance_result):
        #Extract fiat currencies
        print("Balance result: ", balance_result)
        fiat_index = [c for c in balance_result if (c.startswith("Z"))]
        if self.default_currency not in fiat_index:
            print("Currencies will be converted in report currency by default")
            self.currencies['fiat'].append("Z" + self.default_currency)
            self.balance['fiat'].append(0.0)
        else:
            for i in fiat_index:                
                self.currencies['fiat'].append(i)
                self.balance['fiat'].append(float(balance_result[i]))

    def correct_fiat_ticker_syntax(self):
        self.currencies['fiat'] = [i[1:] if (i.startswith("Z")) else i for i in self.currencies['fiat']]
        # We remove the first char in purpose to get the correct acronym for market ask (e.g : XXBT -> XBT, ZEUR -> EUR)

    def extract_crypto_balance(self, balance_result):
        crypto_owned = [c for c in balance_result if(not c.startswith("Z"))]
        # We get every symbols except the ones which starts with "Z" (these are fiat currencies)
        # print (crypto_owned)
        if crypto_owned == [] : self._empty_wallet_error()

        # crypto_owned = [i[1:] if (i.startswith("X")) else i for i in crypto_owned]

        for i in crypto_owned:

            self.currencies['crypto'].append(i)
            self.balance['crypto'].append(float(balance_result[i]))           

    def correct_crypto_ticker_syntax(self):
        self.currencies['crypto'] = [i[1:] if (i.startswith("X")) else i for i in self.currencies['crypto']]
        # We remove the first char in purpose to get the correct acrynom for market ask \
        # (e.g : XXBT -> XBT, ZEUR -> EUR)

    def extract_balances(self, balance_result):
        
        self.extract_fiat_balance(balance_result)
        self.correct_fiat_ticker_syntax()

        self.extract_crypto_balance(balance_result)
        self.correct_crypto_ticker_syntax()

        print("Currencies on your wallet : ", self.currencies)
        print("Current balance you own : ", self.balance)

# Getter functions
    def get_fiat_price_in_btc(self, fiat):
        data_price = self.k.query_public('Ticker',{'pair': "XBT"+fiat,})
        print("XBT"+fiat)

        if data_price['error'] :
            self._public_query_error(data_price)
        else:
            index=list(data_price['result'].keys())[0]
        return data_price['result'][index]['c'][0]

    def update_pair_market_list(self, crypto_owned):
        # We prepare our list of markets exchange we are interested in
        if type(crypto_owned) == list:
            for i in crypto_owned:
                if i != "XBT":
                    self.market.append(i + "XBT")
        else:
            if crypto_owned != "XBT":
                self.market.append(crypto_owned + 'XBT')

    def extract_market_data(self, market):
        data = self.k.query_public('Ticker', {'pair': market, })
        print("Extracting ", market, "data")

        if data['error']:
            print(data['error'][0])
            self._public_query_error(data)
            return False
        return data

    def update_market_price(self, market, price):
        index = list(market['result'].keys())[0]
        p = market['result'][index]['c'][0]
        price.append(p)
        print("Price of ", market, " added")

    def get_crypto_price_in_btc(self, crypto_owned):
        price = []
        market_index = 0

        self.update_pair_market_list(crypto_owned)
        print("Markets concerned : ",self.market)

        while market_index < len(self.market):
            # We use a while loop because the for loop doesn't allow us to modify market_index during iteration
            market_data = self.extract_market_data(self.market[market_index])
            if market_data:
                self.update_market_price(market_data, price)
                price[market_index] = float(price[market_index])

            market_index += 1
        return price

# Process functions
    def update_fiat_amount_in_total(self, fiat):
        xbt_fiat = self.get_fiat_price_in_btc(fiat)
        self.fiatbtc_pair.update({fiat: xbt_fiat})
        self.total[fiat] = self.btc_total * float(xbt_fiat)

    def process_conversion(self, price, crypto_owned, fiat_index):
        #Finally multiplying balance of crypto of user wallet BY actual real-time price of market
        # price of coin in FIAT * amount of coin = Estimated value of currencies in FIAT MONEY

        # crypto_owned = [i[1:] if(i.startswith("X")) else i for i in crypto_owned]
        # fiat_index = [i[1:] if(i.startswith("Z")) else i for i in fiat_index]

        for i in fiat_index:
            self.total.update({i : ''})
            self.totals.append(0)
        #Initializing in case we never get the market data    
            
        """
        #Converting data from each fiat to their corresponding market in XBT (XRP with XRPXBT, ETHXBT,... \
        # via string recognition
        """
        for i in range(len(self.market)):
            if(self.market[i][0:3] in self.currencies['crypto']):
                crypto_tmp = self.market[i][0:3]
            elif(self.market[i][0:4] in self.currencies['crypto']):
                crypto_tmp = self.market[i][0:4]
                
            elif('X'+self.market[i][0:3] in self.currencies['crypto']):
                crypto_tmp = 'X'+self.market[i][0:3]
        
            self.values.update({self.market[i] : self.balance['crypto'][self.currencies['crypto'].index(crypto_tmp)] * price[i]})
            print(self.market[i], self.balance['crypto'][self.currencies['crypto'].index(crypto_tmp)], price[i])
            
            # Unused fiat_tmp ? What's the point here ?
            if(self.market[i][0]=='D'): fiat_tmp = self.market[i][4:7]    
            else: fiat_tmp = self.market[i][3:6]
            
            self.btc_total += self.values[self.market[i]]
            print("btc_total =",self.btc_total)
            
        for i in fiat_index:
            self.update_fiat_amount_in_total(i)
            
        for n in range(len(fiat_index)):
            self.values.update({self.currencies['fiat'][n] : self.balance['fiat'][n]})
        
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

                if currency not in self.total: self.update_fiat_amount_in_total(currency)
                #If user wants a fiat conversion not in his kraken wallet

                var = 0
                lastTotal = float(lastLine[-3])
                if lastLine[-1] == currency and lastTotal > self.DELTA:
                    var = float((self.total[currency] - lastTotal) / lastTotal)*100
                
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
