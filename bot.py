import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Config (set these in Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CREATOR_ID = int(os.getenv("CREATOR_ID"))

# Database with your structure
database = {
    "nltopics": {},
    "languages": {},
    "fetishes": {},
    "anime": {},
    "megas": {},
    "lives": {},
    "howto": {}
}

contact_mode_users = set()

def create_menu():
    return [
        [InlineKeyboardButton("📚 NL Topics", callback_data="nltopics"), 
         InlineKeyboardButton("🌐 Languages", callback_data="languages")],
        [InlineKeyboardButton("🎭 Fetishes", callback_data="fetishes"), 
         InlineKeyboardButton("🇯🇵 Anime", callback_data="anime")],
        [InlineKeyboardButton("💾 Megas", callback_data="megas"), 
         InlineKeyboardButton("🔴 Lives", callback_data="lives")],
        [InlineKeyboardButton("❓ How to Open Links", callback_data="howto")],
        [InlineKeyboardButton("📩 Contact Support", callback_data="contact")]
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(create_menu())
    await update.message.reply_text("🔻 Choose option:", reply_markup=keyboard)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⚡")
    
    if query.data == "howto":
        await query.edit_message_text("Guide to open links...", 
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
    elif query.data == "contact":
        contact_mode_users.add(query.from_user.id)
        await query.edit_message_text("Describe your issue...",
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
    elif query.data in database:
        links = database[query.data]
        await query.delete_message()
        for num, text in links.items():
            await context.bot.send_message(chat_id=query.message.chat_id, text=text)
            await asyncio.sleep(0.5)
    elif query.data == "back":
        await start(update, context)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id in contact_mode_users:
        if update.message.text == "/cancel":
            contact_mode_users.remove(update.message.from_user.id)
            await update.message.reply_text("Cancelled")
            return
            
        await context.bot.send_message(
            chat_id=CREATOR_ID,
            text=f"New message from {update.message.from_user.id}:\n\n{update.message.text}"
        )
        await update.message.reply_text("Message sent to admin")
        contact_mode_users.remove(update.message.from_user.id)

async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add [code] [link]\nCodes: nl, la, fe, an, me, li, ho")
        return
    
    code_map = {
        "nl": "nltopics",
        "la": "languages",
        "fe": "fetishes",
        "an": "anime",
        "me": "megas",
        "li": "lives",
        "ho": "howto"
    }
    
    code = context.args[0].lower()
    if code not in code_map:
        await update.message.reply_text("Invalid code! Use: nl, la, fe, an, me, li, ho")
        return
    
    category = code_map[code]
    link = " ".join(context.args[1:])
    new_id = max(database[category].keys(), default=0) + 1
    database[category][new_id] = link
    
    await update.message.reply_text(f"✅ Added to {category} as #{new_id}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_link))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact))
    app.run_polling()

if __name__ == "__main__":
    main()