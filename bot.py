#!/usr/bin/env python3
"""
Fixed Telegram Forward Info Bot
- Handles all message types safely
- Includes /myid command
- Robust error handling
"""

import logging
from datetime import datetime
from telegram import Update, Message
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

class SafeForwardBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(self.token).build()
        
        # Safe handler registration
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("myid", self.myid))
        self.app.add_handler(MessageHandler(filters.ALL, self.handle_message))  # Changed to ALL

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔍 Send or forward any message to get info\n"
            "🆔 Use /myid to see your own ID"
        )

    async def myid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(
            f"🆔 <b>Your ID</b>: <code>{user.id}</code>\n"
            f"👤 <b>Username</b>: @{user.username if user.username else 'N/A'}",
            parse_mode="HTML"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        try:
            # Safely check forwarding attributes
            if hasattr(msg, 'forward_from'):
                await self.handle_forwarded_user(msg)
            elif hasattr(msg, 'forward_from_chat'):
                await self.handle_forwarded_chat(msg)
            elif hasattr(msg, 'forward_sender_name'):
                await self.handle_private_forward(msg)
            else:
                await msg.reply_text("ℹ️ Send me a forwarded message to get info")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await msg.reply_text("⚠️ Error processing message")

    async def handle_forwarded_user(self, msg: Message):
        """Handle messages forwarded from users"""
        user = msg.forward_from
        await msg.reply_text(
            f"👤 <b>User Info</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"└ Username: @{user.username if user.username else 'N/A'}",
            parse_mode="HTML"
        )

    async def handle_forwarded_chat(self, msg: Message):
        """Handle messages forwarded from chats/channels"""
        chat = msg.forward_from_chat
        await msg.reply_text(
            f"📢 <b>Chat Info</b>\n"
            f"├ ID: <code>{chat.id}</code>\n"
            f"└ Title: {chat.title}",
            parse_mode="HTML"
        )

    async def handle_private_forward(self, msg: Message):
        """Handle privacy-protected forwards"""
        await msg.reply_text(
            f"👤 <b>Forwarded from</b>: {msg.forward_sender_name}\n"
            f"🕒 <b>Date</b>: {msg.forward_date.strftime('%Y-%m-%d %H:%M')}\n"
            "⚠️ More info hidden by privacy settings",
            parse_mode="HTML"
        )

    def run(self):
        logger.info("Starting safe forward bot...")
        self.app.run_polling()

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "your tokenTOKEN"
    bot = SafeForwardBot(TOKEN)
    bot.run()
