import unittest
import time
from core import MarketSimulator # Assuming core/__init__.py makes it available

class TestMarketSimulator(unittest.TestCase):

    def test_initialization(self):
        simulator = MarketSimulator(initial_price=50000)
        self.assertEqual(simulator.get_current_price(), 50000)
        self.assertEqual(len(simulator.trade_history), 0)

    def test_update_market_price(self):
        simulator = MarketSimulator(initial_price=50000, price_fluctuation_range=100)
        initial_price = simulator.get_current_price()
        
        updated_price = simulator.update_market_price()
        self.assertNotEqual(updated_price, initial_price) # Price should change
        self.assertTrue(initial_price - 100 <= updated_price <= initial_price + 100, 
                        "Price should be within initial_price +/- fluctuation_range if only one update")

        # Test price floor
        simulator_low = MarketSimulator(initial_price=1050, price_fluctuation_range=100)
        for _ in range(20): # Multiple updates to try and hit the floor
            simulator_low.update_market_price()
        self.assertGreaterEqual(simulator_low.get_current_price(), 1000.00)
        
        # Check rounding
        self.assertEqual(simulator.get_current_price(), round(simulator.get_current_price(), 2))


    def test_execute_trade(self):
        simulator = MarketSimulator(initial_price=50000)
        
        # Test BUY trade
        buy_price = 50000
        buy_amount = 0.1
        buy_stop_loss = 47500
        simulator.execute_trade(trade_type="BUY", amount=buy_amount, price=buy_price, stop_loss_price=buy_stop_loss)
        
        self.assertEqual(len(simulator.trade_history), 1)
        trade1 = simulator.trade_history[0]
        self.assertEqual(trade1["type"], "BUY")
        self.assertEqual(trade1["amount_btc"], buy_amount)
        self.assertEqual(trade1["price_usd"], buy_price)
        self.assertEqual(trade1["stop_loss_price_usd"], buy_stop_loss)
        self.assertIn("timestamp", trade1)

        # Test SELL trade
        time.sleep(0.01) # ensure different timestamp
        sell_price = 52000
        sell_amount = 0.05
        simulator.execute_trade(trade_type="SELL", amount=sell_amount, price=sell_price) # No stop-loss for sell

        self.assertEqual(len(simulator.trade_history), 2)
        trade2 = simulator.trade_history[1]
        self.assertEqual(trade2["type"], "SELL")
        self.assertEqual(trade2["amount_btc"], sell_amount)
        self.assertEqual(trade2["price_usd"], sell_price)
        self.assertNotIn("stop_loss_price_usd", trade2)
        self.assertIn("timestamp", trade2)
        
        self.assertNotEqual(trade1["timestamp"], trade2["timestamp"])


if __name__ == '__main__':
    unittest.main()
