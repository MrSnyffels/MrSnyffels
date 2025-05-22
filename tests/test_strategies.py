import unittest
from strategies import SimpleThresholdStrategy # Assuming strategies/__init__.py makes it available

class TestSimpleThresholdStrategy(unittest.TestCase):

    def test_initialization_valid(self):
        strategy = SimpleThresholdStrategy(buy_threshold=50000, sell_threshold=60000, stop_loss_percentage=0.05)
        self.assertEqual(strategy.buy_threshold, 50000)
        self.assertEqual(strategy.sell_threshold, 60000)
        self.assertEqual(strategy.stop_loss_percentage, 0.05)
        self.assertIn("Simple Threshold Strategy", str(strategy))
        self.assertIn("50000", str(strategy))
        self.assertIn("60000", str(strategy))
        self.assertIn("5.0%", str(strategy))

    def test_initialization_invalid_thresholds(self):
        with self.assertRaisesRegex(ValueError, "Buy threshold must be less than sell threshold."):
            SimpleThresholdStrategy(buy_threshold=60000, sell_threshold=50000)
        with self.assertRaisesRegex(ValueError, "Buy threshold must be less than sell threshold."):
            SimpleThresholdStrategy(buy_threshold=50000, sell_threshold=50000)

    def test_initialization_invalid_stop_loss(self):
        with self.assertRaisesRegex(ValueError, "Stop-loss percentage must be between 0 and 1"):
            SimpleThresholdStrategy(stop_loss_percentage=0)
        with self.assertRaisesRegex(ValueError, "Stop-loss percentage must be between 0 and 1"):
            SimpleThresholdStrategy(stop_loss_percentage=1)
        with self.assertRaisesRegex(ValueError, "Stop-loss percentage must be between 0 and 1"):
            SimpleThresholdStrategy(stop_loss_percentage=1.1)
        with self.assertRaisesRegex(ValueError, "Stop-loss percentage must be between 0 and 1"):
            SimpleThresholdStrategy(stop_loss_percentage=-0.05)

    def test_check_signal(self):
        strategy = SimpleThresholdStrategy(buy_threshold=50000, sell_threshold=60000, stop_loss_percentage=0.05)
        
        # Buy signal
        self.assertEqual(strategy.check_signal(49000), "BUY")
        self.assertEqual(strategy.check_signal(49999.99), "BUY")
        
        # Sell signal
        self.assertEqual(strategy.check_signal(61000), "SELL")
        self.assertEqual(strategy.check_signal(60000.01), "SELL")
        
        # No signal
        self.assertIsNone(strategy.check_signal(50000))
        self.assertIsNone(strategy.check_signal(55000))
        self.assertIsNone(strategy.check_signal(60000))

if __name__ == '__main__':
    unittest.main()
