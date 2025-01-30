Updating README and adding report file. Initial version of the code uploaded

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
