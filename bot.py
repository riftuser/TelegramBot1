import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

ADMIN_ID = 7631211375
CREATOR_ID = 8066177203
BOT_TOKEN = "7239607925:AAGYq1zt1NOw4vW3VnDa5SSJIQiifvimeBk"

database = {
    "NL Topics": {},
    "Languages": {},
    "Fetishes": {},
    "Anime": {},
    "Megas": {},
    "Lives": {},
    "How to Open Links": {}
}

contact_mode_users = set()

def create_menu():
    return [
        [InlineKeyboardButton("📚 NL Topics", callback_data="NL Topics"), 
         InlineKeyboardButton("🌐 Languages", callback_data="Languages")],
        [InlineKeyboardButton("🎭 Fetishes", callback_data="Fetishes"), 
         InlineKeyboardButton("🇯🇵 Anime", callback_data="Anime")],
        [InlineKeyboardButton("💾 Megas", callback_data="Megas"), 
         InlineKeyboardButton("🔴 Lives", callback_data="Lives")],
        [InlineKeyboardButton("❓ How to Open Links", callback_data="How to Open Links")],
        [InlineKeyboardButton("📩 Contact Support", callback_data="Contact")],
        [InlineKeyboardButton("📢 Share Bot", url="https://t.me/share/url?url=https://t.me/The0LinkerBot")]
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "🔹 Choose an option:",
            reply_markup=InlineKeyboardMarkup(create_menu())
        )
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "🔹 Choose an option:",
            reply_markup=InlineKeyboardMarkup(create_menu())
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "How to Open Links":
        tutorial = """🔐 Access Guide:
1. Select 'View Content' option
2. Let the preview load completely
3. Return to previous screen
4. Wait 30 seconds for verification"""
        await query.edit_message_text(
            text=tutorial,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )
    elif query.data == "Contact":
        contact_msg = """✉️ Support Ticket\n\nDescribe your issue in detail.\nWe'll respond within 24 hours.\n\nType /cancel to abort"""
        contact_mode_users.add(query.from_user.id)
        await query.edit_message_text(
            text=contact_msg,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )
    elif query.data in database:
        links = database[query.data]
        for num, text in links.items():
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=text,
                parse_mode="Markdown"
            )
        await query.edit_message_text(
            text=f"🔗 Sent {len(links)} {query.data} links",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )
    elif query.data == "back":
        await start(update, context)

async def handle_contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id in contact_mode_users:
        if update.message.text == "/cancel":
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
        await update.message.reply_text("Usage: /add category message")
        return
    
    category = context.args[0]
    message = " ".join(context.args[1:])
    
    if category not in database:
        await update.message.reply_text("Invalid category!")
        return
    
    link_number = len(database[category]) + 1
    database[category][link_number] = message
    await update.message.reply_text(f"Added to {category} as link #{link_number}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", lambda u,c: contact_mode_users.discard(u.message.from_user.id)))
    app.add_handler(CommandHandler("send", send_to_user))
    app.add_handler(CommandHandler("add", add_category))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()