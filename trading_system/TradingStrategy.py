# The Trading Strategy Class represents the trading strategy based on top of the book changes.
# It will create an order when the top of the book is crossed. 
# This means when there is an arbitrage opportunity. 

# This class is divided into two parts:
#  Signal part : this part handles the trading signal. In this case, a signal will be triggered when the top of the book is crossed.
#Execution part : this part handles the execution of the orders. It will be responsible of managing the order life cycle. 

# In the following code, we will create the TradingStrategy Class.
# The class will have three parameters, which are reference to the three communication channels.
# One is taking the book events form the order book, 
#the two others are made to send orders and receive order updates from the market.


class TradingStrategy:
	
	def __init__(self, ob_2_ts, ts_2_om, om_2_ts):
		self.orders = []
		self.order_id = 0
		self.position = 0
		self.pnl = 0
		self.cash = 10000
		self.current_bid = 0
		self.current_offer = 0
		self.ob_2_ts = ob_2_ts
		self.ts_2_om = ts_2_om
		self.om_2_ts = om_2_ts
		
		
	#We will code two functions to handle the book events from the order book as shown in the code; 
	#handle_input_from_bb checks whether there are book events in deque ob_2_ts and
	#will call the handle_book_event function. 
	
	def handle_input_from_bb(self,book_event=None): 
		if self.ob_2_ts is None:
			print('simulation mode')
			self.handle_book_event(book_event) 
			
		else:
			if len(self.ob_2_ts)>0: 
				be=self.handle_book_event(self.ob_2_ts.popleft()) 
				self.handle_book_event(be)
				
	
	# The handle_book_event function calls the function signal to check whether 
	# there is a signal to send an order.		
	def handle_book_event(self,book_event):
		if book_event is not None:
			self.current_bid = book_event['bid_price'] 
			self.current_offer = book_event['offer_price']
			
		if self.signal(book_event): 
			self.create_orders(book_event,
												 min(book_event['bid_quantity'], 
														 book_event['offer_quantity'])
												)
			self.execution()
		
	# In this case, the signal verifies whether the bid price is higher than the ask price. 
	# If this condition is verified, this function returns True. 
	# The handle_book_event function in the code will create an order
	# by calling the create_orders function. 
	
	def signal(self, book_event): 
		if book_event is not None:
			if book_event["bid_price"] > book_event["offer_price"]:
				if book_event["bid_price"]>0 and book_event["offer_price"]>0: 
					return True
				else:
					return False
		else:
			return False
		
	# The create_orders function from the code creates two orders. 
	# When we have an arbitrage situation, we must trade fast. 
	# Therefore, the two orders must be created simultaneously. 
	# This function increments the order ID for any created orders. 
	# This order ID will be local to the trading strategy. 
	
	
	def create_orders(self,book_event,quantity): 
		self.order_id+=1 
		ord = {'id': self.order_id,
					 'price': book_event['bid_price'], 
					 'quantity': quantity,
					 'side': 'sell',
					 'action': 'to_be_sent'
					}
		self.orders.append(ord.copy())
		
		price=book_event['offer_price'] 
		side='buy'
		self.order_id+=1
		ord = {'id': self.order_id,
					 'price': book_event['offer_price'], 
					 'quantity': quantity,
					 'side': 'buy',
					 'action': 'to_be_sent'
					}
		self.orders.append(ord.copy())
	
	
	# The function execution will take care of processing orders in their whole order life cycle. 
	# For instance, when an order is created, its status is new. 
	# Once the order has been sent to the market, the market will respond by acknowledging the order or reject the order. 
	# If the other is rejected, this function will remove the order from the list of outstanding orders.
	
	# When an order is filled, it means this order has been executed. 
	# Once an order is filled, the strategy must update the position 
	# and the PnL with the help of the code below. 
	
	def execution(self):
		orders_to_be_removed = []
		for index, order in enumerate(self.orders):
			if order['action'] == 'to_be_sent': # Send order
				order['status'] = 'new' 
				order['action'] = 'no_action' 
				if self.ts_2_om is None:
					print('Simulation mode') 
				else:
					self.ts_2_om.append(order.copy()) 
			if order['status'] == 'rejected':
				orders_to_be_removed.append(index) 
			if order['status'] == 'filled':
				orders_to_be_removed.append(index)
				pos = order['quantity'] if order['side'] == 'buy' else -order['quantity'] 
				self.position += pos
				self.pnl -= pos * order['price']
				self.cash -= pos * order['price']
			
		for order_index in sorted(orders_to_be_removed,reverse=True): 
			del (self.orders[order_index])
  
	# The handle_response_from_om and handle_market_response functions will collect the information
	# from the order manager (collecting information from the market) as shown in the following code. 
	
	def handle_response_from_om(self): 
		if self.om_2_ts is not None:
			self.handle_market_response(self.om_2_ts.popleft()) 
		else:
			print('simulation mode')
	
	def handle_market_response(self, order_execution): 
		order,_=self.lookup_orders(order_execution['id']) 
		if order is None:
			print('error not found')
			return 
		order['status']=order_execution['status'] 
		self.execution()
	
	# The lookup_orders function in the following code checks whether
	# an order exists in the data structure gathering all the orders and return this order.
	
	def lookup_orders(self,id): 
		count=0
		for o in self.orders: 
			if o['id'] == id:
				return o, count
			count+=1 
		return None, None
	
	# The test_receive_top_of_book test case verifies whether the book event is correctly handled by the trading strategy. 
	# The test_rejected_order and test_filled_order test cases verify whether a response from the market is correctly handled.
	
	
	# The code will create a setUp function, being called each time we run a test. 
	# We will create TradingStrategy each time we invoke a test. 
	# This way of doing it increases the reuse of the same code.
	
