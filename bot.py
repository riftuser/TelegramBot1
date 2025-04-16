import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = 7631211375  # Your admin ID
CREATOR_ID = 8066177203  # Bot creator ID
BOT_TOKEN = "7358736845:AAG_gyss5hs_ac8XYqIZYWRwcZoKfcDzXcA"  # Your bot token

# Database: {category: {link_number: message}}
database = {
    "WarZone": {1: "WarZone link 1", 2: "WarZone link 2"},
    "NL Topics": {1: "NL Topics link 1"},
    "Cams": {1: "Cams link 1"},
    # Add more categories here
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("WarZone", callback_data="WarZone"), InlineKeyboardButton("NL Topics", callback_data="NL Topics")],
        [InlineKeyboardButton("Cams", callback_data="Cams"), InlineKeyboardButton("Languages", callback_data="Languages")],
        [InlineKeyboardButton("Candids", callback_data="Candids"), InlineKeyboardButton("Captions", callback_data="Captions")],
        [InlineKeyboardButton("Support Us 💬", callback_data="Support"), InlineKeyboardButton("Contact Us 💬", callback_data="Contact")]
    ]
    await update.message.reply_text("Choose a category:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category = query.data
    
    if category in database:
        links = database[category]
        message = f"{category} links:\n\n" + "\n".join([f"{num}. {text}" for num, text in links.items()])
    elif category == "Support":
        message = "Support us by donating..."
    elif category == "Contact":
        message = "Contact us at @username"
    else:
        message = "No links available yet."
    
    await query.answer()
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]]))

async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("❌ No permission!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/add category_name message`")
        return
    
    category = context.args[0]
    message = " ".join(context.args[1:])
    
    if category not in database:
        database[category] = {}
    
    link_number = len(database[category]) + 1
    database[category][link_number] = message
    await update.message.reply_text(f"✅ Added to {category} (Link #{link_number})")

async def update_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("❌ No permission!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text("Usage: `/update category link_number new_message`")
        return
    
    category, link_num, *new_msg = context.args
    if category not in database or not link_num.isdigit() or int(link_num) not in database[category]:
        await update.message.reply_text("❌ Invalid category/link!")
        return
    
    database[category][int(link_num)] = " ".join(new_msg)
    await update.message.reply_text(f"✅ Updated {category} (Link #{link_num})")

async def remove_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("❌ No permission!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/remove category link_number`")
        return
    
    category, link_num = context.args
    if category not in database or not link_num.isdigit() or int(link_num) not in database[category]:
        await update.message.reply_text("❌ Invalid category/link!")
        return
    
    del database[category][int(link_num)]
    await update.message.reply_text(f"✅ Removed {category} (Link #{link_num})")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click, pattern="^(?!back).*$"))
    app.add_handler(CallbackQueryHandler(back_button, pattern="^back$"))
    app.add_handler(CommandHandler("add", add_category))
    app.add_handler(CommandHandler("update", update_link))
    app.add_handler(CommandHandler("remove", remove_link))
    app.run_polling()

if __name__ == "__main__":
    main()