import requests
import json
import time
from datetime import datetime
import random

# ============ SOZLAMALAR ============
TELEGRAM_TOKEN = "8303477154:AAH7DY4-LFQXcnuWgKGHCP5gV14owlZP68A"
GEMINI_API_KEY = "AIzaSyAmuIUg-N76HT3_zKQrXpbl-oF9Urd6GWc"
ADMIN_ID = 6961100352  # Sizning Telegram ID

# ============ FAYLLAR ============
QUESTIONS_FILE = "questions.json"
USER_DATA_FILE = "user_data.json"

# ============ BIOLOGIYA VA KIMYO KALIT SO'ZLARI ============
BIO_CHEM_KEYWORDS = [
    'hujayra', 'to\'qima', 'dnk', 'rnk', 'protein', 'ferment', 'organizma',
    'fotosintez', 'respiratsiya', 'evolyutsiya', 'genetika', 'ekologiya',
    'atom', 'molekula', 'element', 'reaksiya', 'kislota', 'asos', 'tuz',
    'oksidlanish', 'organik', 'noorganik', 'biologiya', 'kimyo',
    'cell', 'dna', 'rna', 'enzyme', 'biology', 'chemistry', 'mitoz', 'meyoz'
]

# ============ TELEGRAM API ============
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Xato: {e}")
        return None

def edit_message(chat_id, message_id, text, reply_markup=None):
    url = f"{BASE_URL}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

def answer_callback(callback_id, text=""):
    url = f"{BASE_URL}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_id, "text": text})

def get_updates(offset=0):
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json().get("result", [])
    except:
        return []

# ============ GEMINI API (REST) ============
def ask_gemini(question, system_prompt=""):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{system_prompt}\n\n{question}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "❌ Javob olinmadi. Qayta urinib ko'ring."
    except Exception as e:
        return f"❌ Xatolik yuz berdi: {str(e)}"

# ============ FAYL BILAN ISHLASH ============
def load_json(filename, default=None):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default if default is not None else {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_questions():
    return load_json(QUESTIONS_FILE, [])

def save_questions(questions):
    save_json(QUESTIONS_FILE, questions)

def load_user_data():
    return load_json(USER_DATA_FILE, {})

def save_user_data(data):
    save_json(USER_DATA_FILE, data)

# ============ FILTR ============
def is_bio_chem_question(text):
    text_lower = text.lower()
    
    # Kalit so'zlar orqali tekshirish
    for keyword in BIO_CHEM_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    
    # Gemini bilan tekshirish
    try:
        check_prompt = f"Quyidagi savol biologiya yoki kimyo faniga tegishlimi? Faqat 'HA' yoki 'YO'Q' deb javob ber.\n\nSavol: {text}"
        response = ask_gemini(check_prompt)
        return "HA" in response.upper() or "YES" in response.upper()
    except:
        return False

# ============ KLAVIATURA ============
def get_main_keyboard(user_id):
    if user_id == ADMIN_ID:
        return {
            "keyboard": [
                [{"text": "📚 Savollar"}],
                [{"text": "💬 Gemini AI"}, {"text": "📊 Statistika"}]
            ],
            "resize_keyboard": True
        }
    else:
        return {
            "keyboard": [
                [{"text": "📝 Test ishlash"}],
                [{"text": "💬 Gemini AI"}, {"text": "📊 Mening natijalarim"}]
            ],
            "resize_keyboard": True
        }

# ============ SESSION BOSHQARUVI ============
user_sessions = {}

def get_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    return user_sessions[user_id]

# ============ START ============
def handle_start(chat_id, user_id, first_name):
    user_data = load_user_data()
    
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "name": first_name,
            "tests_completed": 0,
            "total_score": 0,
            "history": []
        }
        save_user_data(user_data)
    
    text = f"""
👋 Assalomu alaykum, {first_name}!

🧬 Men Biologiya va Kimyo bo'yicha AI yordamchi botman.

📌 Imkoniyatlarim:
• 💬  AI bilan biologiya va kimyo savollariga javob
• 📝 Test ishlash va natijalarni baholash
• 📊 Natijalaringizni kuzatish

⚠️ Faqat biologiya va kimyo savollariga javob beraman! admin @Husanboyo07 va yana albatta qiziqarli botlar bor ulardan biri sertifikat test ishlash mumkin bolgan bot unda siz real vaqt tizimida test ishlasangiz boladi https://t.me/Biomalumolarbazabot
"""
    
    send_message(chat_id, text, get_main_keyboard(user_id))

