import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ======================
# CONFIGURATION
# ======================
BOT_TOKEN = "7239607925:AAGYq1zt1NOw4vW3VnDa5SSJIQiifvimeBk"  # YOUR BOT TOKEN
ADMIN_ID = 7631211375  # YOUR ADMIN USER ID
CREATOR_ID = 8066177203  # YOUR CREATOR USER ID

# ======================
# DATABASE SETUP
# ======================
database = {
    "nltopics": {
        1: "🔗 NL Topic Link 1: https://example.com/nl1",
        2: "🔗 NL Topic Link 2: https://example.com/nl2"
    },
    "languages": {
        1: "🔗 Language Link 1: https://example.com/lang1",
        2: "🔗 Language Link 2: https://example.com/lang2"
    },
    "fetishes": {
        1: "🔗 Fetish Link 1: https://example.com/fetish1",
        2: "🔗 Fetish Link 2: https://example.com/fetish2"
    },
    "anime": {
        1: "🔗 Anime Link 1: https://example.com/anime1"
    },
    "megas": {
        1: "🔗 Mega Link 1: https://example.com/mega1"
    },
    "lives": {
        1: "🔗 Live Link 1: https://example.com/live1"
    },
    "howto": {
        1: "• HOW TO OPEN LINKS •\n\n1. Click 'Watch Video'\n2. Wait 30 seconds\n3. Enjoy the content"
    }
}

contact_mode_users = set()

# ======================
# MENU SYSTEM
# ======================
def create_main_menu():
    """Create the main menu with 2x2 buttons and single bottom buttons"""
    return [
        [InlineKeyboardButton("📚 NL Topics", callback_data="nltopics"), 
         InlineKeyboardButton("🌐 Languages", callback_data="languages")],
        [InlineKeyboardButton("🎭 Fetishes", callback_data="fetishes"), 
         InlineKeyboardButton("🇯🇵 Anime", callback_data="anime")],
        [InlineKeyboardButton("💾 Megas", callback_data="megas"), 
         InlineKeyboardButton("🔴 Lives", callback_data="lives")],
        [InlineKeyboardButton("❓ How To Open Links", callback_data="howto")],
        [InlineKeyboardButton("🔄 Help Us", callback_data="help_menu")],
        [InlineKeyboardButton("📩 Contact Support", callback_data="contact")]
    ]

def create_help_menu():
    """Create the Help Us submenu"""
    return [
        [InlineKeyboardButton("📢 Share Bot", url="https://t.me/share/url?url=https://t.me/The0LinkerBot")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back")]
    ]

# ======================
# COMMAND HANDLERS
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    try:
        keyboard = InlineKeyboardMarkup(create_main_menu())
        if update.message:
            await update.message.reply_text(
                "🔻 MAIN MENU 🔻",
                reply_markup=keyboard
            )
        else:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(
                text="🔻 MAIN MENU 🔻",
                reply_markup=keyboard
            )
    except Exception as e:
        print(f"Start error: {e}")

async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command with 2-letter codes"""
    if update.message.from_user.id not in [ADMIN_ID, CREATOR_ID]:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add [code] [link]\nCodes: nl, la, fe, an, me, li, ho")
        return
    
    # 2-letter code mapping
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
        await update.message.reply_text("❌ Invalid code! Use: nl, la, fe, an, me, li, ho")
        return
    
    category = code_map[code]
    link = " ".join(context.args[1:])
    link_num = max(database[category].keys(), default=0) + 1
    database[category][link_num] = link
    
    await update.message.reply_text(f"✅ Added to {category} as link #{link_num}")

# ======================
# BUTTON HANDLERS
# ======================
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process all button clicks"""
    query = update.callback_query
    await query.answer("⚡")  # Button click animation
    
    try:
        if query.data == "help_menu":
            await show_help_menu(query)
        elif query.data == "howto":
            await show_howto_guide(query)
        elif query.data == "contact":
            await start_contact_mode(query)
        elif query.data in database:
            await send_category_links(query, context)
        elif query.data == "back":
            await return_to_main_menu(query)
    except Exception as e:
        print(f"Button error: {e}")

async def show_help_menu(query):
    """Display Help Us submenu"""
    keyboard = InlineKeyboardMarkup(create_help_menu())
    await query.edit_message_text(
        text="🔄 HELP US GROW:",
        reply_markup=keyboard
    )

async def show_howto_guide(query):
    """Display how-to guide"""
    guide = database["howto"][1]
    back_button = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    await query.edit_message_text(
        text=guide,
        reply_markup=InlineKeyboardMarkup(back_button)
    )

async def start_contact_mode(query):
    """Enter contact support mode"""
    contact_mode_users.add(query.from_user.id)
    back_button = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    await query.edit_message_text(
        text="✉️ CONTACT OUR TEAM:\n\nDescribe your issue...\n\nSend /cancel to exit",
        reply_markup=InlineKeyboardMarkup(back_button)
    )

async def send_category_links(query, context):
    """Send all links for a category one by one"""
    links = database[query.data]
    await query.delete_message()  # Remove the category selection message
    
    # Send each link with delay
    for num, link in links.items():
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=link
        )
        await asyncio.sleep(0.5)  # Prevent rate limiting
    
    # Send completion message
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"✅ Sent {len(links)} {query.data} links",
        reply_markup=keyboard
    )

async def return_to_main_menu(query):
    """Return to main menu"""
    keyboard = InlineKeyboardMarkup(create_main_menu())
    await query.edit_message_text(
        text="🔻 MAIN MENU 🔻",
        reply_markup=keyboard
    )

# ======================
# MESSAGE HANDLERS
# ======================
async def handle_contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process contact support messages"""
    if update.message.from_user.id not in contact_mode_users:
        return
    
    if update.message.text == "/cancel":
        contact_mode_users.remove(update.message.from_user.id)
        await update.message.reply_text("❌ Contact mode cancelled")
        return
    
    # Forward message to admin
    user = update.message.from_user
    forward_msg = f"📩 NEW SUPPORT MESSAGE:\nFrom: @{user.username}\nID: {user.id}\n\n{update.message.text}"
    await context.bot.send_message(chat_id=CREATOR_ID, text=forward_msg)
    
    # Confirm to user
    contact_mode_users.remove(update.message.from_user.id)
    await update.message.reply_text("✅ Message sent to support team")

# ======================
# BOT SETUP
# ======================
def main():
    """Start the bot"""
    print("🟢 STARTING BOT...")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("add", add_link))
        
        # Button handler
        app.add_handler(CallbackQueryHandler(button_click))
        
        # Message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message))
        
        print("✅ BOT IS RUNNING")
        app.run_polling()
    except Exception as e:
        print(f"❌ FAILED TO START: {e}")

if __name__ == "__main__":
    main()