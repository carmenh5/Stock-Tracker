# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 17:35:52 2020

@author: Carmen H
"""
# import the following modules
import pandas as pd
import os
import time
import shutil
import mplfinance as mpl

# the following modules need to be downloaded before program will run (selenium)
from selenium import webdriver

#%% Class to hold data for each stock
class retracementLevels:
    # self init to define class
    def __init__(self, stock):
        # set the name of the class to the company to avoid confusion
        self.name = stock
        self.max = 0
        self.min = 0
        self.level23_6 = 0
        self.level38_2 = 0
        self.level50 = 0
        self.level61_8 = 0
        self.trend = "unknown"
        
    def setLevel(self, identifier, value):
        if (identifier == "max"):
            self.max = value
        elif (identifier == "min"):
            self.min = value
        elif (identifier == "level23_6"):
            self.level23_6 = value
        elif (identifier == "level38_2"):
            self.level38_2 = value
        elif (identifier == "level50"):
            self.level50 = value
        elif (identifier == "level61_8"):
            self.level61_8 = value
    
    def setTrend(self, trendGiven):
        self.trend = trendGiven
    

#%% find the list of stocks the user has bought
# store the stocks in an array
stocksBought = []
userInput = "notDone"

while userInput != "done":
    userInput = input("Enter ticker of stock bought or 'done' to exit: ")
    
    if userInput != "done":
        stocksBought.append(userInput)

#%% Set download paths
# find file in downloads
# should be most recent file downloaded
# change destination to which ever destination folder we want
destination = "C:/Users/w_hsi/Desktop/Uni/GitProjects/"

# change (C:/Users/w_hsi/Downloads/) to your own path
download_path = 'C:/Users/w_hsi/Downloads/'

#%% download the historical data from the stocks the user wants
index = 0
driver = webdriver.Chrome()

while len(stocksBought) > index:
    searchStock = stocksBought[index]
    searchURL = "https://ca.finance.yahoo.com/quote/" + searchStock + "/history?p=" + searchStock
    index = index + 1
    
    # remove if already have file in downloads file and destination
    if os.path.exists(download_path + searchStock + ".csv"):
        os.remove(download_path + searchStock + ".csv")
    if os.path.exists(destination + searchStock + ".csv"):
        os.remove(destination + searchStock + ".csv")
    
    driver.get(searchURL)
    driver.maximize_window()
    
    driver.implicitly_wait(5)
    download = driver.find_element_by_xpath('//*[text()="Download"]')
    download.click()
    
    time.sleep(5)
    
    if os.path.exists(download_path + searchStock + ".csv"):
        shutil.move(download_path + searchStock + ".csv", destination)

# get market trend using the s&p500
if len(stocksBought) > 0:
    searchStock = "^GSPC"
    searchURL = "https://ca.finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC"
    
    if os.path.exists(download_path + searchStock + ".csv"):
        os.remove(download_path + searchStock + ".csv")
    if os.path.exists(destination + searchStock + ".csv"):
        os.remove(destination + searchStock + ".csv")
    
    driver.get(searchURL)
    driver.maximize_window()
    
    driver.implicitly_wait(5)
    download = driver.find_element_by_xpath('//*[text()="Download"]')
    download.click()
    
    time.sleep(5)
    
    if os.path.exists(download_path + searchStock + ".csv"):
        shutil.move(download_path + searchStock + ".csv", destination)
    
# close the browser window
driver.quit()

#%% open and load the csv files
# dictionary of dataframes
stockData = {}
stocksBought.append("^GSPC")
for stock in stocksBought:
    fileName = stock + ".csv"
    #tempData = pd.read_csv(fileName)
    tempData = pd.read_csv(fileName, index_col= 0, parse_dates =True)
    stockData[stock] = tempData

#%% make the classes
# store information in levelData dictionary
levelData = {}

for key in stockData:
    levelData[key] = retracementLevels(key)
    maximum = (stockData[key])['High'].max()
    minimum = (stockData[key])['Low'].min()
    maximumDate = (stockData[key])['High'].idxmax()
    minimumDate = (stockData[key])['Low'].idxmin()
    distance = maximum - minimum
    levelData[key].setLevel("max", maximum)
    levelData[key].setLevel("min", minimum)
    
    # find market trend
    # if minimum date is before maximum date (index is less) then should be uptrend
    if (maximumDate > minimumDate):
        levelData[key].setTrend("uptrend")
    elif(maximumDate < minimumDate):
        levelData[key].setTrend("downtrend")
    
    # calculate retracement levels
    if (levelData[key].trend == "downtrend"):
        levelData[key].setLevel("level23_6", minimum + (distance*0.236))
        levelData[key].setLevel("level38_2", minimum + (distance*0.382))
        levelData[key].setLevel("level50", minimum + (distance*0.5))
        levelData[key].setLevel("level61_8", minimum + (distance*0.618))
    elif (levelData[key].trend == "uptrend"):
        levelData[key].setLevel("level23_6", maximum - (distance*0.236))
        levelData[key].setLevel("level38_2", maximum - (distance*0.382))
        levelData[key].setLevel("level50", maximum - (distance*0.5))
        levelData[key].setLevel("level61_8", maximum - (distance*0.618))
    elif (levelData[key].trend == "unknown"):
        # check value relative to last value
        if (stockData[key]).iloc[0]['Adj Close'] > (stockData[key]).iloc[1]['Adj Close']:
            levelData[key].setLevel("level23_6", minimum + (distance*0.236))
            levelData[key].setLevel("level38_2", minimum + (distance*0.382))
            levelData[key].setLevel("level50", minimum + (distance*0.5))
            levelData[key].setLevel("level61_8", minimum + (distance*0.618))
        elif (stockData[key]).iloc[0]['Adj Close'] < (stockData[key]).iloc[1]['Adj Close']:
            levelData[key].setLevel("level23_6", maximum - (distance*0.236))
            levelData[key].setLevel("level38_2", maximum - (distance*0.382))
            levelData[key].setLevel("level50", maximum - (distance*0.5))
            levelData[key].setLevel("level61_8", maximum - (distance*0.618))

#%% plot and save graphs
for key in levelData:
    
    if (key == "^GSPC"):
        fileName = "SP500"
    else:
        fileName = key
    
    figTitle = fileName + " Stock Price with 20, 50, and 100 Day Moving Averages and Retracement Levels at " + str(round(levelData[key].level23_6,2)) + ", " + str(round(levelData[key].level38_2,2)) + ", " + str(round(levelData[key].level50,2)) + ", and " + str(round(levelData[key].level61_8,2))
    hlinelevels = [levelData[key].min, levelData[key].max, levelData[key].level23_6, levelData[key].level38_2, levelData[key].level50, levelData[key].level61_8]
    
    mpl.plot(stockData[key], type='candle', ylabel='Price in USD', title=figTitle, hlines=hlinelevels, mav=(20,50,100), figscale=2.0, savefig=fileName+'.png')
