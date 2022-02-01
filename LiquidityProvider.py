#The goal of the Liquidity Provider Class is to generate liquidities, as an exchange.
#It will send price updates to the trading system.
#Since we randomly generate liquidities, we just need to test whether 
#the first liquidity that is sent by the LiquidityProvider Class is well formed.

from random import randrange 
from random import sample, seed


class LiquidityProvider:
def __init__(self, lp_2_gateway=None):
                    self.orders = []
                    self.order_id = 0
                    seed(0)
                    self.lp_2_gateway = lp_2_gateway
