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
 
v0.1.3
Writelog feature added.

1. Displays the different amount of crypto currencies you own on your Kraken wallet.
2. Displays the total crypto money you own in equivalent fiat money.
3. Adapted to the crypto and fiat currencies you already own.
4. If you don't own any fiat money on your Kraken wallet, it will be displayed the equivalent in USD.
(The fiat money can be easily modified but be aware that some markets doesn't allow it,
DASHUSD -> DASHJPY for example, can't be done because the market doesn't exist on Kraken.
Check k.query_public('Ticker',{'pair': 'YOURMARKET',}) inline to know if it exist.
5. Works with multi-fiat currencies wallets.
6. Write and log data into "data.csv" located in the same folder directory

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

currencies = [] #List of differents currencies owned by user
market = []     #List of markets concerned by currencies in user's wallet
balance = []    #List of the differents amount of crypto currencies owned by user



    #%% Log file writer
def createLogFile(filename, assets, writeFiat):
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

def writeLog(data, filename="data.csv", writeFiat=False, currency="USD"):
    assets = k.query_public('Assets')
    if(os.path.exists(os.path.join(os.getcwd(),filename)) == False):
        CreateLogFile(filename, assets, writeFiat)
        var = 0 #Var (%) is set to 0 when creating file
        
    else: # If file already exists :
        with open(filename,'r') as f:
            for row in reversed(list(csv.reader(f))):
                lastLine = row
                break

            if(lastLine[-1] == currency):
                lastTotal = float(lastLine[-3])
                var = float((total[currency] - lastTotal) / lastTotal)*100
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
    tmp = k.query_public('Time')
    row.append(tmp['result']['unixtime'])
    tmp = list(data.items())
    #row = csv.DictWriter(log_file, delimiter=',', lineterminator='\n', fieldnames=tmp)
    
    for asset in list(assets['result']):
        if(str(assets['result'][asset]['altname'] + currency) in values.keys()):
            assertValue = values[str(assets['result'][asset]['altname']) + currency]
            row.append("{0:.5f}".format(assertValue))
        else:
            row.append("0")
        
    row.append("{0:.2f}".format(total[currency]))    
    row.append("{0:.2f}".format(var))
    row.append(currency)

    wr.writerow(row)
    log_file.close()

#%%Extracting data from Kraken Exchange API

k = krakenex.API()
k.load_key('kraken.key')    
data = k.query_private('Balance')
#print(data)
#TODO if error
if data['error'] : 
    print("Error : ",data['error'])
    sys.exit("Can't continue with error")


#DEBUG
#data = data.replace("XXRP","ZJPY")
#data['result']["ZUSD"] = data['result']["XZEC"]
#del data['result']["XZEC"]
#Can be used to test if others currencies (e.g ZPJY) are compatibles with others market pairs you are into. 

#%%We find currencies concerned by the user wallet

#Exctracts crypto currencies
crypto_index = [c for c in data['result'] if(not c.startswith("Z"))]
#We get every symbols except the ones which starts with "Z" (these are fiat currencies)
#print (crypto_index)
if crypto_index == [] : sys.exit("Can't find any crypto currency on your wallet yet.")
for i in crypto_index:
    currencies.append(i)

#Extracts fiat currencies
fiat_index = [c for c in data['result'] if (c.startswith("Z"))]
#print (fiat_index)
if fiat_index == [] :
    print("Currencies will be converted in USD by default")
    fiat_index.append(0)
    currencies.append('ZUSD')
else:
    currencies = currencies + fiat_index

print("Currencies on your wallet : ",currencies)

#%%Here we get our current currency situation
#raw currency values to be extracted
for i in crypto_index:
    balance.append(data['result'][i])

for i in fiat_index:
    balance.append(data['result'][i])
#We extract what we need

#%% Converting balance to float (needed for operations)
balance = [float(i) for i in balance]
print("Current balance you own : ",balance)
#Casting current balance to float

#%%We prepare our list of markets exchange we are interested in
print (crypto_index, fiat_index)
crypto_index = [i[1:] if(i.startswith("X")) else i for i in crypto_index]
fiat_index = [i[1:] if(i.startswith("Z")) else i for i in fiat_index]
        #We remove the first char in purpose to get the correct acrynom for market ask \
        #(e.g : XXBT -> XBT, ZEUR -> EUR)

for i in crypto_index:
    for j in fiat_index:
        market.append(i+j)
        
print("Markets we aim to analyze to : ",market) #This is optionnal
#Add more currencies if needed but it's done automatically
#%% Extracts price of every currencies user is involved onto
# Also removing markets which doesn't exist on Kraken
price = []
i=0
while i < len(market):  #We use a while loop because the for loop doesn't allow us to modifiy i index during iteration
    data_price = k.query_public('Ticker',{'pair': market[i],})
    print(market[i])
#Error ?
    if data_price['error'] :
        
        print(data_price['error'][0])
        if data_price['error'][0] == "EQuery:Invalid asset pair" or "EQuery:Unknown asset pair":
                print("Check market list, ",market[i]," pair doesn't exist on kraken exchange. Erasing from market list.")
                market.remove(market[i])
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
        print("Price of ",market[i]," added")
        price[i] = float(price[i])
        #(Thanks to plguhur)
        
        i+=1
        #price is a list of str -> cast to float
#%% Finally multiplying balance of crypto of user wallet BY actual real-time price of market
# price of coin in FIAT * amount of coin = Estimated value of currencies in FIAT MONEY
values = {}
total = {}

totals = []
for i in fiat_index:
    total.update({i : ''})
    totals.append(0)
#Initializing in case we never get the market data    
    

#Converting data from each fiat to their corresponding market (ZEUR with XBTEUR, ETHEUR,... \
# same for ZUSD and XBTUSD, ETHUSD, etc...) via string recognition
for i in range(len(market)):
    if(market[i][0:3] in currencies):
        crypto_tmp = market[i][0:3]
    elif(market[i][0:4] in currencies):
        crypto_tmp = market[i][0:4]
        
    elif('X'+market[i][0:3] in currencies):
        crypto_tmp = 'X'+market[i][0:3]

    
    values.update({market[i] : balance[currencies.index(crypto_tmp)] * price[i]})
    #We find the index of the crypto in crypto_tmp and extract its balance
    print(market[i], balance[currencies.index(crypto_tmp)], price[i])

    if(market[i][0]=='D'): fiat_tmp = market[i][4:7]    
    else: fiat_tmp = market[i][3:6]

    totals[list(total.keys()).index(fiat_tmp)] += values[market[i]]
    
for n in range(len(fiat_index)):
    values.update({currencies[len(crypto_index)+n] : balance[len(crypto_index)+n]})
#For each market, we calculate the price for each fiat money involved in
#One exception : when i-n < 0, we need to fix balance index because 
#len(price) and len(market) is not equal to len(balance)        
    
    totals[n] += balance[len(crypto_index)+n]
# Don't forget to add what is remaining in fiat in your wallet
        
#%% Displaying
for i in range(len(fiat_index)):
    total.update({list(total.keys())[i] : totals[i]})      
        

values.update({'Total' : total})
print(values)

writeLog(values, currency="EUR")
