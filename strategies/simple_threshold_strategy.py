class SimpleThresholdStrategy:
    def __init__(self, buy_threshold=50000, sell_threshold=60000, stop_loss_percentage=0.05):
        self.name = "Simple Threshold Strategy"
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        if buy_threshold >= sell_threshold:
            raise ValueError("Buy threshold must be less than sell threshold.")
        if not (0 < stop_loss_percentage < 1):
            raise ValueError("Stop-loss percentage must be between 0 and 1 (e.g., 0.05 for 5%).")
        self.stop_loss_percentage = stop_loss_percentage

    def check_signal(self, current_price: float) -> str | None:
        """
        Checks for a buy or sell signal based on the current price.

        Args:
            current_price: The current market price of the asset.

        Returns:
            "BUY" if the price is below the buy threshold.
            "SELL" if the price is above the sell threshold.
            None otherwise.
        """
        if current_price < self.buy_threshold:
            return "BUY"
        elif current_price > self.sell_threshold:
            return "SELL"
        else:
            return None

    def __str__(self):
        return f"{self.name} (Buy < ${self.buy_threshold}, Sell > ${self.sell_threshold}, Stop-Loss: {self.stop_loss_percentage*100}%)"

if __name__ == '__main__':
    # Example Usage (for testing the strategy itself)
    strategy = SimpleThresholdStrategy(buy_threshold=50000, sell_threshold=60000, stop_loss_percentage=0.05)
    print(f"Strategy loaded: {strategy}")

    test_prices = [45000, 55000, 65000, 49999, 60001]
    print(f"Buy threshold: {strategy.buy_threshold}, Sell threshold: {strategy.sell_threshold}, SL: {strategy.stop_loss_percentage*100}%")
    for price in test_prices:
        signal = strategy.check_signal(price)
        print(f"Price: ${price}, Signal: {signal}")

    try:
        SimpleThresholdStrategy(buy_threshold=60000, sell_threshold=50000)
    except ValueError as e:
        print(f"Error creating strategy with invalid thresholds: {e}")
    
    try:
        SimpleThresholdStrategy(stop_loss_percentage=1.5)
    except ValueError as e:
        print(f"Error creating strategy with invalid stop-loss: {e}")

    try:
        SimpleThresholdStrategy(stop_loss_percentage=0)
    except ValueError as e:
        print(f"Error creating strategy with invalid stop-loss (zero): {e}")

    strategy_high_risk = SimpleThresholdStrategy(stop_loss_percentage=0.10) # 10% stop loss
    print(strategy_high_risk)
