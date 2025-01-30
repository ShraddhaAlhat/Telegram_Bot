Updating README and adding report file. code uploaded

# Telegram Bot for PDF, Image, and Text Processing with WebSearch Integration
This is a Python-based Telegram bot that integrates with Google Gemini AI for natural language processing and image analysis. It can handle a wide range of tasks including answering text queries, analyzing images, summarizing documents, and searching the web.

## Features

- **Web Search** ```(/websearch)```: Allows users to perform a web search by providing a query. The bot fetches relevant web results.
- **Text Processing**: The bot processes user queries, generates detailed responses, and adds emojis naturally.
- **Image Analysis**: The bot analyzes uploaded images and returns detailed descriptions.
- **PDF Document Processing**: The bot extracts text from PDFs and summarizes or analyzes the content.


## Prerequisites:

1. **Python** >= 3.7
2. **MongoDB instance** (Mongo URI)
3. **Google Gemini API** Key for generative AI responses.

## Steps to Set Up Locally

1. Clone the repository:


```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```
2.Install dependencies:

```bash
pip install -r requirements.txt
```
3. Add your own API keys in ```.evn```

4. Start the bot:
```bash
python bot.py

```
####  Getting Telegram Token
- Open Telegram and search for @BotFather.
- Start a conversation by typing ```/start```.
- Type ```/newbot```, provide a name and a username ending with "bot" (e.g., ```my_telegram_bot```).
- Copy the API token provided and store it in your ```.env``` file as

## Bot Commands

- **```/start```**: Initializes the bot, prompting the user to share their contact info.
- **Send a text message**: The bot will generate a response based on the input using Google Gemini.
- **Send an image**: The bot will analyze the image and provide a description.
- **Send a PDF file**: The bot will extract and summarize the text content

## Bot Usage Example

1. Start a conversation with the bot:
- Send ```/start``` to the bot.
- If you're a new user, the bot will ask for your phone number to register.


2. Send a query:

- Type any text, and the bot will generate a response. Example:

```bash
What is the capital of France?
```
- The bot will reply with a factual answer, for example:
   
   "*💡 The capital of France is Paris.*"

3. Send an image:

- Upload an image, and the bot will analyze and describe it. Example:
  
  "*📸 Image Analysis: This is a picture of a sunset over the ocean with a few scattered clouds."*


4. Send a PDF document:

- Upload a PDF document, and the bot will summarize it. Example:
  
  *"📑 Document Summary: This document discusses the importance of machine learning in modern applications...*"

 ## Project Structure
``` bash /your-repo
  /bot.py             # Main bot logic and handling
  /requirements.txt   # List of dependencies
  /README.md          # Project overview
  .env                # Store API keys and other configurations
```
### Logging:
- The bot logs important events (errors, queries, responses) for better debugging and performance tracking.

### Error Handling:

- The bot provides feedback in case of errors (e.g., timeout errors, empty responses, invalid file formats).
