
import os
import re
import logging
import traceback
import asyncio
import time
from datetime import datetime
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, Defaults
import google.generativeai as genai
from motor.motor_asyncio import AsyncIOMotorClient
from PyPDF2 import PdfReader
from PIL import Image

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

executor = ThreadPoolExecutor(max_workers=4)

# MongoDB setup
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client.gemini_bot
users = db.users
chats = db.chats
files = db.files

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config={
        "max_output_tokens": 2000,
        "temperature": 0.7
    }
)
vision_model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config={
        "max_output_tokens": 1000,
        "temperature": 0.5
    }
)

async def typing_action(update: Update):
    """Show typing indicator"""
    while True:
        await update.effective_chat.send_action(action="typing")
        await asyncio.sleep(4.5)

def clean_response(text: str) -> str:
    """Remove markdown and format text"""
    return re.sub(r'\*+', '', text).strip()

def add_emojis(text: str) -> str:
    """Add emojis naturally if missing"""
    if not any(c in text for c in [
        '\U0001F600-\U0001F64F',  # Emoticons
        '\U0001F300-\U0001F5FF',  # Symbols & Pictographs
        '\U0001F680-\U0001F6FF'   # Transport & Map
    ]):
        if '?' in text:
            return f"❓ {text}"
        return f"💡 {text}"
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing = await users.find_one({"chat_id": user.id})
    
    if not existing:
        await users.insert_one({
            "chat_id": user.id,
            "first_name": user.first_name,
            "username": user.username,
            "phone": None,
            "registered_at": datetime.now()
        })
        contact_btn = KeyboardButton("Share Phone", request_contact=True)
        await update.message.reply_text(
            "👋 Welcome! Please share your phone number:",
            reply_markup=ReplyKeyboardMarkup([[contact_btn]], one_time_keyboard=True)
        )
    else:
        await update.message.reply_text("🎉 Welcome back!")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    phone = update.message.contact.phone_number
    await users.update_one(
        {"chat_id": user.id},
        {"$set": {"phone": phone}}
    )
    await update.message.reply_text(
        "✅ Registration complete!",
        reply_markup=ReplyKeyboardRemove()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith('/'):
        return
        
    start_time = time.time()
    typing_task = asyncio.create_task(typing_action(update))
    
    try:
        user = update.effective_user
        text = update.message.text
        
        if not text.strip():
            await update.message.reply_text("💬 Please enter your query")
            return
            
        prompt = f"""Respond to: {text}
        
        - Provide a complete, factual answer
        - Use 1-2 relevant emojis naturally in the response
        - Avoid markdown formatting
        - Maintain professional tone
        - Structure answer clearly with paragraphs"""
        
        response = await asyncio.wait_for(
            text_model.generate_content_async(prompt),
            timeout=30
        )
        
        if not response.text:
            raise ValueError("Empty response")
            
        clean_text = clean_response(response.text)
        final_text = add_emojis(clean_text)
        
        await update.message.reply_text(final_text)
        await chats.insert_one({
            "user_id": user.id,
            "query": text,
            "response": final_text,
            "timestamp": datetime.now()
        })
        
        logging.info(f"Processed in {time.time() - start_time:.2f}s")
        
    except asyncio.TimeoutError:
        await update.message.reply_text("⏳ Response timed out - please try again")
    except Exception as e:
        logging.error(f"Error: {traceback.format_exc()}")
        await update.message.reply_text("⚠️ Error processing request")
    finally:
        typing_task.cancel()

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    typing_task = asyncio.create_task(typing_action(update))
    progress_msg = None
    
    try:
        user = update.effective_user
        progress_msg = await update.message.reply_text("🖼️ Processing image...")
        
        photo = update.message.photo[-1]
        file = await photo.get_file()
        image_data = await file.download_as_bytearray()
        
        loop = asyncio.get_running_loop()
        image = await loop.run_in_executor(
            executor,
            lambda: Image.open(BytesIO(image_data)).convert("RGB")
        )
        
        response = await asyncio.wait_for(
            vision_model.generate_content_async(
                ["Describe this image in detail. Focus on key elements and context.", image]
            ),
            timeout=30
        )
        
        clean_text = clean_response(response.text)
        final_text = f"📸 Image Analysis:\n\n{add_emojis(clean_text)}"
        
        await files.insert_one({
            "user_id": user.id,
            "type": "image",
            "analysis": final_text,
            "timestamp": datetime.now(),
            "processing_time": time.time() - start_time
        })
        
        await progress_msg.edit_text(final_text)
        
    except Exception as e:
        if progress_msg:
            await progress_msg.edit_text("❌ Image processing failed")
        logging.error(f"Image error: {traceback.format_exc()}")
    finally:
        typing_task.cancel()

def extract_pdf_text(data: bytes) -> str:
    try:
        with BytesIO(data) as pdf_file:
            reader = PdfReader(pdf_file)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n".join(text)
    except Exception as e:
        logging.error(f"PDF error: {str(e)}")
        raise

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    typing_task = asyncio.create_task(typing_action(update))
    progress_msg = None
    
    try:
        user = update.effective_user
        progress_msg = await update.message.reply_text("📄 Processing document...")
        
        file = await update.message.document.get_file()
        data = await file.download_as_bytearray()
        
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(
            executor,
            lambda: extract_pdf_text(bytes(data))
        )
        
        if not text.strip():
            raise ValueError("No text extracted")
        
        if len(text) > 15000:
            text = text[:15000] + "\n[Content truncated for analysis]"
        
        response = await asyncio.wait_for(
            text_model.generate_content_async(
                f"Summarize this document in structured points:\n{text}"
            ),
            timeout=40
        )
        
        clean_text = clean_response(response.text)
        final_text = f"📑 Document Summary:\n\n{add_emojis(clean_text)}"
        
        await files.insert_one({
            "user_id": user.id,
            "type": "pdf",
            "analysis": final_text,
            "timestamp": datetime.now(),
            "processing_time": time.time() - start_time
        })
        
        await progress_msg.edit_text(final_text)
        
    except asyncio.TimeoutError:
        await progress_msg.edit_text("⏳ Processing timeout - try smaller files")
    except Exception as e:
        if progress_msg:
            await progress_msg.edit_text("⚠️ Document processing failed")
        logging.error(f"PDF error: {traceback.format_exc()}")
    finally:
        typing_task.cancel()

def main():
    app = ApplicationBuilder() \
        .token(os.getenv("TELEGRAM_TOKEN")) \
        .defaults(Defaults(block=False)) \
        .build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_file))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    app.run_polling()

if __name__ == "__main__":
    main()