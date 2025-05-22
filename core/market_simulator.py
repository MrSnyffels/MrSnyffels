import random
import time

class MarketSimulator:
    def __init__(self, initial_price=55000, price_fluctuation_range=500):
        self.current_btc_price = float(initial_price)
        self.price_fluctuation_range = price_fluctuation_range
        self.trade_history = [] # To store simulated trades later

    def get_current_price(self) -> float:
        """Returns the current simulated Bitcoin price."""
        return self.current_btc_price

    def update_market_price(self) -> float:
        """
        Simulates a market price update.
        The price will change randomly within a defined fluctuation range.
        """
        change = random.uniform(-self.price_fluctuation_range, self.price_fluctuation_range)
        self.current_btc_price += change
        # Ensure price doesn't go below a reasonable minimum (e.g., $1000)
        if self.current_btc_price < 1000:
            self.current_btc_price = 1000.00
        
        # Round to 2 decimal places like typical currency
        self.current_btc_price = round(self.current_btc_price, 2)
        # print(f"Market Update: BTC price is now ${self.current_btc_price}") # For debugging
        return self.current_btc_price

    # Placeholder for trade execution logic
    def execute_trade(self, trade_type: str, amount: float, price: float, stop_loss_price: float | None = None):
        """Simulates executing a trade. For now, just records it."""
        timestamp = time.time()
        trade_record = {
            "timestamp": timestamp,
            "type": trade_type, # "BUY" or "SELL"
            "amount_btc": amount, # Amount of BTC bought/sold
            "price_usd": price
        }
        if stop_loss_price is not None and trade_type == "BUY":
            trade_record["stop_loss_price_usd"] = stop_loss_price
        
        self.trade_history.append(trade_record)
        # print(f"Simulated Trade: {trade_type} {amount} BTC at ${price}, SL: ${stop_loss_price}")
        return True # Simulate successful trade

if __name__ == '__main__':
    simulator = MarketSimulator(initial_price=50000, price_fluctuation_range=100)
    print(f"Initial BTC Price: ${simulator.get_current_price()}")

    for _ in range(10): # Simulate 10 price updates
        time.sleep(0.1) # Simulate time passing
        updated_price = simulator.update_market_price()
        print(f"Updated BTC Price: ${updated_price}")

    # Example of simulated trade
    buy_price = simulator.get_current_price()
    stop_loss = buy_price * 0.9 # 10% stop loss
    simulator.execute_trade("BUY", 0.1, buy_price, stop_loss_price=stop_loss)
    simulator.execute_trade("SELL", 0.05, simulator.get_current_price() + 5000) # Simulate selling higher
    print("\nSimulated Trade History:")
    for trade in simulator.trade_history:
        print(trade)