import unittest
import TradingStrategy


class TestMarketSimulator(unittest.TestCase): 
	
	def setUp(self):
		self.trading_strategy= TradingStrategy()
	# The first unit test that we perform for a trading strategy is 
	# to validate that the book event sent by the book is received correctly. 
	
	# We will create a book event manually and we will use the handle_book_event function. 
	# We are going to validate the fact that the trading strategy behaves the way it is supposed
	# to by checking whether the orders produced were expected.
	
	# Let's verify whether the trading strategy receives the market response coming from the order manager.
	def test_receive_top_of_book(self): 
		book_event = {"bid_price" : 12, 
									"bid_quantity" : 100, 
									"offer_price" : 11, 
									"offer_quantity" : 150
								 }
		self.trading_strategy.handle_book_event(book_event) 
		self.assertEqual(len(self.trading_strategy.orders), 2) 
		self.assertEqual(self.trading_strategy.orders[0]['side'], 'sell') 
		self.assertEqual(self.trading_strategy.orders[1]['side'], 'buy') 
		self.assertEqual(self.trading_strategy.orders[0]['price'], 12) 
		self.assertEqual(self.trading_strategy.orders[1]['price'], 11) 
		self.assertEqual(self.trading_strategy.orders[0]['quantity'], 100) 
		self.assertEqual(self.trading_strategy.orders[1]['quantity'], 100) 
		self.assertEqual(self.trading_strategy.orders[0]['action'], 'no_action') 
		self.assertEqual(self.trading_strategy.orders[1]['action'], 'no_action')
		
		
	# We will create a market response indicating a rejection of a given order. 
	# We will also check whether the trading strategy removes this order from the list of orders belonging to the trading strategy:
	def test_rejected_order(self): 
		self.test_receive_top_of_book() 
		order_execution = {'id': 1,
											 'price': 12, 
											 'quantity': 100, 
											 'side': 'sell', 
											 'status' : 'rejected'
											}
		self.trading_strategy.handle_market_response(order_execution) 
		self.assertEqual(self.trading_strategy.orders[0]['side'], 'buy') 
		self.assertEqual(self.trading_strategy.orders[0]['price'], 11) 
		self.assertEqual(self.trading_strategy.orders[0]['quantity'], 100) 
		self.assertEqual(self.trading_strategy.orders[0]['status'], 'new')

	# Now, we will need to test the behavior of the trading strategy when the order is filled. 
	# We will need to update the position, the pnl, and the cash that we have to invest as shown in the following code. 
	def test_filled_order(self): 
		self.test_receive_top_of_book() 
		order_execution = {'id': 1,
											 'price': 11, 
											 'quantity': 100, 
											 'side': 'sell', 
											 'status' : 'filled'
											}
		self.trading_strategy.handle_market_response(order_execution)
		self.assertEqual(len(self.trading_strategy.orders),1)
		order_execution = {'id': 2,
											 'price': 12, 
											 'quantity': 100, 
											 'side': 'buy', 
											 'status' : 'filled'
											}
		self.trading_strategy.handle_market_response(order_execution)
		self.assertEqual(self.trading_strategy.position, 0)
		self.assertEqual(self.trading_strategy.cash, 10100)
		self.assertEqual(self.trading_strategy.pnl, 100)
	
		
