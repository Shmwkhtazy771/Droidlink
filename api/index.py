import telebot
from flask import Flask, request

# --- الإعدادات ---
TOKEN = '8313488232:AAFSCmIgCV-ped9mxJFGs3RyRn-A0vw8_Tg'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- معالج أمر البداية (اختيار اللغة فقط) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup()
    # أزرار بسيطة للتجربة
    markup.add(telebot.types.InlineKeyboardButton("🇸🇦 العربية", callback_data=f"ar_{user_id}"))
    markup.add(telebot.types.InlineKeyboardButton("🇺🇸 English", callback_data=f"en_{user_id}"))
    
    bot.send_message(message.chat.id, "مرحباً! اختر لغتك للتجربة:\nWelcome! Choose language to test:", reply_markup=markup)

# --- معالج ضغط الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if "ar_" in call.data:
        bot.answer_callback_query(call.id, "تم اختيار اللغة العربية ✅")
        bot.edit_message_text("ممتاز! النظام استجاب باللغة العربية. الاتصال سليم 100%.", call.message.chat.id, call.message.message_id)
    elif "en_" in call.data:
        bot.answer_callback_query(call.id, "English Selected ✅")
        bot.edit_message_text("Great! The system responded in English. Connection is 100% solid.", call.message.chat.id, call.message.message_id)

# --- مسار استقبال البيانات (Webhook) ---
@app.route('/api/index', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "Server is Up!", 200
