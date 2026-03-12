import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"]  # Your Vercel URL e.g. https://infinite-craft.vercel.app
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

import httpx

async def supabase_get(path: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{SUPABASE_URL}/rest/v1/{path}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            timeout=10,
        )
        return res.json() if res.status_code == 200 else []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [[
        InlineKeyboardButton(
            "🧪 Play Infinite Craft",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Hey {user.first_name}!\n\n"
        "Welcome to *Infinite Craft* — the element combining game!\n\n"
        "🌍 Start with Earth, Water, Fire & Wind\n"
        "⚗️ Combine elements to discover new ones\n"
        "🌟 Be the first to discover rare elements\n"
        "🏆 Climb the global leaderboard!\n\n"
        "Tap the button below to start playing 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await supabase_get(
        "user_elements?select=telegram_id,users(username)&limit=1000"
    )
    # Count per user
    counts = {}
    for row in data:
        uid = row.get("telegram_id")
        uname = row.get("users", {}).get("username", "Unknown") if isinstance(row.get("users"), dict) else "Unknown"
        if uid not in counts:
            counts[uid] = {"username": uname, "count": 0}
        counts[uid]["count"] += 1

    sorted_users = sorted(counts.values(), key=lambda x: x["count"], reverse=True)[:10]

    if not sorted_users:
        await update.message.reply_text("No players yet! Be the first to play 🎮")
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 *Global Leaderboard*\n"]
    for i, u in enumerate(sorted_users):
        medal = medals[i] if i < 3 else f"#{i+1}"
        lines.append(f"{medal} @{u['username']} — *{u['count']}* elements")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def discoveries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = await supabase_get(
        f"user_elements?telegram_id=eq.{user.id}&select=element_name"
    )
    count = len(data)
    first = await supabase_get(
        f"first_discoveries?telegram_id=eq.{user.id}&select=element_name"
    )
    first_count = len(first)

    keyboard = [[
        InlineKeyboardButton("🧪 Keep Playing", web_app=WebAppInfo(url=WEBAPP_URL))
    ]]

    await update.message.reply_text(
        f"🧪 *Your Discoveries*\n\n"
        f"Total elements: *{count}*\n"
        f"First discoveries: *{first_count}* 🌟\n\n"
        f"{'Great job!' if count > 20 else 'Keep combining to discover more!'}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🧪 Open Game", web_app=WebAppInfo(url=WEBAPP_URL))
    ]]
    await update.message.reply_text(
        "Tap below to open Infinite Craft! 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Infinite Craft Bot Commands*\n\n"
        "/start — Welcome + play button\n"
        "/play — Open the game\n"
        "/top — Global leaderboard\n"
        "/discoveries — Your stats\n"
        "/help — This message",
        parse_mode="Markdown",
    )


def main():
   await  app = Application.builder().token(BOT_TOKEN).build()
   await  app.add_handler(CommandHandler("start", start))
   await app.add_handler(CommandHandler("play", play))
   await app.add_handler(CommandHandler("top", top))
   await  app.add_handler(CommandHandler("discoveries", discoveries))
   await app.add_handler(CommandHandler("help", help_cmd))
    logger.info("Bot started...")
    app.run_polling(allowed_updates=Update.ALL_TYPES

if __name__ == "__main__":
    asyncio.run(main())main()
