import os
import json
import requests
from telethon import TelegramClient, events, Button

api_id = '9609511'
api_hash = '066c47a00d147eb82ccd6af1f7bc7826'
bot_token = '6841028399:AAEziS8K7SlCVV7bxJaJDZ_phjTURTh_QyI'

elevenlabs_api_key = '642ccb358bcc15c64a990b84c499eaa5'
voice_id_1 = 'QUkTP5zGztmb17GWHSnj'
voice_id_2 = 'kqi0xEeNkRZvVryPZNFQ'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

user_voice_preferences = {}

async def convert_audio(audio_bytes, filename):
    tmp_filename = f"audios/{filename}.ogg"
    with open(tmp_filename, "wb") as audio_file:
        audio_file.write(audio_bytes)
    os.system(f"ffmpeg -y -i {tmp_filename} -c:a libopus {tmp_filename}.ogg")
    return f"{tmp_filename}.ogg"

def generate_voice(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "similarity_boost": 0.100,
            "stability": 0.50,
            "style": 0.60,
            "use_speaker_boost": True
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        return None

@client.on(events.NewMessage(func=lambda event: event.text and event.text != "/start"))
async def echo(event):
    if event.media:
        await event.respond('❌ <b>Поддерживается только текст</b>', parse_mode='HTML')
        return

    await event.respond(f'⚡️ <b>Генерирую...</b>', parse_mode='HTML')

    user_id = event.sender_id
    if user_id in user_voice_preferences:
        voice_id = user_voice_preferences[user_id]
    else:
        voice_id = voice_id_1

    voice_message = generate_voice(event.raw_text, voice_id)
    
    if voice_message:
        audio_filename = f"{event.id}_{event.date.strftime('%Y%m%d_%H%M%S')}"
        converted_audio = await convert_audio(voice_message, audio_filename)
        await client.send_file(event.chat_id, converted_audio, voice_note=True, caption=f"🗣 Голос: {voice_id}")
        os.remove(converted_audio)
    else:
        await event.respond('❌ <b>Ошибка при генерации голоса</b>, <i>Обратитесь к @yummy1gay за репортбагом</i>', parse_mode='HTML')

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        '👋 <b>Привет!</b> <i>С помощью данного бота можно сгенерировать аудио голосом Эйдена Флинна.</i>\n'
        '✍️ <i>Просто отправь мне текст и я его озвучу</i>'
        '🗣 <i>Выбери голос которым будет озвучиватся текст:</i>',
        buttons=[
            [Button.inline('Эйден Флинн', data='voice_1')],
            [Button.inline('Горо Номору', data='voice_2')]
        ],
        parse_mode='HTML'
    )

@client.on(events.CallbackQuery(pattern=b'voice_1'))
async def choose_voice_1(event):
    user_id = event.sender_id
    user_voice_preferences[user_id] = voice_id_1
    await event.edit(
        '👋 <b>Привет!</b> <i>С помощью данного бота можно сгенерировать аудио голосом Эйдена Флинна, и Горо Номору</i>\n'
        '✍️ <i>Просто отправь мне текст и я его озвучу</i>'
        '🗣 <i>Выбран голос Эйдена Флинна</i>', parse_mode='HTML'
    )

@client.on(events.CallbackQuery(pattern=b'voice_2'))
async def choose_voice_2(event):
    user_id = event.sender_id
    user_voice_preferences[user_id] = voice_id_2
    await event.edit(
        '👋 <b>Привет!</b> <i>С помощью данного бота можно сгенерировать аудио голосом Эйдена Флинна, и Горо Номору</i>\n'
        '✍️ <i>Просто отправь мне текст и я его озвучу</i>'
        '🗣 <i>Выбран голос Горо Номору</i>', parse_mode='HTML'
    )

client.start()
client.run_until_disconnected()
