import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ------------------------------------------------------------------
# 1. Environment
# ------------------------------------------------------------------
load_dotenv()                               # reads .env if running locally
TOKEN: str = os.getenv("TELEGRAM_TOKEN")    # must be set in Render
PORT: int = int(os.getenv("PORT", "8080"))  # Render supplies $PORT
WEBHOOK_URL: str = os.getenv("WEBHOOK_URL")  # e.g. https://botshare.onrender.com/

if not TOKEN or not WEBHOOK_URL:
    raise RuntimeError("TELEGRAM_TOKEN or WEBHOOK_URL is missing.")

# ------------------------------------------------------------------
# 2. Handlers
# ------------------------------------------------------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🚀 BOTSHARE online!  /help for commands")

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("/start – greet\n/help – this message")

# ------------------------------------------------------------------
# 3. Main entry
# ------------------------------------------------------------------
def main() -> None:
    # Create application WITHOUT polling/updater
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # Register commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    # Start webhook server (Render detects the bound $PORT)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,           # Telegram will push updates here
        allowed_updates=Update.ALL_TYPES,  # receive all update types
    )

if __name__ == "__main__":
    main()
