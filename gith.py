import telebot
import requests
import random
import string
import zipfile
import os
import time

TOKEN = "7492001137:AAGfDGg8YoFWkFps8SqcOkjht2B1D4g6vU4"
bot = telebot.TeleBot(TOKEN)

start_time = time.time()

def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def download_file(url):
    response = requests.get(url)
    return response.content if response.status_code == 200 else None

def get_repo_content(repo_url):
    api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/contents"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(api_url, headers=headers)
    content = {}
    if response.ok:
        for item in response.json():
            if item["type"] == "file":
                content[item["name"]] = download_file(item["download_url"])
            elif item["type"] == "dir":
                subdir_content = get_repo_content(item["url"])
                content.update(subdir_content)
    return content

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "```\n My Bot GitHub Downloader By @sedihbetgw \n```", parse_mode='Markdown')

@bot.message_handler(commands=['git'])
def send_repo_files(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Format Salah /git [url repo github]")
        return
    repo_url = message.text.split()[1]
    content = get_repo_content(repo_url)

    if not content:
        bot.reply_to(message, "No files found in the repository.")
        return

    zip_name = random_string(10) + ".zip"
    with zipfile.ZipFile(zip_name, 'w') as zip_file:
        for file_name, file_content in content.items():
            zip_file.writestr(file_name, file_content)

    with open(zip_name, "rb") as zip_file:
        bot.send_document(message.chat.id, zip_file)

    os.remove(zip_name)

@bot.message_handler(commands=['get'])
def wget_file(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Format Salah /get [url file]")
        return
    url = message.text.split()[1]

    r = requests.get(url)
    if r.status_code == 200:
        file_name = url.split("/")[-1]
        with open(file_name, "wb") as file:
            file.write(r.content)
        with open(file_name, "rb") as file:
            bot.send_document(message.chat.id, file)
        os.remove(file_name)
    else:
        bot.reply_to(message, "Failed to download the file from the provided URL.")

@bot.message_handler(commands=['uptime'])
def uptime(message):
    current_time = time.time()
    uptime_seconds = current_time - start_time
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    bot.reply_to(message, f"Bot has been running for {uptime_str}")

bot.polling()
