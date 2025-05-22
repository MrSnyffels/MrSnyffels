import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler # For handling button presses
import asyncio # For the mock monitoring loop

# Assuming these are correctly set up in __init__.py files
from core import MarketSimulator
from strategies import SimpleThresholdStrategy

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Placeholder for Telegram Bot Token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE" # Important: Replace with a placeholder or use environment variables

# Global instances for simplicity in this step
# In a more complex app, manage these within application context or dedicated classes
market_sim = MarketSimulator(initial_price=52000, price_fluctuation_range=1500) # Increased fluctuation range
# Initialize with default thresholds, or allow configuration later
active_strategy = SimpleThresholdStrategy(buy_threshold=50000, sell_threshold=55000, stop_loss_percentage=0.05) # Explicitly set SLP

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Welcome to the Bitcoin Trading Bot.",
        # We'll add buttons for strategy selection later
    )
    await update.message.reply_text(
        "I can help you simulate Bitcoin trading based on selected strategies. "
        "Use /help to see available commands (coming soon!)."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts a short mock monitoring process."""
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Starting market monitoring for 5 price updates...")
    
    context.user_data['monitoring'] = True # Flag to control monitoring

    for i in range(5): # Simulate 5 price updates
        if not context.user_data.get('monitoring', False):
            await context.bot.send_message(chat_id=chat_id, text="Monitoring stopped by user.")
            break

        price = market_sim.update_market_price()
        signal = active_strategy.check_signal(price)
        
        message = f"Monitored Price Update #{i+1}: BTC = ${price:,.2f}"
        if signal:
            message += f" - Signal: {signal}!"
            # Build keyboard for confirmation
            keyboard = [
                [
                    InlineKeyboardButton(f"Confirm {signal} BTC", callback_data=f'trade_confirm_{signal}_{price}'),
                    InlineKeyboardButton("Reject", callback_data=f'trade_reject_{signal}_{price}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
        else:
            message += " - No signal."
            # Send plain message if no signal, or optionally skip non-signal messages
            await context.bot.send_message(chat_id=chat_id, text=message) 

        await asyncio.sleep(2) # Wait 2 seconds before the next price update

    if context.user_data.get('monitoring', True): # If loop finished without stop
       await context.bot.send_message(chat_id=chat_id, text="Finished market monitoring.")
    context.user_data['monitoring'] = False

async def stop_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stops the mock monitoring process."""
    chat_id = update.effective_chat.id
    if context.user_data.get('monitoring', False):
        context.user_data['monitoring'] = False
        await context.bot.send_message(chat_id=chat_id, text="Stopping market monitoring...")
    else:
        await context.bot.send_message(chat_id=chat_id, text="Monitoring is not currently active.")

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer() # Answer the callback query (important step)

    # query.data will be like 'trade_confirm_BUY_52000.00' or 'trade_reject_SELL_53000.00'
    parts = query.data.split('_')
    # action_type = parts[0] # 'trade' # Not strictly needed if pattern is specific
    action_verb = parts[1] # 'confirm' or 'reject'
    signal_type = parts[2] # 'BUY' or 'SELL'
    price_str = parts[3]   # '52000.00'
    price = float(price_str)

    message_text = ""

    if action_verb == 'confirm':
        dummy_amount_btc = 0.01 
        stop_loss_price_calculated = None

        if signal_type == "BUY":
            stop_loss_price_calculated = price * (1 - active_strategy.stop_loss_percentage)
            stop_loss_price_calculated = round(stop_loss_price_calculated, 2)
        
        # Pass stop_loss_price_calculated to execute_trade
        if market_sim.execute_trade(trade_type=signal_type, 
                                    amount=dummy_amount_btc, 
                                    price=price, 
                                    stop_loss_price=stop_loss_price_calculated if signal_type == "BUY" else None):
            message_text = f"Simulated {signal_type} of {dummy_amount_btc} BTC at ${price:,.2f} confirmed and recorded."
            if signal_type == "BUY" and stop_loss_price_calculated is not None:
                message_text += f"\nMock Stop-Loss set at ${stop_loss_price_calculated:,.2f} ({active_strategy.stop_loss_percentage*100:.0f}%)."
            logger.info(f"User confirmed {signal_type} at ${price}. SL: {stop_loss_price_calculated if signal_type == 'BUY' else 'N/A'}. Simulated trade recorded.")
        else:
            message_text = f"Failed to simulate {signal_type} of {dummy_amount_btc} BTC at ${price:,.2f}."
            logger.error(f"User confirmed {signal_type} at ${price}, but simulated trade failed.")
    
    elif action_verb == 'reject':
        message_text = f"Simulated {signal_type} of BTC at ${price:,.2f} rejected by user."
        logger.info(f"User rejected {signal_type} at ${price}.")

    # Edit the original message to remove the inline keyboard and show the result
    # Ensure the original message text part is included before the new status
    original_message_part = query.message.text.split("\n")[0] # Get the first line of the original message
    await query.edit_message_text(text=f"{original_message_part}\n\n➡️ {message_text}")

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("Please replace YOUR_TELEGRAM_BOT_TOKEN_HERE with your actual Telegram Bot Token.")
        # For now, we won't exit, to allow testing the structure, but in a real scenario, the bot wouldn't start.
        # return 

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("monitor", monitor))
    application.add_handler(CommandHandler("stop_monitor", stop_monitor))
    application.add_handler(CallbackQueryHandler(button_callback_handler, pattern='^trade_'))

    # Add an error handler
    application.add_error_handler(error_handler)

    # We will add more handlers here later (e.g., for selecting strategies)

    # Run the bot until the user presses Ctrl-C
    # application.run_polling() # We will uncomment this when ready for actual polling

    logger.info("Telegram bot setup is complete. Polling would start here if enabled.")

if __name__ == '__main__':
    # main() # We will uncomment this when ready to run the bot directly
    logger.info("bot/main.py structure created. Not running main() yet.")
