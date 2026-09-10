import os, logging, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from services.pipeline import create_video

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ["BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 VELOCITY AI CARTOON STUDIO\n\n"
        "/cartoon <story idea>\n\n"
        "Example:\n/cartoon A poor boy meets a princess in a magical city."
    )

async def cartoon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args).strip()
    if not prompt:
        await update.message.reply_text("Use: /cartoon <your story idea>")
        return
    status = await update.message.reply_text("🎬 Preparing your YouTube cartoon…")
    try:
        path = await create_video(prompt, lambda x: status.edit_text(x))
        with open(path, "rb") as f:
            await update.message.reply_document(
                document=f,
                caption="🎬 Finished — YouTube-ready 16:9 MP4."
            )
        os.remove(path)
    except Exception as e:
        logging.exception("generation failed")
        await status.edit_text("❌ " + str(e))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cartoon", cartoon))
    app.run_polling()

if __name__ == "__main__":
    main()
