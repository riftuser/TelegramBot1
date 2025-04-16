import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

ADMIN_ID = 7631211375  # YOUR ADMIN ID
CREATOR_ID = 8066177203  # BOT CREATOR ID
BOT_TOKEN = "7358736845:AAG_gyss5hs_ac8XYqIZYWRwcZoKfcDzXcA"  # YOUR BOT TOKEN

# Database: {category: {link_number: message}}
database = {
    "WarZone": {1: "https://example.com/warzone1"},
    "NL Topics": {1: "https://example.com/nltopics1"},
    "Cams": {1: "https://example.com/cams1"},
}

# --- BUTTONS LAYOUT (2 per row) ---
def get_main_menu_buttons():
    return [
        [InlineKeyboardButton("🔥 WarZone", callback_data="WarZone")],
        [InlineKeyboardButton("📚 NL Topics", callback_data="NL Topics")],
        [InlineKeyboardButton("📹 Cams", callback_data="Cams")],
        [InlineKeyboardButton("🌐 Languages", callback_data="Languages")],
        [InlineKeyboardButton("💬 Support Us", callback_data="Support"), 
         InlineKeyboardButton("📞 Contact Us", callback_data="Contact")]
    ]

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(get_main_menu_buttons())
    await update.message.reply_text(
        "🔍 **Choose a category:**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# --- BUTTON CLICK HANDLER ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        await start(update, context)
        return
    
    category = query.data
    
    if category in database:
        links = database[category]
        message = f"🔗 **{category} Links:**\n\n" + "\n".join(
            [f"{num}. {text}" for num, text in links.items()]
        )
    elif category == "Support":
        message = "💸 **Support us:**\nhttps://example.com/donate"
    elif category == "Contact":
        message = "📩 **Contact:**\n@YourUsername"
    else:
        message = "❌ No links available yet."
    
    back_button = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(back_button),
        parse_mode="Markdown"
    )

# --- ADD COMMAND (NOW ACCEPTS SPACES) ---
async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: `/add category message_with_spaces`")
        return
    
    category = context.args[0]
    message = " ".join(context.args[1:])  # Joins ALL remaining words
    
    if not message:  # If no message provided
        await update.message.reply_text("❌ Please include a message/link!")
        return
    
    if category not in database:
        database[category] = {}
    
    link_number = len(database[category]) + 1
    database[category][link_number] = message
    
    await update.message.reply_text(
        f"✅ Added to **{category}** as link #{link_number}",
        parse_mode="Markdown"
    )

# --- UPDATE COMMAND ---
async def update_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text("❌ Usage: `/update category link_number new_message`")
        return
    
    category = context.args[0]
    link_number = int(context.args[1])
    new_message = " ".join(context.args[2:])
    
    if category not in database or link_number not in database[category]:
        await update.message.reply_text("❌ Invalid category/link!")
        return
    
    database[category][link_number] = new_message
    await update.message.reply_text(f"✅ Updated **{category}** link #{link_number}", parse_mode="Markdown")

# --- REMOVE COMMAND ---
async def remove_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/remove category link_number`")
        return
    
    category = context.args[0]
    link_number = int(context.args[1])
    
    if category not in database or link_number not in database[category]:
        await update.message.reply_text("❌ Invalid category/link!")
        return
    
    del database[category][link_number]
    await update.message.reply_text(f"✅ Removed **{category}** link #{link_number}", parse_mode="Markdown")

# --- RUN BOT ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(CommandHandler("add", add_category))
    app.add_handler(CommandHandler("update", update_link))
    app.add_handler(CommandHandler("remove", remove_link))
    
    app.run_polling()

if __name__ == "__main__":
    main()