# ============ GEMINI SAVOL ============
def handle_gemini_question(chat_id, user_id, text):
    # Filtr
    if not is_bio_chem_question(text):
        send_message(chat_id, 
            "❌ Kechirasiz, men faqat biologiya va kimyo savollariga javob beraman.\n\n"
            "📖 Iltimos, darsni yaxshi o'rganib oling va biologiya yoki kimyo bo'yicha savol bering! 🧬⚗️"
        )
        return
    
    # Typing effect
    send_message(chat_id, "⏳ Javob tayyorlanmoqda...")
    
    # Gemini dan javob olish
    system_prompt = """Sen biologiya va kimyo fanlari bo'yicha professional o'qituvchisan. 
Quyidagi savolga batafsil, lekin tushunarli javob ber. 
Javobingni strukturali qilib, kerakli joylarida emoji ishlatib yoz."""
    
    answer = ask_gemini(text, system_prompt)
    send_message(chat_id, answer)

# ============ ADMIN - SAVOLLAR ============
def handle_admin_questions(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "➕ Savol qo'shish", "callback_data": "add_question"}],
            [{"text": "📋 Savollar ro'yxati", "callback_data": "list_questions"}],
            [{"text": "🗑 Savolni o'chirish", "callback_data": "delete_question"}]
        ]
    }
    send_message(chat_id, "📚 Savollar boshqaruvi:", keyboard)

def handle_add_question(chat_id, user_id):
    session = get_session(user_id)
    session['state'] = 'adding_question'
    
    send_message(chat_id,
        "📝 Yangi savol qo'shish:\n\n"
        "Savol formatini quyidagicha yuboring:\n\n"
        "SAVOL: Savol matni?\n"
        "A) Variant 1\n"
        "B) Variant 2\n"
        "C) Variant 3\n"
        "D) Variant 4\n"
        "JAVOB: A\n"
        "FAN: biologiya"
    )

def handle_question_input(chat_id, user_id, text):
    try:
        lines = text.strip().split('\n')
        
        question = ""
        options = []
        correct = ""
        subject = ""
        
        for line in lines:
            if line.startswith("SAVOL:"):
                question = line.replace("SAVOL:", "").strip()
            elif line.startswith(("A)", "B)", "C)", "D)")):
                options.append(line.strip())
            elif line.startswith("JAVOB:"):
                correct = line.replace("JAVOB:", "").strip()
            elif line.startswith("FAN:"):
                subject = line.replace("FAN:", "").strip()
        
        if question and len(options) == 4 and correct and subject:
            questions = load_questions()
            questions.append({
                "id": len(questions) + 1,
                "question": question,
                "options": options,
                "correct": correct,
                "subject": subject
            })
            save_questions(questions)
            
            send_message(chat_id, "✅ Savol muvaffaqiyatli qo'shildi!")
            session = get_session(user_id)
            session.pop('state', None)
        else:
            send_message(chat_id, "❌ Format noto'g'ri! Qaytadan urinib ko'ring.")
    except Exception as e:
        send_message(chat_id, f"❌ Xatolik: {e}")

def handle_list_questions(chat_id):
    questions = load_questions()
    
    if not questions:
        send_message(chat_id, "📭 Hozircha savollar yo'q.")
        return
    
    text = "📋 Savollar ro'yxati:\n\n"
    for i, q in enumerate(questions[:10], 1):
        text += f"{i}. {q['question'][:50]}...\n"
    
    send_message(chat_id, text)

def handle_delete_question(chat_id, user_id):
    questions = load_questions()
    
    if not questions:
        send_message(chat_id, "📭 O'chiriladigan savollar yo'q.")
        return
    
    session = get_session(user_id)
    session['state'] = 'deleting_question'
    
    send_message(chat_id, f"📋 Jami savollar: {len(questions)}\n\n"
                          "O'chirmoqchi bo'lgan savol raqamini yuboring:")

