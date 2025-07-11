"""
BOTSHARE • минимальный Telegram-бот (webhook only) + /price
Тестировалось с:
  python-telegram-bot[webhooks] == 20.8   (тянет httpx 0.26.x)
  httpx ~= 0.26.0
  Python 3.11
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
import httpx  # <= 0.26.x

# -----------------------------------------------------------
# 1. Базовая настройка и переменные окружения
# -----------------------------------------------------------
load_dotenv()  # локальная разработка читает .env

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")           # https://*.onrender.com/
PORT = int(os.getenv("PORT", "8080"))            # Render передаёт $PORT

if not (TOKEN and WEBHOOK_URL):
    raise RuntimeError("TELEGRAM_TOKEN или WEBHOOK_URL не заданы.")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

# -----------------------------------------------------------
# 2. Хендлеры команд
# -----------------------------------------------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 BOTSHARE online!\n"
        "Команды:\n"
        "  /price [TICKER] – цена токена (по умолчанию SOL)\n"
        "  /help – справка"
    )


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start – приветствие\n"
        "/price [TICKER] – цена токена в USDC"
    )

async def price(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /price [TICKER]
    Показывает цену токена в USDC через CoinGecko.
    Поддерживаемые тикеры: SOL, JUP, ETH.
    """
    # 1) Получаем тикер из аргументов
    token = ctx.args[0].upper() if ctx.args else "SOL"

    # 2) Сопоставляем с CoinGecko ID
    id_map = {
        "SOL": "solana",
        "JUP": "jupiter",
        "ETH": "ethereum",
    }
    cg_id = id_map.get(token)
    if not cg_id:
        await update.message.reply_text(
            f"⚠️ Неподдерживаемый тикер '{token}'.\n"
            "Поддерживаем: " + ", ".join(id_map.keys())
        )
        return

    # 3) Делаем запрос к CoinGecko
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        logging.warning("CoinGecko API error: %s", e)
        await update.message.reply_text("⚠️ API недоступен, попробуйте позже.")
        return

    # 4) Извлекаем цену и отвечаем
    price_usd = data[cg_id]["usd"]
    await update.message.reply_text(f"1 {token} ≈ {price_usd:,.2f} USD")



# -----------------------------------------------------------
# 3. Точка входа
# -----------------------------------------------------------
def main() -> None:
    logging.info("Launching BOTSHARE…")
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()                       # Updater создаётся автоматически
    )

    # регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("price", price))

    logging.info("Starting webhook on port %s", PORT)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()

