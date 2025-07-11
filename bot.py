import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()                            
TOKEN = os.getenv("TELEGRAM_TOKEN")      

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 BOTSHARE online!")

def main():
    PORT = int(os.getenv("PORT", "8080"))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = (
        ApplicationBuilder()
        .token(TOKEN)
        .updater(None)        
        .build()
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
    )

if __name__ == "__main__":
    main()
