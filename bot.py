import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# CONFIG (USE YOUR EXACT DETAILS)
ADMIN_ID = 7631211375  # Your admin ID
CREATOR_ID = 8066177203  # Your creator ID
BOT_TOKEN = "7239607925:AAGYq1zt1NOw4vW3VnDa5SSJIQiifvimeBk"  # YOUR EXACT TOKEN

# Database
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
        [InlineKeyboardButton("❓ How To Open Links", callback_data="howto")],
        [InlineKeyboardButton("📩 Contact Support", callback_data="contact")],
        [InlineKeyboardButton("📢 Share Bot", url="https://t.me/share/url?url=https://t.me/The0LinkerBot")]
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(create_menu())
    if update.message:
        await update.message.reply_text("🔹 Choose an option:", reply_markup=keyboard)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("🔹 Choose an option:", reply_markup=keyboard)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("⚡")
    
    if query.data == "howto":
        tutorial = """🔐 Access Guide:
1. Select 'View Content'
2. Let it load completely
3. Return to previous screen
4. Wait 30 seconds"""
        await query.edit_message_text(tutorial, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
    elif query.data == "contact":
        contact_msg = """✉️ Support Ticket\n\nDescribe your issue.\nWe'll respond within 24h.\n\n/cancel to abort"""
        contact_mode_users.add(query.from_user.id)
        await query.edit_message_text(contact_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
    elif query.data in database:
        links = database[query.data]
        if links:
            await query.edit_message_text(f"📤 Sending {len(links)} links...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
            for num, text in links.items():
                await asyncio.sleep(0.3)
                await context.bot.send_message(chat_id=query.message.chat_id, text=text, parse_mode="Markdown")
        else:
            await query.edit_message_text(f"❌ No links available", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]]))
    elif query.data == "back":
        await start(update, context)

async def handle_contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id in contact_mode_users:
        if update.message.text.lower() == "/cancel":
            contact_mode_users.remove(update.message.from_user.id)
            await update.message.reply_text("❌ Ticket canceled")
            return
            
        user = update.message.from_user
        message = f"📩 New Ticket:\nFrom: @{user.username}\nID: {user.id}\n\n{update.message.text}"
        await context.bot.send_message(chat_id=CREATOR_ID, text=message)
        contact_mode_users.remove(update.message.from_user.id)
        await update.message.reply_text("✅ Ticket submitted!")

async def send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /send userid message")
        return
    
    try:
        user_id = int(context.args[0])
        message = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text("✅ Message sent!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add category_key message\nKeys: nl, la, fe, an, me, li, ho")
        return
    
    cat_map = {
        "nl": "nltopics",
        "la": "languages",
        "fe": "fetishes",
        "an": "anime",
        "me": "megas",
        "li": "lives",
        "ho": "howto"
    }
    
    cat_key = context.args[0].lower()
    if cat_key not in cat_map:
        await update.message.reply_text("❌ Invalid key. Use: nl, la, fe, an, me, li, ho")
        return
    
    category = cat_map[cat_key]
    message = " ".join(context.args[1:])
    link_number = len(database[category]) + 1
    database[category][link_number] = message
    
    await update.message.reply_text(f"✅ Added to {category} as link #{link_number}")

def main():
    print("🔥 STARTING BOT WITH YOUR TOKEN 🔥")
    print(f"Token: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:]}")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("cancel", lambda u,c: contact_mode_users.discard(u.message.from_user.id)))
        app.add_handler(CommandHandler("send", send_to_user))
        app.add_handler(CommandHandler("add", add_category))
        app.add_handler(CallbackQueryHandler(button_click))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message))
        
        print("✅ BOT IS RUNNING! Send /start to test")
        app.run_polling()
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        print("CHECK YOUR TOKEN OR SERVER CONNECTION")

if __name__ == "__main__":
    main()