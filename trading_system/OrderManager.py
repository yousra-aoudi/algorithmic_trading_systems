# The purpose of the order manager is to gather the orders from all the trading strategies
# and to communicate this order with the market. 
# It will check the validity of the orders and can also keep track of the overall positions and PnL. 
# It can be a safeguard against mistakes introduced in trading strategies. 

# This component is the interface between the trading strategies and the market. 

class OrderManager:
	
	def __init__(self,ts_2_om = None, om_2_ts = None,om_2_gw=None,gw_2_om=None): 
		self.orders=[]
		self.order_id=0
		self.ts_2_om = ts_2_om
		self.om_2_gw = om_2_gw
		self.gw_2_om = gw_2_om
		self.om_2_ts = om_2_ts
		
	# To get new orders into the OrderManager system, we check whether the size of the ts_2_om channel is higher than 0. 
	# If there is an order in the channel, we remove this order and we call the handle_order_from_tradinig_strategy function. 	
	
	def handle_input_from_ts(self): 
		if self.ts_2_om is not None:
			if len(self.ts_2_om)>0: 
				self.handle_order_from_trading_strategy(self.ts_2_om.popleft())
			else:
				print('simulation mode')
				
	# The handle_order_from_trading_strategy function handles the new order coming from the trading strategies. 
	# For now, the OrderManager class will just get a copy of the order and store this order into a list of orders.
	
	def handle_order_from_trading_strategy(self,order): 
		if self.check_order_valid(order):
			order=self.create_new_order(order).copy() 
			self.orders.append(order)
			if self.om_2_gw is None:
				print('simulation mode') 
			else:
				self.om_2_gw.append(order.copy())
				
				
	# Once we take care of the order side, we are going to take care of the market response. 
	# For this, we will use the same method we used for the two prior functions. 
	# The handle_input_from_market function checks whether the gw_2_om channel exists. 
	# If that's the case, the function reads the market response object coming from the market
	# and calls the handle_order_from_gateway function. 
	
	def handle_input_from_market(self): 
		if self.gw_2_om is not None:
			if len(self.gw_2_om)>0: 
				self.handle_order_from_gateway(self.gw_2_om.popleft())
		else:
			print('simulation mode')
			
  # The handle_order_from_gateway function will look up in the list of orders created 
	# by the handle_order_from_trading_strategy function. If the market response corresponds
	# to an order in the list, it means that this market response is valid. 
	# We will be able to change the state of this order. 
	# If the market response doesn't find a specific order, 
	# it means that there is a problem in the exchange between the trading system and the market. 
	# We will need to raise an error. 
	
	def handle_order_from_gateway(self,order_update): 
		order=self.lookup_order_by_id(order_update['id']) 
		if order is not None:
			order['status']=order_update['status'] 
			if self.om_2_ts is not None:
				self.om_2_ts.append(order.copy()) 
			else:
				print('simulation mode') self.clean_traded_orders()
		else:
			print('order not found')
			
 	# The check_order_valid function will perform regular checks on an order. 
	def check_order_valid(self,order): 
		if order['quantity'] < 0:
			return False
		if order['price'] < 0:
			return False
    return True

	# The create_new_order, lookup_order_by_id, and clean_traded_orders functions will create an order 
	# based on the order sent by the trading strategy, which has a unique order ID.
	# The second function will help with looking up the order from the list of outstanding orders. 
	# The last function will clean the orders that have been rejected, filled, or canceled. 
	
	# The create_new_order function will create a dictionary to store the order characteristics:
	def create_new_order(self,order): 
		self.order_id += 1
		neworder = {'id': self.order_id,
								'price': order['price'], 
								'quantity': order['quantity'], 
								'side': order['side'], 
								'status': 'new',
								'action': 'New'
							 }
		return neworder

	# The lookup_order_by_id function will return a reference to the order by looking up by order ID:
	def lookup_order_by_id(self,id):
		for i in range(len(self.orders)):
			if self.orders[i]['id'] == id:
				return self.orders[i] 
		return None
	
	# The clean_traded_orders function will remove from the list of orders all the orders that have been filled:
	def clean_traded_orders(self): 
		order_offsets = []
		for k in range(len(self.orders)):
			if self.orders[k]['status'] == 'filled':
				order_offsets.append(k) 
			if len(order_offsets):
				for k in sorted(order_offsets,reverse = True): 
					del (self.orders[k])
					
	# Since the OrderManager component is critical for the safety of trading, 
	# we need to have exhaustive unit testing to ensure that no strategy will damage your gain, and prevent us from incurring losses:
	import unittest
	import OrderManager
	
	class TestOrderBook(unittest.TestCase):
		
		def setUp(self):
			self.order_manager = OrderManager()

		# The test_receive_order_from_trading_strategy test verifies whether an order is correctly received by the order manager. 
		# First, we create an order, order1, and we call the handle_order_from_trading_strategy function. 
		# Since the trading strategy creates two orders (stored in the channel ts_2_om), 
		# we call the test_receive_order_from_trading_strategy function twice. 
		# The order manager will then generate two orders.
		
		def test_receive_order_from_trading_strategy(self): 
			order1 = {'id': 10, 
								'price': 219, 
								'quantity': 10, 
								'side': 'bid',
							 } 
			self.order_manager.handle_order_from_trading_strategy(order1) 
			self.assertEqual(len(self.order_manager.orders),1) 
			self.order_manager.handle_order_from_trading_strategy(order1) 
			self.assertEqual(len(self.order_manager.orders),2) 
			self.assertEqual(self.order_manager.orders[0]['id'],1) 
			self.assertEqual(self.order_manager.orders[1]['id'],2)
		
		# To prevent a malformed order from being sent to the market, 
		# the test_receive_order_from_trading_strategy_error test checks
		# whether an order created with a negative price is rejected:
		
		def test_receive_order_from_trading_strategy_error(self): 
			order1 = {'id': 10, 
								'price': -219, 
								'quantity': 10, 
								'side': 'bid',
							 }
			self.order_manager.handle_order_from_trading_strategy(order1)
			self.assertEqual(len(self.order_manager.orders),0)
			
		
		#The following test, test_receive_from_gateway_filled, confirms a market response has been propagated by the order manager:
		def test_receive_from_gateway_filled(self): 
			self.test_receive_order_from_trading_strategy() 
			orderexecution1 = {'id': 2,
												 'price': 13, 
												 'quantity': 10, 
												 'side': 'bid', 
												 'status' : 'filled'
												}
			self.order_manager.handle_order_from_gateway(orderexecution1)
			self.assertEqual(len(self.order_manager.orders), 1)
			
		def test_receive_from_gateway_acked(self): 
			self.test_receive_order_from_trading_strategy() 
			orderexecution1 = {'id': 2,
												 'price': 13, 
												 'quantity': 10, 
												 'side': 'bid', 
												 'status' : 'acked'
												}
			self.order_manager.handle_order_from_gateway(orderexecution1) 
			self.assertEqual(len(self.order_manager.orders), 2) 
			self.assertEqual(self.order_manager.orders[1]['status'], 'acked')
 
		
