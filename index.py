# ENSURE, THAT EVERY STATUS EXCEPT 'idle' HAS IT'S .png ICON IN
# PYTHON SCRIPT'S DIRECTORY, ELSEWAY IT CAN CAUSE AN ERROR
# ALSO ENSURE, THAT THERE IS AN AVATAR avatar.jpg IN THIS DIRECTORY
# --- CONFIG --- #

api_id = 0000000
api_hash = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

statuses = {
    'game': '🃏 Играю',
    'work': '💻 Работаю',
    'sleep': '😴 Сплю',
    'study': '🧑‍🎓 Учусь',
    'relax': '💃 Отдыхаю',
    'idle': '🙅‍♂️ без статуса',
    'busy': '⛔️ Занят',
    'dnd': '🚫 НЕ БЕСПОКОИТЬ 🚫'
}


# --- /CONFIG --- #

# Import modules
from telethon import TelegramClient, events, Button
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from PIL import Image, ImageEnhance
import io
import os

# Find, where python script is located to fix the problems with relative path

path = os.path.dirname(os.path.abspath(__file__)) + "/"

# Start client and bot sessions

client = TelegramClient('setstatus_client', api_id, api_hash)
bot = TelegramClient('setstatus_bot', api_id, api_hash)
client.start()
bot.start(bot_token="1681502332:AAE3tSKgQbon8jMLqDX5AvsItjHlfM_giyk")

# Lookup for user's name and id

base = ''
admins = []

try:
    name = client.get_me()
    base = name.first_name
    admins = [name.id]
    current_name = str(name.last_name)[1:-1]

    if current_name and current_name in statuses.value():
        for key, value in statuses.items():
            if value == current_name:
                current_status = key
                break
except:
    pass

# Create main menu

buttons = []
for value, status in list(statuses.items()):
    buttons.append(Button.inline(status, value))

markup = []
for i in range(0, len(buttons), 2):
    markup.append(buttons[i:i + 2])


# Function, that sets the status

async def set_status(status):
    if status == 'idle':
        await client(UpdateProfileRequest(
            first_name=base,
            last_name=''
        ))
        with open(path + 'avatar.jpg', 'rb') as f:
            status_img_bytes = f.read()
    else:
        status_text = '᚜' + statuses[status] + '᚛'

        await client(UpdateProfileRequest(
            first_name=base,
            last_name=status_text
        ))

        status_img_path = path + status + '.png'

        avatar = Image.open(path + 'avatar.jpg')
        avatar = ImageEnhance.Brightness(avatar).enhance(.45)

        icon = Image.open(status_img_path)
        icon = icon.transform((avatar.size[0] // 2, avatar.size[1] // 2), Image.EXTENT, (0, 0, icon.size[0], icon.size[1]))

        avatar.paste(icon, (avatar.size[0] // 2 - icon.size[0] // 2, avatar.size[1] // 2 - icon.size[1] // 2), icon)

        status_img_bytes = io.BytesIO()
        avatar.save(status_img_bytes, format='PNG')
        status_img_bytes = status_img_bytes.getvalue()

    await client(DeletePhotosRequest(await client.get_profile_photos('me')))
    await client(UploadProfilePhotoRequest(await client.upload_file(status_img_bytes)))


# When bot receives message, it should print the menu

@bot.on(events.NewMessage())
async def handler(event):
    await event.reply(message='Текущий статус: ' + statuses[current_status] + ' (' + current_status + ')', parse_mode="Markdown", buttons=markup)


# Buttons handler

@bot.on(events.CallbackQuery())
async def callback(event):
    global current_status
    data = event.data.decode('utf-8')
    if data in statuses:
        await set_status(data)
        current_status = data
        await event.answer('Статус ' + data + ' установлен')

    await event.edit(text='Текущий статус: ' + statuses[current_status] + ' (' + current_status + ')', parse_mode="Markdown", buttons=markup)

# Finally, activate longpolling for bot

bot.run_until_disconnected()