def handle_delete_input(chat_id, user_id, text):
    try:
        num = int(text)
        questions = load_questions()
        
        if 1 <= num <= len(questions):
            deleted = questions.pop(num - 1)
            save_questions(questions)
            send_message(chat_id, f"✅ Savol o'chirildi:\n{deleted['question']}")
            
            session = get_session(user_id)
            session.pop('state', None)
        else:
            send_message(chat_id, "❌ Noto'g'ri raqam!")
    except ValueError:
        send_message(chat_id, "❌ Raqam kiriting!")

# ============ TEST ISHLASH ============
def start_test(chat_id, user_id):
    questions = load_questions()
    
    if not questions:
        send_message(chat_id, "📭 Hozircha testlar mavjud emas.")
        return
    
    # 10 ta random savol
    selected = random.sample(questions, min(10, len(questions)))
    
    session = get_session(user_id)
    session['test_questions'] = selected
    session['test_answers'] = []
    session['current_question'] = 0
    
    send_test_question(chat_id, user_id)

def send_test_question(chat_id, user_id):
    session = get_session(user_id)
    questions = session.get('test_questions', [])
    current = session.get('current_question', 0)
    
    if current >= len(questions):
        finish_test(chat_id, user_id)
        return
    
    q = questions[current]
    
    text = f"❓ Savol {current + 1}/{len(questions)}\n\n"
    text += f"📝 {q['question']}\n\n"
    
    keyboard = {"inline_keyboard": []}
    for i, opt in enumerate(q['options']):
        callback_data = f"answer_{chr(65+i)}"
        keyboard["inline_keyboard"].append([{"text": opt, "callback_data": callback_data}])
    
    send_message(chat_id, text, keyboard)

def handle_test_answer(chat_id, user_id, answer):
    session = get_session(user_id)
    questions = session.get('test_questions', [])
    current = session.get('current_question', 0)
    
    if current >= len(questions):
        return
    
    q = questions[current]
    
    session['test_answers'].append({
        'question': q['question'],
        'user_answer': answer,
        'correct_answer': q['correct'],
        'is_correct': answer == q['correct']
    })
    
    if answer == q['correct']:
        send_message(chat_id, "✅ To'g'ri!")
    else:
        send_message(chat_id, f"❌ Noto'g'ri! To'g'ri javob: {q['correct']}")
    
    session['current_question'] += 1
    time.sleep(1)
    send_test_question(chat_id, user_id)

def finish_test(chat_id, user_id):
    session = get_session(user_id)
    answers = session.get('test_answers', [])
    
    correct_count = sum(1 for a in answers if a['is_correct'])
    total = len(answers)
    score = (correct_count / total) * 100 if total > 0 else 0
    
    # Gemini baholash
    analysis_prompt = f"""
Sen pedagogik baholash mutaxassisisan. Talaba test ishladi:

Umumiy: {total}
To'g'ri: {correct_count}
Xato: {total - correct_count}
Foiz: {score:.1f}%

Quyidagilarni ber:
1. Umumiy baholash (A'lo, Yaxshi, Qoniqarli, Qoniqarsiz)
2. Kuchli va zaif tomonlar
3. Motivatsion xabar

Javobni emoji bilan bezab, qisqa va tushunarli yoz.
"""
    
    analysis = ask_gemini(analysis_prompt)
    
    # Natijani saqlash
    user_data = load_user_data()
    if str(user_id) in user_data:
        user_data[str(user_id)]['tests_completed'] += 1
        user_data[str(user_id)]['total_score'] += score
        user_data[str(user_id)]['history'].append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'score': score,
            'correct': correct_count,
            'total': total
        })
        save_user_data(user_data)
    
    result_text = f"""
🎯 Test natijalari:

📊 Statistika:
• Jami: {total}
• To'g'ri: {correct_count} ✅
• Xato: {total - correct_count} ❌
• Ball: {score:.1f}%

{'-' * 30}

🤖 Gemini 2.0 Baholashi:

{analysis}
"""
    
    send_message(chat_id, result_text, get_main_keyboard(user_id))
    
    # Sessionni tozalash
    user_sessions[user_id] = {}

