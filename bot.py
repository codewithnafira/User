#!/usr/bin/env python3
"""
Telegram Forwarded Message Info Bot
- Shows detailed info when messages are forwarded
- /myid command to get your own ID
- Privacy-aware handling
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramInfoBot:
    def __init__(self, token: str):
        """Initialize the bot with Telegram token"""
        self.token = token
        self.app = Application.builder().token(self.token).build()
        
        # Register handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("myid", self.myid_command))
        self.app.add_handler(MessageHandler(filters.FORWARDED, self.handle_forwarded))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message"""
        user = update.effective_user
        await update.message.reply_text(
            f"👋 Hello {user.first_name}!\n\n"
            "I can show information about forwarded messages.\n\n"
            "Try these commands:\n"
            "/myid - Show your Telegram ID\n"
            "/help - Show help information\n\n"
            "Just forward me any message to see info about the sender!",
            parse_mode="HTML"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message"""
        await update.message.reply_text(
            "ℹ️ <b>Bot Help</b>\n\n"
            "<b>Commands:</b>\n"
            "/myid - Show your Telegram ID\n"
            "/help - This message\n\n"
            "<b>Forwarding:</b>\n"
            "• Forward any message to see sender info\n"
            "• Some info may be hidden due to privacy settings",
            parse_mode="HTML"
        )

    async def myid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /myid command"""
        user = update.effective_user
        await update.message.reply_text(
            f"🆔 <b>Your Telegram ID</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ First Name: {user.first_name}\n"
            f"├ Username: @{user.username if user.username else 'N/A'}\n"
            f"└ Language: {user.language_code if user.language_code else 'N/A'}",
            parse_mode="HTML"
        )

    @staticmethod
    def estimate_account_age(user_id: int) -> str:
        """Estimate account age from user ID"""
        try:
            timestamp = (user_id >> 32) & 0xFFFFFFFF
            account_date = datetime.fromtimestamp(timestamp)
            age = datetime.now() - account_date
            
            if age.days > 365:
                return f"{age.days//365} year{'s' if age.days//365>1 else ''} old"
            return f"{age.days//30} month{'s' if age.days//30>1 else ''} old"
        except Exception as e:
            logger.warning(f"Couldn't estimate account age: {e}")
            return "unknown age"

    def format_user_info(self, user) -> str:
        """Format user information in tree structure"""
        return (
            f"👤 <b>User Information</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ Is Bot: {'✅ Yes' if user.is_bot else '❌ No'}\n"
            f"├ First Name: {user.first_name}\n"
            f"├ Username: @{user.username if user.username else 'N/A'}\n"
            f"├ Language: {user.language_code if hasattr(user, 'language_code') else 'N/A'}\n"
            f"└ Account Age: {self.estimate_account_age(user.id)}\n"
        )

    def format_chat_info(self, chat) -> str:
        """Format chat/channel information"""
        return (
            f"📢 <b>Chat Information</b>\n"
            f"├ ID: <code>{chat.id}</code>\n"
            f"├ Type: {chat.type.capitalize()}\n"
            f"├ Title: {chat.title}\n"
            f"└ Username: @{chat.username if chat.username else 'N/A'}\n"
        )

    async def handle_forwarded(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle forwarded messages with comprehensive fallbacks"""
        msg = update.message
        logger.info(f"Received forwarded message: {msg.message_id}")
        
        try:
            if msg.forward_from:
                # Message from a user
                await msg.reply_text(
                    self.format_user_info(msg.forward_from),
                    parse_mode="HTML"
                )
            elif msg.forward_from_chat:
                # Message from a chat/channel
                await msg.reply_text(
                    self.format_chat_info(msg.forward_from_chat),
                    parse_mode="HTML"
                )
            elif msg.forward_sender_name:
                # Privacy-enabled forward
                await msg.reply_text(
                    f"👤 <b>Forwarded from</b>: {msg.forward_sender_name}\n"
                    f"🕒 <b>Date</b>: {msg.forward_date.strftime('%Y-%m-%d %H:%M')}\n"
                    "⚠️ <i>More info hidden by privacy settings</i>",
                    parse_mode="HTML"
                )
            else:
                await msg.reply_text(
                    "❌ <b>Couldn't identify sender</b>\n\n"
                    "Possible reasons:\n"
                    "1. Not a proper forwarded message\n"
                    "2. Extremely strict privacy settings\n"
                    "3. From a secret chat",
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Error handling forwarded message: {e}")
            await msg.reply_text(
                "⚠️ <b>Bot error occurred</b>\n"
                "Please check server logs",
                parse_mode="HTML"
            )

    def run(self):
        """Run the bot until interrupted"""
        logger.info("Starting bot...")
        self.app.run_polling()


if __name__ == "__main__":
    import os
    
    # For testing, you can hardcode the token:
    # BOT_TOKEN = "YOUR_TOKEN_HERE"
    
    # Or load from environment variable:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("Missing TELEGRAM_BOT_TOKEN")
        exit(1)

    bot = TelegramInfoBot(BOT_TOKEN)
    bot.run()
