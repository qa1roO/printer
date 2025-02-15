import os
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
load_dotenv() 
API = os.getenv('TELEGRAM_API')
PRINTER_NAME = os.getenv('PRINTER_NAME')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await update.message.document.get_file()
    file_ext = file.file_path.split('.')[-1].lower()
    file_path = f"{file.file_id}.{file_ext}"

    await file.download_to_drive(file_path)
    await update.message.reply_text("Отправка")

    if file_ext=='pdf':
        final_path = file_path
    elif file_ext == 'docx':
        final_path = f'{file.file_id}.pdf'
        try:
            subprocess.run(f'libreoffice --headless --convert-to pdf "{file_path}"', shell=True, check=True)
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"cannot convert to docx: {e}")
            return
    else:
        await update.message.reply_text("инвалид.")
        return

    try:
        subprocess.run(f'lp -d {PRINTER_NAME} "{final_path}"', shell=True, check=True)

        os.remove(final_path)

        await update.message.reply_text("good")
    except Exception as e:
        await update.message.reply_text(f"абшибка: {e}")

app = ApplicationBuilder().token(API).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

print("RUnning")
app.run_polling()
