import os, logging, asyncio, re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from services.pipeline import generate_project

logging.basicConfig(level=logging.INFO)
TOKEN=os.environ["BOT_TOKEN"]

def parse_request(args):
    if not args:
        return None, None, ""
    language="hinglish"
    duration=10
    # Supported: /cartoon hinglish 10 story...
    if args[0].lower() in ("hinglish","english"):
        language=args.pop(0).lower()
    if args and re.fullmatch(r"\d+",args[0]):
        duration=int(args.pop(0))
    return language,duration," ".join(args).strip()

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 VELOCITY LONG-FORM CARTOON STUDIO\n\n"
        "Use:\n/cartoon hinglish 10 A boy falls in love with a princess\n\n"
        "Language: hinglish / english\nLength: 5 / 10 / 20 / 30 minutes"
    )

async def cartoon(update:Update,context:ContextTypes.DEFAULT_TYPE):
    language,duration,prompt=parse_request(list(context.args))
    if not prompt:
        await update.message.reply_text(
            "Example:\n/cartoon hinglish 10 A poor boy meets a rich girl"
        )
        return
    if duration not in (5,10,20,30):
        await update.message.reply_text("Length must be 5, 10, 20 or 30 minutes.")
        return

    status=await update.message.reply_text("🧠 Planning your long-form story…")
    try:
        path,title=await generate_project(
            prompt,language,duration,
            lambda s: status.edit_text(s)
        )
        with open(path,"rb") as f:
            await update.message.reply_document(
                f,filename=os.path.basename(path),
                caption=f"🎬 {title}\n🌐 {language.title()}\n⏱️ {duration} minutes\n📺 1920×1080 YouTube video"
            )
        os.remove(path)
    except Exception as e:
        logging.exception("generation failed")
        await status.edit_text("❌ Generation failed:\n"+str(e))

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("cartoon",cartoon))
    app.run_polling()

if __name__=="__main__":
    main()