# ============ STATISTIKA ============
def show_user_stats(chat_id, user_id):
    user_data = load_user_data()
    
    if str(user_id) not in user_data:
        send_message(chat_id, "📭 Sizda hali natijalar yo'q.")
        return
    
    data = user_data[str(user_id)]
    avg = data['total_score'] / data['tests_completed'] if data['tests_completed'] > 0 else 0
    
    text = f"""
📊 Sizning natijalaringiz:

👤 Ism: {data['name']}
📝 Ishangan testlar: {data['tests_completed']}
⭐️ O'rtacha ball: {avg:.1f}%

📈 Oxirgi 5 ta natija:
"""
    
    for i, h in enumerate(data['history'][-5:], 1):
        text += f"\n{i}. {h['date']} - {h['score']:.1f}% ({h['correct']}/{h['total']})"
    
    send_message(chat_id, text)

def show_admin_stats(chat_id):
    user_data = load_user_data()
    questions = load_questions()
    
    total_users = len(user_data)
    total_tests = sum(u['tests_completed'] for u in user_data.values())
    
    text = f"""
📊 Bot statistikasi:

👥 Foydalanuvchilar: {total_users}
📝 Savollar: {len(questions)}
✅ Testlar: {total_tests}

🔝 Top 5:
"""
    
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['tests_completed'], reverse=True)[:5]
    
    for i, (uid, data) in enumerate(sorted_users, 1):
        avg = data['total_score'] / data['tests_completed'] if data['tests_completed'] > 0 else 0
        text += f"\n{i}. {data['name']} - {data['tests_completed']} test, {avg:.1f}%"
    
    send_message(chat_id, text)

# ============ ASOSIY HANDLER ============
def handle_message(message):
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    text = message.get('text', '')
    first_name = message['from'].get('first_name', 'Foydalanuvchi')
    
    session = get_session(user_id)
    state = session.get('state')
    
    # Admin maxsus inputlar
    if user_id == ADMIN_ID:
        if state == 'adding_question':
            handle_question_input(chat_id, user_id, text)
            return
        elif state == 'deleting_question':
            handle_delete_input(chat_id, user_id, text)
            return
    
    # Komandalar
    if text == '/start':
        handle_start(chat_id, user_id, first_name)
    elif text == "📚 Savollar" and user_id == ADMIN_ID:
        handle_admin_questions(chat_id)
    elif text == "📝 Test ishlash":
        start_test(chat_id, user_id)
    elif text == "💬 Gemini AI":
        send_message(chat_id, "💬 Biologiya yoki kimyo bo'yicha savolingizni yozing:")
    elif text == "📊 Mening natijalarim":
        show_user_stats(chat_id, user_id)
    elif text == "📊 Statistika" and user_id == ADMIN_ID:
        show_admin_stats(chat_id)
    else:
        # Gemini savol
        handle_gemini_question(chat_id, user_id, text)

def handle_callback(callback):
    chat_id = callback['message']['chat']['id']
    user_id = callback['from']['id']
    data = callback['data']
    callback_id = callback['id']
    
    answer_callback(callback_id)
    
    if data == "add_question":
        handle_add_question(chat_id, user_id)
    elif data == "list_questions":
        handle_list_questions(chat_id)
    elif data == "delete_question":
        handle_delete_question(chat_id, user_id)
    elif data.startswith("answer_"):
        answer = data.replace("answer_", "")
        handle_test_answer(chat_id, user_id, answer)

# ============ ASOSIY LOOP ============
def main():
    print("🤖 Bot ishga tushdi...")
    offset = 0
    
    while True:
        try:
            updates = get_updates(offset)
            
            for update in updates:
                offset = update['update_id'] + 1
                
                if 'message' in update:
                    handle_message(update['message'])
                elif 'callback_query' in update:
                    handle_callback(update['callback_query'])
        
        except KeyboardInterrupt:
            print("\n🛑 Bot to'xtatildi.")
            break
        except Exception as e:
            print(f"❌ Xato: {e}")
            time.sleep(3)

if __name__ == '__main__':
    main()