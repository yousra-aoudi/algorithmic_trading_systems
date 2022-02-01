#In the code, we will create the LiquidityProvider class. 
#The goal of this class is to act as a liquidity provider or an exchange. 
#It will send price updates to the trading system. 
#It will use the lp_2_gateway channel to send the price updates.


from random import randrange 
from random import sample, seed #Since we randomly generate liquidities, we will use a pseudo random generator initialized by a seed.


class LiquidityProvider:
  
  def __init__(self, lp_2_gateway=None):
    self.orders = []
    self.order_id = 0
    seed(0)
    self.lp_2_gateway = lp_2_gateway
    
  # We create a utility function to look up orders in the list of orders.
  def lookup_orders(self,id): 
    
    count=0
    for o in self.orders: 
      if o['id'] == id:
        return o, count 
      count+=1
    return None, None
  
  # The insert_manual_order function will insert orders manually into the trading system.
  def insert_manual_order(self,order): 
    if self.lp_2_gateway is None:
      print('simulation mode')
      return order 
    self.lp_2_gateway.append(order.copy())
    
  # The generate_random_order function will generate orders randomly. There will be three types of orders:
  # New (we will create a new Order ID)
  # Modify (we will use the order ID of an order that it was created and we will change the quantity)
  # Delete (we will use the order ID and we will delete the order)
  
  #Each time we create a new order, we will need to increment the order ID. 
  #We will use thelookup_orders function as shown in the following code to check
  #whether the order has already been created. 
  
  def generate_random_order(self): 
		
    price = randrange(8,12) 
    quantity = randrange(1,10)*100 
    side = sample(['buy','sell'],1)[0] 
    order_id = randrange(0,self.order_id+1) 
    o = self.lookup_orders(order_id)
    
    new_order = False 
    if o is None:
      action = 'new'
      new_order = True 
    else:
			action = sample(['modify','delete'],1)[0]
			
			ord = {'id': self.order_id, 
						 'price': price, 
						 'quantity': quantity, 
						 'side': side, 
						 'action': action
						}

		if not new_order: 
			self.order_id+=1
			self.orders.append(ord)
		
		if not self.lp_2_gateway: 
			print('simulation mode') 
			return ord
    
		self.lp_2_gateway.append(ord.copy())
  
	#We test whether the LiquidityProvider class works correctly by using unit testing. 
	#Python has the unittest module. 
	#As shown, we will create the TestMarketSimulator class, inheriting from TestCase.
	
	import unittest
	
	import LiquidityProvider
	
	class TestMarketSimulator(unittest.TestCase): 
		
		def setUp(self):
			self.liquidity_provider = LiquidityProvider()
			
		def test_add_liquidity(self): 
			self.liquidity_provider.generate_random_order() 
			self.assertEqual(self.liquidity_provider.orders[0]['id'],0)
			self.assertEqual(self.liquidity_provider.orders[0]['side'], 'buy') 
			self.assertEqual(self.liquidity_provider.orders[0]['quantity'], 700) 
			self.assertEqual(self.liquidity_provider.orders[0]['price'], 11) OrderBook class
     
