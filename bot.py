import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

ADMIN_ID = 7631211375
CREATOR_ID = 8066177203
BOT_TOKEN = "7358736845:AAG_gyss5hs_ac8XYqIZYWRwcZoKfcDzXcA"

database = {
    "WarZone": {1: "WarZone link 1"},
    "NL Topics": {1: "NL Topics link 1"},
    "Cams": {1: "Cams link 1"},
    "Languages": {1: "Languages link 1"},
    "Candids": {1: "Candids link 1"},
    "Captions": {1: "Captions link 1"},
    "Fetishes": {1: "Fetishes link 1"},
    "Anime": {1: "Anime link 1"},
    "Verified Teen Sellers": {1: "Verified Teen Sellers link 1"},
    "Megas": {1: "Megas link 1"},
    "Games": {1: "Games link 1"},
    "Lives": {1: "Lives link 1"},
    "How to Open Links": {1: "How to Open Links info"}
}

def create_menu():
    return [
        [InlineKeyboardButton("WarZone", callback_data="WarZone"), 
         InlineKeyboardButton("NL Topics", callback_data="NL Topics")],
        [InlineKeyboardButton("Cams", callback_data="Cams"), 
         InlineKeyboardButton("Languages", callback_data="Languages")],
        [InlineKeyboardButton("Candids", callback_data="Candids"), 
         InlineKeyboardButton("Captions", callback_data="Captions")],
        [InlineKeyboardButton("Fetishes", callback_data="Fetishes"), 
         InlineKeyboardButton("Anime", callback_data="Anime")],
        [InlineKeyboardButton("Verified Teen Sellers", callback_data="Verified Teen Sellers"), 
         InlineKeyboardButton("Megas", callback_data="Megas")],
        [InlineKeyboardButton("Games", callback_data="Games"), 
         InlineKeyboardButton("Lives", callback_data="Lives")],
        [InlineKeyboardButton("How to Open Links", callback_data="How to Open Links"), 
         InlineKeyboardButton("Support Us", callback_data="Support")],
        [InlineKeyboardButton("Contact Us", callback_data="Contact")]
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose a category or option:",
        reply_markup=InlineKeyboardMarkup(create_menu())
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        await start(update, context)
        return
    
    if query.data in ["Support", "Contact"]:
        message = "Support Us" if query.data == "Support" else "Contact Us"
        await query.edit_message_text(
            text=f"*{message}* info will be here",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
        )
        return
    
    if query.data in database:
        links = database[query.data]
        message = f"*{query.data} Links:*\n\n" + "\n".join(
            [f"{num}. {text}" for num, text in links.items()]
        )
        await query.edit_message_text(
            text=message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
        )

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /add category *bold_text* normal_text")
        return
    
    category = context.args[0]
    message = " ".join(context.args[1:])
    
    if category not in database:
        database[category] = {}
    
    link_number = len(database[category]) + 1
    database[category][link_number] = message
    
    await update.message.reply_text(
        f"✅ Added to *{category}* as link #{link_number}",
        parse_mode="Markdown"
    )

# (Keep update_link and remove_link functions from previous version)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CommandHandler("add", add_category))
    # (Add other command handlers)
    app.run_polling()

if __name__ == "__main__":
    main()