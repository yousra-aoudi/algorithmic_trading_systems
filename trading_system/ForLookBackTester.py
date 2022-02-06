# ForLookBackTester class will handle, line by line, all the prices of the data frame. 
# We will need to have two lists capturing the prices to calculate the two moving averages. 
# We will store the history of profit and loss, cash, and holdings to draw a chart to see how much money we will make.


import pandas as pd
import numpy as np
from pandas_datareader import data import matplotlib.pyplot as plt import h5py
from collections import deque

goog_data=load_financial_data(start_date='2001-01-01', end_date = '2022-01-01',output_file='goog_data.pkl')

# Python program to get average of a list 
def average(lst):
  return sum(lst) / len(lst)


class ForLoopBackTester: 
  def __init__(self):
    self.small_window=deque()
    self.large_window=deque()
    self.list_position=[]
    self.list_cash=[]
    self.list_holdings = []
    self.list_total=[]
    
    self.long_signal=False 
    self.position=0 
    self.cash=10000 
    self.total=0 
    self.holdings=0
		
	# The function below updates the real-time metrics the trading strategy needs in order to make a decision

  def create_metrics_out_of_prices(self,price_update): 
		self.small_window.append(price_update['price']) 
		self.large_window.append(price_update['price']) 
	
		if len(self.small_window)>50:
			self.small_window.popleft() 
		if len(self.large_window)>100:
			self.large_window.popleft() 
		if len(self.small_window) == 50:
			if average(self.small_window) > average(self.large_window): 
				self.long_signal=True
			else:
				self.long_signal = False
				return True
  	return False

	def buy_sell_or_hold_something(self,price_update): 
		if self.long_signal and self.position<=0:
			print(str(price_update['date']) + " send buy order for 10 shares price=" + str(price_update['price']))
			self.position += 10
			self.cash -= 10 * price_update['price'] 
		elif self.position>0 and not self.long_signal:
			print(str(price_update['date'])+ " send sell order for 10 shares price=" + str(price_update['price']))
			self.position -= 10
			self.cash -= -10 * price_update['price']
			
			self.holdings = self.position * price_update['price'] 
			self.total = (self.holdings + self.cash)
			print('%s total=%d, holding=%d, cash=%d' % (str(price_update['date']),self.total, self.holdings, self.cash))
			
			self.list_position.append(self.position)
			self.list_cash.append(self.cash)
			self.list_holdings.append(self.holdings)
			self.list_total.append(self.holdings+self.cash)
			
			naive_backtester=ForLoopBackTester()
			for line in zip(goog_data.index,goog_data['Adj Close']):
				date=line[0]
				price=line[1] 
				price_information={'date' : date,'price' : float(price)}
				is_tradable = naive_backtester.create_metrics_out_of_prices(price_information) 
				if is_tradable:
					naive_backtester.buy_sell_or_hold_something(price_information)
   
   

