

from LiquidityProvider import LiquidityProvider
from TradingStrategyDualMA import TradingStrategyDualMA 
from MarketSimulator import MarketSimulator
from OrderManager import OrderManager
from OrderBook import OrderBook

from collections import deque
import pandas as pd
import numpy as np
from pandas_datareader import data
import matplotlib.pyplot as plt
import h5py

def call_if_not_empty(deq, fun): 
  while (len(deq) > 0):
    fun()
    
