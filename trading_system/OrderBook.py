# We will build an OrderBook class; 
# this class will collect orders from LiquidityProvider and sort the orders and create book events.
# The book events in a trading system are preset events and these events can be anything
# a trader thinks it is worth knowing. 
# In this implementation, we choose to generate a book event each time there is a change on the top of the book 
# (any changes in the first level of the book will create an event).

# We will code OrderBook by having a list for asks and bids. 
# The constructor has two optional arguments, which are the two channels to receive orders and send book events.

class OrderBook:
  
  def __init__(self,gt_2_ob = None,ob_to_ts = None):
    self.list_asks = [] 
    self.list_bids = [] 
    self.gw_2_ob=gt_2_ob 
    self.ob_to_ts = ob_to_ts 
    self.current_bid = None 
    self.current_ask = None
    
  # We will write a function, handle_order_from_gateway, which will receive the orders from the liquidity provider.
	def handle_order_from_gateway(self,order = None): 
		if self.gw_2_ob is None:
			print('simulation mode')
			self.handle_order(order) 
		elif len(self.gw_2_ob)>0:
			order_from_gw=self.gw_2_ob.popleft()
			self.handle_order(order_from_gw)
	
	# Let's write a function to check whether the gw_2_ob channel has been defined. 
	# If the channel has been instantiated, handle_order_from_gateway will pop the order
	# from the top of deque gw_2_ob and will call the handle_order function to process the order for a given action: 
	
	# In the code, handle_order calls either handle_modify, handle_delete, or handle_new.
	def handle_order(self,o): 
		if o['action']=='new': 
			self.handle_new(o) # The handle_new function adds an order to the appropriate list,self.list_bidsandself.list_asks.
		elif o['action']=='modify': 
			self.handle_modify(o) # The handle_modify function modifies the order from the book by using the order given as an argument of this function.
		elif o['action']=='delete': 
			self.handle_delete(o) # The handle_delete function removes an order from the book by using the order given as an argument of this function.
		else:
			print('Error-Cannot handle this action')
			
		return self.check_generate_top_of_book_event()
	
	# We will now implement the handle_modify function to manage the amendment. 
	# This function searches in the list of orders if the order exists. 
	# If that's the case, we will modify the quantity by the new quantity. 
	# This operation will be possible only if we reduce the quantity of the order:
	def handle_modify(self,o): 
		order=self.find_order_in_a_list(o) 
		if order['quantity'] > o['quantity']:
			order['quantity'] = o['quantity'] 
		else:
			print('incorrect size') 
		return None
	
	# The handle_delete function will manage the order cancelation. 
	# We will remove the orders from the list of orders by checking whether the order exists with the order ID:
	def handle_delete(self,o):
		lookup_list = self.get_list(o)
		order = self.find_order_in_a_list(o,lookup_list) 
		if order is not None:
			lookup_list.remove(order)
		return None
	
	# The get_list function in the code will help to find the side (which order book) contains the order:
	def get_list(self,o): 
		if 'side' in o:
			if o['side']=='bid':
				lookup_list = self.list_bids
			elif o['side'] == 'ask': 
				lookup_list = self.list_asks
			else:
				print('incorrect side') 
				return None
			return lookup_list
		else:
			for order in self.list_bids: 
				if order['id']==o['id']:
					return self.list_bids 
			for order in self.list_asks:
				if order['id'] == o['id']: 
					return self.list_asks
			return None
   
 	# The find_order_in_a_list function will return a reference to the order if this order exists:
	def find_order_in_a_list(self,o,lookup_list = None): 
		if lookup_list is None:
			lookup_list = self.get_list(o) 
		if lookup_list is not None:
			for order in lookup_list:
				if order['id'] == o['id']:
					return order
			print('order not found id=%d' % (o['id']))
		return None
	
	# The following two functions will help with creating the book events. 
	# The book events as defined in the check_generate_top_of_book_event function
	# will be created by having the top of the book changed.
	
	# The create_book_event function creates a dictionary representing a book event.
	# A book event will be given to the trading strategy to indicate what change was made at the top of the book level:
	def create_book_event(self,bid,offer): 
		book_event = {"bid_price": bid['price'] if bid else -1, 
									"bid_quantity": bid['quantity'] if bid else -1, 
									"offer_price": offer['price'] if offer else -1, 
									"offer_quantity": offer['quantity'] if offer else -1
								 }
		return book_event
	
	# The check_generate_top_of_book_event function will create a book event when the top of the book has changed. 
	# When the price or the quantity for the best bid or offer has changed, 
	# we will inform the trading strategies that there is a change at the top of the book:
	def check_generate_top_of_book_event(self): 
		tob_changed = False
		if not self.list_bids:
			if self.current_bid is not None: 
				tob_changed = True
			# if top of book change generate an event if not self.current_bid:
			if self.current_bid != self.list_bids[0]: 
				tob_changed=True 
				self.current_bid=self.list_bids[0] if self.list_bids else None
			if not self.current_ask: 
				if not self.list_asks:
					if self.current_ask is not None: 
						tob_changed = True
					elif self.current_ask != self.list_asks[0]: 
						tob_changed = True
						self.current_ask = self.list_asks[0] if self.list_asks else None
				
			if tob_changed: 
				be=self.create_book_event(self.current_bid,self.current_ask)
			if self.ob_to_ts is not None: 
				self.ob_to_ts.append(be)
			else:
				return be
	
	# When we test the order book, we need to test the following functionalities:
	# Adding a new order 
	# Modifying a new order 
	# Deleting an order 
	# Creating a book event
	
	# Unit test for the Order Book
	import unittest
	import OrderBook
	
	class TestOrderBook(unittest.TestCase): 
		
		def setUp(self):
			self.reforderbook = OrderBook()
		
		# Let's create a function to verify if the order insertion works. 
		# The book must have the list of asks and the list of bids sorted:
		def test_handlenew(self): 
			order1 = {'id': 1, 
								'price': 219, 
								'quantity': 10, 
								'side': 'bid', 
								'action': 'new'
							 }
			ob_for_aapl = self.reforderbook
			ob_for_aapl.handle_order(order1)
			order2 = order1.copy()
			order2['id'] = 2
			order2['price'] = 220 
			ob_for_aapl.handle_order(order2) 
			order3 = order1.copy() 
			order3['price'] = 223 
			order3['id'] = 3 
			ob_for_aapl.handle_order(order3) 
			order4 = order1.copy() 
			order4['side'] = 'ask' 
			order4['price'] = 220 
			order4['id'] = 4 
			ob_for_aapl.handle_order(order4) 
			order5 = order4.copy() 
			order5['price'] = 223 
			order5['id'] = 5 
			ob_for_aapl.handle_order(order5) 
			order6 = order4.copy() 
			order6['price'] = 221 
			order6['id'] = 6 
			ob_for_aapl.handle_order(order6)
			
			self.assertEqual(ob_for_aapl.list_bids[0]['id'],3) 
			self.assertEqual(ob_for_aapl.list_bids[1]['id'], 2) 
			self.assertEqual(ob_for_aapl.list_bids[2]['id'], 1) 
			self.assertEqual(ob_for_aapl.list_asks[0]['id'],4) 
			self.assertEqual(ob_for_aapl.list_asks[1]['id'], 6) 
			self.assertEqual(ob_for_aapl.list_asks[2]['id'], 5)
			
		# Let's now write the following function to test whether the amendment works. 
		# We fill the book by using the prior function, then we amend the order by changing the quantity:
		def test_handleamend(self): 
			self.test_handlenew() 
			order1 = {'id': 1, 
								'quantity': 5, 
								'action': 
								'modify'
							 }
			self.reforderbook.handle_order(order1)
			self.assertEqual(self.reforderbook.list_bids[2]['id'], 1) 
			self.assertEqual(self.reforderbook.list_bids[2]['quantity'], 5)
		
		# Book management function that removes order from the book by the order ID. 
		# In this test case, we fill the book with the prior function and we remove the order:
		def test_handledelete(self): 
			self.test_handlenew() 
			order1 = {'id': 1,
								'action': 
								'delete'
							 }
			self.assertEqual(len(self.reforderbook.list_bids), 3)
			self.reforderbook.handle_order(order1)
			self.assertEqual(len(self.reforderbook.list_bids), 2)
			
		def test_generate_book_event(self): 
			order1 = {'id': 1, 
								'price': 219, 
								'quantity': 10, 
								'side': 'bid', 
								'action': 'new'
							 }
			ob_for_aapl = self.reforderbook
			self.assertEqual(ob_for_aapl.handle_order(order1),
											 {'bid_price': 219, 'bid_quantity': 10, 
												'offer_price': -1, 'offer_quantity': -1
											 }
											)
			order2 = order1.copy()
			order2['id'] = 2
			order2['price'] = 220
			order2['side'] = 'ask' 
			self.assertEqual(ob_for_aapl.handle_order(order2), 
											 {'bid_price': 219, 'bid_quantity': 10,
												'offer_price': 220, 'offer_quantity': 10
											 }
											) 
			
	if __name__ == '__main__':
		unittest.main()
  


	





	
	
	
	
	
    
