import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

ADMIN_ID = 7631211375
CREATOR_ID = 8066177203
BOT_TOKEN = "7358736845:AAG_gyss5hs_ac8XYqIZYWRwcZoKfcDzXcA"

# Empty database
database = {
    "WarZone": {},
    "NL Topics": {},
    "Cams": {},
    "Languages": {},
    "Candids": {},
    "Captions": {},
    "Fetishes": {},
    "Anime": {},
    "Verified Teen Sellers": {},
    "Megas": {},
    "Games": {},
    "Lives": {},
    "How to Open Links": {}
}

# Track users in contact mode
contact_mode_users = set()

def create_menu():
    return [
        [InlineKeyboardButton("🔥 WarZone", callback_data="WarZone"), 
         InlineKeyboardButton("📚 NL Topics", callback_data="NL Topics")],
        [InlineKeyboardButton("📹 Cams", callback_data="Cams"), 
         InlineKeyboardButton("🌐 Languages", callback_data="Languages")],
        [InlineKeyboardButton("📸 Candids", callback_data="Candids"), 
         InlineKeyboardButton("✏️ Captions", callback_data="Captions")],
        [InlineKeyboardButton("🎭 Fetishes", callback_data="Fetishes"), 
         InlineKeyboardButton("🇯🇵 Anime", callback_data="Anime")],
        [InlineKeyboardButton("👧 Verified Teen Sellers", callback_data="Verified Teen Sellers"), 
         InlineKeyboardButton("💾 Megas", callback_data="Megas")],
        [InlineKeyboardButton("🎮 Games", callback_data="Games"), 
         InlineKeyboardButton("🔴 Lives", callback_data="Lives")],
        [InlineKeyboardButton("❓ How to Open Links", callback_data="How to Open Links"), 
         InlineKeyboardButton("💬 Support Us", callback_data="Support")],
        [InlineKeyboardButton("📝 Contact Us", callback_data="Contact")]
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Choose a category or option:",
            reply_markup=InlineKeyboardMarkup(create_menu())
        )
    else:  # For callback queries
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "Choose a category or option:",
            reply_markup=InlineKeyboardMarkup(create_menu())
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "How to Open Links":
        tutorial = """• 📖 Tutorial to open Best Links:

1️⃣ Click on Watch a Video
2️⃣ Fast forward the video a bit
3️⃣ Return to the main page
4️⃣ Wait for half a minute to turn it into green, there you go! ✅

⚠️ Use a VPN if you get any other bad task!"""
        await query.edit_message_text(
            text=tutorial,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
    elif query.data == "Contact":
        contact_msg = """📝 Contact Us 📝

Write down your inquiry in one full message and send it. It'll be forwarded to our team!
Send /cancel to end the task"""
        contact_mode_users.add(query.from_user.id)
        await query.edit_message_text(
            text=contact_msg,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
    elif query.data in database:
        links = database[query.data]
        if links:
            message = f"🔗 {query.data} Links:\n\n" + "\n".join(
                [f"{num}. {text}" for num, text in links.items()]
            )
        else:
            message = f"No links available for {query.data} yet."
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
        )
    elif query.data == "back":
        await start(update, context)

async def handle_contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id in contact_mode_users:
        user = update.message.from_user
        message = f"📨 New Contact Message from {user.username or user.first_name} (ID: {user.id}):\n\n{update.message.text}"
        
        # Forward to creator
        await context.bot.send_message(chat_id=CREATOR_ID, text=message)
        
        await update.message.reply_text("✅ Your message has been forwarded to our team!")
        contact_mode_users.remove(update.message.from_user.id)

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /add category message (supports *bold* formatting)")
        return
    
    category = context.args[0]
    message = " ".join(context.args[1:])
    
    if category not in database:
        await update.message.reply_text("❌ Invalid category!")
        return
    
    link_number = len(database[category]) + 1
    database[category][link_number] = message
    
    await update.message.reply_text(
        f"✅ Added to *{category}* as link #{link_number}",
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CommandHandler("add", add_category))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()