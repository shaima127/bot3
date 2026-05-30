from fastapi import FastAPI, Request
from database import get_or_create_user, update_user_state
from evolution import send_whatsapp_message
from ai_handler import (
    get_placement_test, get_flutter_lesson, 
    correct_code_and_explain, logic_to_code, generate_ai_response
)

app = FastAPI(title="Flutter AI Tutor Bot")

from fastapi import BackgroundTasks

@app.post("/webhook")
@app.post("/")
async def evolution_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    print("====================================")
    print("🔔 استلام Webhook من الواتساب:")
    # يتم تحويل المعالجة إلى الخلفية (Background) حتى لا ينتظر الواتساب ويتسبب بمشاكل وتداخل
    background_tasks.add_task(process_message, payload)
    return {"status": "success"}

def process_message(payload: dict):
    # التأكد من أن الحدث هو حدث استقبال رسالة
    event_type = payload.get("event")
    if event_type != "messages.upsert":
        return

    data = payload.get("data", {})
    message_info = data.get("message", {})
    
    if not message_info:
        return
    
    remote_jid = data.get("key", {}).get("remoteJid", "")
    from_me = data.get("key", {}).get("fromMe", False)
    
    # حماية من رقم فارغ أو رسائل المجموعات والنظام ورسائل البوت نفسه
    if not remote_jid or "status" in remote_jid or "g.us" in remote_jid or from_me:
        return
    
    # جلب النص
    conversation = message_info.get("conversation")
    extended_msg = message_info.get("extendedTextMessage", {}).get("text")
    incoming_text = conversation or extended_msg
    
    if not incoming_text:
        return
        
    sender_name = data.get("pushName", "Student")
    phone_number = str(remote_jid).split("@")[0]
    
    # 1. جلب أو تسجيل بيانات المستخدم بناء على رقمه فقط
    user = get_or_create_user(phone_number, sender_name)
    current_state = user.get("current_state", "new")
    level = user.get("level", 0)
    points = user.get("points", 0)
    
    response_text = ""
    
    if "كود" in incoming_text or "خطأ" in incoming_text or "حول" in incoming_text:
        if "خطأ" in incoming_text:
            response_text = correct_code_and_explain(incoming_text, "يواجه خطأ برمجي")
        elif "حول" in incoming_text:
            response_text = logic_to_code(incoming_text)
        else:
            response_text = generate_ai_response(f"الطالب يسأل عن كود: {incoming_text}. قم بمساعدته برمجياً وشرح التفاصيل.")
            
    elif current_state == "new":
        response_text = f"مرحباً بك يا {sender_name}! 🌟 سعيد جداً بانضمامك لعالم Flutter الممتع.\nخبرني يا بطل، ما هو مستواك الحالي في برمجة الفلاتر؟\n\n1️⃣ مبتدئ جداً (أريد البدء من الصفر)\n2️⃣ أعرف الأساسيات\n3️⃣ متوسط (أريد الاحتراف)\n\nأرسل لي رقم مستواك لنبدأ مشوارنا معاً 🚀"
        update_user_state(phone_number, "assessing")
        
    elif current_state == "assessing":
        if "1" in incoming_text or "مبتدئ" in incoming_text:
            assigned_level = 1
        elif "2" in incoming_text or "اساسيات" in incoming_text or "أساسيات" in incoming_text:
            assigned_level = 2
        elif "3" in incoming_text or "متوسط" in incoming_text or "محترف" in incoming_text:
            assigned_level = 3
        else:
            assigned_level = 1
            
        evaluation = generate_ai_response(f"الطالب {sender_name} أخبرك أن مستواه رقم {assigned_level}. رد عليه بسطر أو سطرين بلطف وود شديد رحب به للبدء بالمستوى المختار، ولا تسأله أسئلة إضافية.")
        response_text = f"تم تسجيل مستواك بنجاح! 💪 كسبت 10 نقاط\n\n{evaluation}\n\n💡 للبدء فورا والاستمتاع، أرسل كلمة 'درس'."
        update_user_state(phone_number, "learning", level=assigned_level, points_to_add=10)
        
    elif current_state == "learning":
        if "درس" in incoming_text:
            response_text = get_flutter_lesson(level)
            response_text += "\n\n💡 (كسبت 5 نقاط لقراءة الدرس) \nاستعد للاختبار بعد قليل! اكتب 'اختبار' عندما تكون جاهزاً."
            update_user_state(phone_number, "ready_for_quiz", points_to_add=5)
        elif "نقاطي" in incoming_text:
             response_text = f"🌟 مجموع نقاطك: {points} نقطة!"
        else:
            response_text = "اكتب 'درس' للحصول على درسك التالي، أو 'نقاطي' للتحقق من نقاطك."
            
    elif current_state == "ready_for_quiz":
        if "اختبار" in incoming_text:
            response_text = generate_ai_response("أعط الطالب سؤال اختيار من متعدد بناء على مستواه في Flutter. واطلب منه الرد بالحل.")
            update_user_state(phone_number, "quiz_answering")
        else:
            response_text = "اكتب 'اختبار' لاختبار معلوماتك!"
            
    elif current_state == "quiz_answering":
        ai_eval = generate_ai_response(f"الطالب ذو المستوى {level} جاوب على اختبار بـ '{incoming_text}'. هل إجابته صحيحة؟ إذا صحيحة امدحه واطلب منه كتابة 'درس' للانتقال. إذا خاطئة، اشرح له الخطأ بلطف واطلب منه إعادة المحاولة.")
        
        response_text = ai_eval
        if "صحيح" in ai_eval or "أحسنت" in ai_eval or "ممتاز" in ai_eval:
             response_text += "\n\n🏆 لقد حصلت على 20 نقطة إضافية! اكتب 'درس' للانتقال للدرس التالي."
             update_user_state(phone_number, "learning", level=level+1, points_to_add=20)
        else:
             response_text += "\n\nلا بأس يا بطل، المحاولة هي طريق النجاح! 💪"
             update_user_state(phone_number, "learning")
             
    else:
        response_text = "مرحباً مجدداً! اكتب 'درس' للبدء."

    # إرسال الرسالة أخيراً لـ Evolution API
    send_whatsapp_message(remote_jid, response_text)

# واجهة بسيطة للأدمن 
# 10. وجود نظام مراقبة يتيح للأدمن تتبع الأداء
@app.get("/admin/stats")
def get_admin_stats():
    from database import supabase
    res = supabase.table("students").select("*").execute()
    students = res.data if res.data else []
    total_students = len(students)
    total_points = sum([s['points'] for s in students if isinstance(s['points'], int)])
    
    return {
        "total_students": total_students,
        "total_points_earned": total_points,
        "students_data": students
    }
