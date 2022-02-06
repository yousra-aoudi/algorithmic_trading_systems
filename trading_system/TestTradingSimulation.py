# The goal of the TestTradingSimulation class is to create the full trading system 
# by gathering all the prior critical components together.

# This class checks whether, for a given input, we have the expected output. 
# Additionally, we will test whether the PnL of the trading strategy has been updated accordingly.

# We will first need to create all the deques representing the communication channels within the trading systems:
import unittest

import LiquidityProvider 
import TradingStrategy 
import MarketSimulator 
import OrderManager
import OrderBook

from collections import deque

class TestTradingSimulation(unittest.TestCase): 
  
  def setUp(self):
    self.lp_2_gateway=deque()
    self.ob_2_ts = deque()
    self.ts_2_om = deque()
    self.ms_2_om = deque()
    self.om_2_ts = deque()
    self.gw_2_om = deque()
    self.om_2_gw = deque()
    
    # We instantiate all the critical components of the trading system:
    self.lp=LiquidityProvider(self.lp_2_gateway)
    self.ob=OrderBook(self.lp_2_gateway, self.ob_2_ts)
    self.ts=TradingStrategy(self.ob_2_ts,self.ts_2_om,self.om_2_ts)
    self.ms=MarketSimulator(self.om_2_gw,self.gw_2_om)
    self.om=OrderManager(self.ts_2_om, self.om_2_ts,self.om_2_gw,self.gw_2_om)
   
	
	# We test whether by adding two liquidities having a bid higher than the offer, 
	# we will create two orders to arbitrage these two liquidities. 
	# We will check whether the components function correctly by checking what they push to their respective channels. 
	# Finally, since we will buy 10 liquidities at a price of 218 and we sell at a price of 219, the PnL should be 10:
    
  def test_add_liquidity(self):
		# Order sent from the exchange to the trading system 
		order1 = {'id': 1, 
							'price': 219, 
							'quantity': 10, 
							'side': 'bid', 
							'action': 'new'
						 }
		self.lp.insert_manual_order(order1)
   	self.assertEqual(len(self.lp_2_gateway),1)
   	self.ob.handle_order_from_gateway()
   	self.assertEqual(len(self.ob_2_ts), 1)
   	self.ts.handle_input_from_bb()
   	self.assertEqual(len(self.ts_2_om), 0)
   	order2 = {'id': 2, 
							'price': 218, 
							'quantity': 10, 
							'side': 'ask', 
							'action': 'new'
						 }
   	self.lp.insert_manual_order(order2.copy())
   	self.assertEqual(len(self.lp_2_gateway),1)
   	self.ob.handle_order_from_gateway()
   	self.assertEqual(len(self.ob_2_ts), 1)
   	self.ts.handle_input_from_bb()
   	self.assertEqual(len(self.ts_2_om), 2)
   	self.om.handle_input_from_ts()
   	self.assertEqual(len(self.ts_2_om), 1)
   	self.assertEqual(len(self.om_2_gw), 1)
   	self.om.handle_input_from_ts()
   	self.assertEqual(len(self.ts_2_om), 0)
   	self.assertEqual(len(self.om_2_gw), 2)
   	self.ms.handle_order_from_gw()
   	self.assertEqual(len(self.gw_2_om), 1)
   	self.ms.handle_order_from_gw()
   	self.assertEqual(len(self.gw_2_om), 2)
   	self.om.handle_input_from_market()
   	self.om.handle_input_from_market()
   	self.assertEqual(len(self.om_2_ts), 2)
   	self.ts.handle_response_from_om()
   	self.assertEqual(self.ts.get_pnl(),0)
   	self.ms.fill_all_orders()
   	self.assertEqual(len(self.gw_2_om), 2)
   	self.om.handle_input_from_market()
   	self.om.handle_input_from_market()
   	self.assertEqual(len(self.om_2_ts), 3)
   	self.ts.handle_response_from_om()
   	self.assertEqual(len(self.om_2_ts), 2)
   	self.ts.handle_response_from_om()
   	self.assertEqual(len(self.om_2_ts), 1)
   	self.ts.handle_response_from_om()
   	self.assertEqual(len(self.om_2_ts), 0)
   	self.assertEqual(self.ts.get_pnl(),10)

	
	def main():
		lp_2_gateway = deque() ob_2_ts = deque()
		ts_2_om = deque()
    ms_2_om = deque()
    om_2_ts = deque()
    gw_2_om = deque()
    om_2_gw = deque()
    lp = LiquidityProvider(lp_2_gateway)
    ob = OrderBook(lp_2_gateway, ob_2_ts)
    ts = TradingStrategy(ob_2_ts, ts_2_om, om_2_ts)
    ms = MarketSimulator(om_2_gw, gw_2_om)
    om = OrderManager(ts_2_om, om_2_ts, om_2_gw, gw_2_om)
		lp.read_tick_data_from_data_source() 
		while len(lp_2_gateway)>0:
			ob.handle_order_from_gateway()
			ts.handle_input_from_bb()
			om.handle_input_from_ts()
			ms.handle_order_from_gw()
			om.handle_input_from_market()
			ts.handle_response_from_om()
			lp.read_tick_data_from_data_source()

if __name__ == '__main__': 
	main()


