import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# CONFIG
BOT_TOKEN = "7239607925:AAGYq1zt1NOw4vW3VnDa5SSJIQiifvimeBk"
ADMIN_ID = 7631211375
CREATOR_ID = 8066177203

# DATABASE
database = {
    "nltopics": {1: "NL Link 1", 2: "NL Link 2"},
    "languages": {1: "Language Link 1"},
    "fetishes": {1: "Fetish Link 1"},
    "anime": {1: "Anime Link 1"},
    "megas": {1: "Mega Link 1"},
    "lives": {1: "Live Link 1"},
    "howto": {1: "• HOW TO OPEN LINKS •\n1. Click 'Watch Video'\n2. Wait 30 sec\n3. Enjoy content"}
}

contact_mode_users = set()

# MENU CREATION WITH BIGGER BUTTONS AND PROPER ALIGNMENT
def create_menu():
    return [
        # First row - 2 big buttons
        [InlineKeyboardButton("📚 NL TOPICS", callback_data="nltopics", width=10), 
         InlineKeyboardButton("🌐 LANGUAGES", callback_data="languages", width=10)],
        
        # Second row - 2 big buttons
        [InlineKeyboardButton("🎭 FETISHES", callback_data="fetishes", width=10), 
         InlineKeyboardButton("🇯🇵 ANIME", callback_data="anime", width=10)],
        
        # Third row - 2 big buttons
        [InlineKeyboardButton("💾 MEGAS", callback_data="megas", width=10), 
         InlineKeyboardButton("🔴 LIVES", callback_data="lives", width=10)],
        
        # Fourth row - Single centered button (How To)
        [InlineKeyboardButton("❓ HOW TO OPEN LINKS", callback_data="howto", width=20)],
        
        # Fifth row - Single centered button (Help Us)
        [InlineKeyboardButton("🔄 HELP US (SHARE)", url="https://t.me/share/url?url=https://t.me/The0LinkerBot", width=20)],
        
        # Sixth row - Single centered button (Contact)
        [InlineKeyboardButton("📩 CONTACT SUPPORT", callback_data="contact", width=20)]
    ]

# COMMAND HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(create_menu())
    if update.message:
        await update.message.reply_text("🔻 MAIN MENU 🔻", reply_markup=keyboard)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("🔻 MAIN MENU 🔻", reply_markup=keyboard)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⚡")  # Button click animation
    
    if query.data == "howto":
        await query.edit_message_text(
            text=database["howto"][1],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back", width=20)]])
        )
    elif query.data == "contact":
        contact_mode_users.add(query.from_user.id)
        await query.edit_message_text(
            text="✉️ CONTACT OUR TEAM @YourSupport\n\nSend /cancel to exit",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back", width=20)]])
        )
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
            await update.message.reply_text("❌ CANCELLED")
            return
            
        await context.bot.send_message(
            chat_id=CREATOR_ID,
            text=f"📩 NEW MESSAGE FROM {update.message.from_user.id}:\n\n{update.message.text}"
        )
        contact_mode_users.remove(update.message.from_user.id)
        await update.message.reply_text("✅ MESSAGE SENT TO SUPPORT")

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
        await update.message.reply_text("❌ INVALID CODE! USE: nl, la, fe, an, me, li, ho")
        return
    
    category = code_map[code]
    link = " ".join(context.args[1:])
    new_id = max(database[category].keys(), default=0) + 1
    database[category][new_id] = link
    
    await update.message.reply_text(f"✅ ADDED TO {category.upper()} AS #{new_id}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_link))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact))
    
    print("🤖 BOT STARTED - ALL BUTTONS WORKING")
    app.run_polling()

if __name__ == "__main__":
    main()