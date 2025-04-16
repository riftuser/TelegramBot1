import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# CONFIG (YOUR DETAILS)
BOT_TOKEN = "7239607925:AAGYq1zt1NOw4vW3VnDa5SSJIQiifvimeBk"  # YOUR TOKEN
ADMIN_ID = 7631211375  # YOUR ADMIN ID
CREATOR_ID = 8066177203  # YOUR CREATOR ID

# Database with sample links
database = {
    "nltopics": {
        1: "https://example.com/nl1",
        2: "https://example.com/nl2"
    },
    "languages": {
        1: "https://example.com/lang1",
        2: "https://example.com/lang2"
    },
    "fetishes": {
        1: "https://example.com/fetish1"
    },
    "megas": {
        1: "https://example.com/mega1"
    },
    "howto": {
        1: "• HOW TO OPEN LINKS •\n\n1. Click 'Watch Video'\n2. Wait 30 sec\n3. Links will unlock"
    }
}

def create_menu():
    """Create 2x2 menu with single bottom button"""
    return [
        # First row - 2 buttons
        [InlineKeyboardButton("NL TOPICS", callback_data="nltopics"), 
         InlineKeyboardButton("LANGUAGES", callback_data="languages")],
        
        # Second row - 2 buttons
        [InlineKeyboardButton("FETISHES", callback_data="fetishes"), 
         InlineKeyboardButton("MEGAS", callback_data="megas")],
        
        # Third row - 1 button (centered)
        [InlineKeyboardButton("HOW TO OPEN", callback_data="howto")],
        
        # Fourth row - 1 button (contact only)
        [InlineKeyboardButton("CONTACT SUPPORT", callback_data="contact")],
        
        # Fifth row - 1 button (help us with share)
        [InlineKeyboardButton("HELP US (SHARE)", url="https://t.me/share/url?url=https://t.me/The0LinkerBot")]
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    keyboard = InlineKeyboardMarkup(create_menu())
    if update.message:
        await update.message.reply_text(
            "🔻 SELECT CATEGORY 🔻",
            reply_markup=keyboard
        )
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text="🔻 SELECT CATEGORY 🔻",
            reply_markup=keyboard
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer("⚡")  # Button click animation
    
    if query.data == "howto":
        guide = database["howto"][1]
        await query.edit_message_text(
            text=guide,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    elif query.data == "contact":
        await query.edit_message_text(
            text="📩 Contact our team at @YourSupport\n\nSend /cancel to exit",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back")]])
        )
    elif query.data in database:
        links = database[query.data]
        # Delete category message first
        await query.delete_message()
        # Send links one by one
        for num, link in links.items():
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=link
            )
            await asyncio.sleep(0.5)  # Delay between messages
    elif query.data == "back":
        await start(update, context)

async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add links"""
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add CATEGORY LINK")
        return
    
    category = context.args[0].lower()
    if category not in database:
        await update.message.reply_text("Invalid category! Use: nltopics, languages, fetishes, megas")
        return
    
    link = " ".join(context.args[1:])
    new_id = max(database[category].keys(), default=0) + 1
    database[category][new_id] = link
    
    await update.message.reply_text(f"✅ Added to {category.upper()} as link #{new_id}")

def main():
    """Start the bot"""
    print("🟢 BOT STARTED - PRESS CTRL+C TO STOP")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_link))
    
    # Add button handler
    app.add_handler(CallbackQueryHandler(button_click))
    
    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()