import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ======================
# CONFIGURATION
# ======================
BOT_TOKEN = "7239607925:AAGYq1zt1NOw4vW3VnDa5SSJIQiifvimeBk"  # YOUR BOT TOKEN
ADMIN_ID = 7631211375  # YOUR ADMIN USER ID
CREATOR_ID = 8066177203  # YOUR CREATOR USER ID
DATABASE_VERSION = "1.0"  # DATABASE VERSION TRACKING

# ======================
# DATABASE SETUP
# ======================
class Database:
    def __init__(self):
        self.data = {
            "nltopics": {
                1: "https://example.com/nl1",
                2: "https://example.com/nl2"
            },
            "languages": {
                1: "https://example.com/lang1",
                2: "https://example.com/lang2"
            },
            "fetishes": {
                1: "https://example.com/fetish1",
                2: "https://example.com/fetish2"
            },
            "anime": {
                1: "https://example.com/anime1"
            },
            "megas": {
                1: "https://example.com/mega1"
            },
            "lives": {
                1: "https://example.com/live1"
            },
            "howto": {
                1: "• HOW TO OPEN LINKS •\n\n1. Click 'Watch Video'\n2. Wait 30 seconds\n3. Enjoy the content"
            }
        }
    
    def add_link(self, category, link):
        if category not in self.data:
            return False
        new_id = max(self.data[category].keys(), default=0) + 1
        self.data[category][new_id] = link
        return new_id

db = Database()
contact_mode_users = set()

# ======================
# MENU SYSTEM
# ======================
def create_main_menu():
    """Create the 2x2 button layout with single bottom buttons"""
    return [
        # First row - 2 buttons
        [InlineKeyboardButton("📚 NL Topics", callback_data="nltopics"), 
         InlineKeyboardButton("🌐 Languages", callback_data="languages")],
        
        # Second row - 2 buttons
        [InlineKeyboardButton("🎭 Fetishes", callback_data="fetishes"), 
         InlineKeyboardButton("🇯🇵 Anime", callback_data="anime")],
        
        # Third row - 2 buttons
        [InlineKeyboardButton("💾 Megas", callback_data="megas"), 
         InlineKeyboardButton("🔴 Lives", callback_data="lives")],
        
        # Fourth row - 1 button (how to)
        [InlineKeyboardButton("❓ How To Open Links", callback_data="howto")],
        
        # Fifth row - 1 button (contact)
        [InlineKeyboardButton("📩 Contact Support", callback_data="contact")]
    ]

# ======================
# COMMAND HANDLERS
# ======================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    try:
        keyboard = InlineKeyboardMarkup(create_main_menu())
        await update.message.reply_text(
            "🔻 SELECT CATEGORY 🔻",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Start command error: {e}")

async def add_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    link_num = db.add_link(category, link)
    
    if link_num:
        await update.message.reply_text(f"✅ Added to {category} as link #{link_num}")
    else:
        await update.message.reply_text("❌ Failed to add link")

# ======================
# BUTTON HANDLERS
# ======================
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process all button clicks"""
    query = update.callback_query
    await query.answer("⚡")  # Button click animation
    
    try:
        if query.data == "howto":
            await show_howto_guide(query)
        elif query.data == "contact":
            await start_contact_mode(query)
        elif query.data in db.data:
            await send_category_links(query, context)
        elif query.data == "back":
            await return_to_main_menu(query)
    except Exception as e:
        print(f"Button error: {e}")

async def show_howto_guide(query):
    """Display how-to guide"""
    guide = db.data["howto"][1]
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
        text="✉️ Contact our support team:\n\nPlease describe your issue in detail...\n\nSend /cancel to exit",
        reply_markup=InlineKeyboardMarkup(back_button)
    )

async def send_category_links(query, context):
    """Send all links for a category one by one"""
    links = db.data[query.data]
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
        text="🔻 SELECT CATEGORY 🔻",
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
    forward_msg = f"📩 New Support Message:\nFrom: @{user.username}\nID: {user.id}\n\n{update.message.text}"
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
    print(f"Database v{DATABASE_VERSION}")
    print(f"Admin ID: {ADMIN_ID}")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("add", add_link_command))
        
        # Button handler
        app.add_handler(CallbackQueryHandler(handle_button_click))
        
        # Message handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_message))
        
        print("✅ BOT IS RUNNING - PRESS CTRL+C TO STOP")
        app.run_polling()
    except Exception as e:
        print(f"❌ BOT FAILED: {e}")

if __name__ == "__main__":
    main()