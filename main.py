from fastapi import FastAPI, Request
from database import get_or_create_user, update_user_state
from evolution import send_whatsapp_message
from ai_handler import (
    get_placement_test, get_flutter_lesson, 
    correct_code_and_explain, logic_to_code, generate_ai_response
)

app = FastAPI(title="Flutter AI Tutor Bot")

@app.post("/webhook")
async def evolution_webhook(request: Request):
    payload = await request.json()
    
    # التأكد من أن الحدث هو حدث استقبال رسالة
    event_type = payload.get("event")
    if event_type != "messages.upsert":
        return {"status": "ignored"}

    data = payload.get("data", {})
    message_info = data.get("message", {})
    
    if not message_info:
        return {"status": "ok"}
    
    remote_jid = data.get("key", {}).get("remoteJid", "")
    # تجاهل رسائل المجموعة وحالة النظام
    if "status" in remote_jid or "g.us" in remote_jid:
        return {"status": "ok"}
    
    # جلب النص
    # Evolution API قد يرسل النص تحت مفاتيح مختلفة بناء على نوع الرسالة
    conversation = message_info.get("conversation")
    extended_msg = message_info.get("extendedTextMessage", {}).get("text")
    incoming_text = conversation or extended_msg
    
    # في حالة لم يكن هناك نص
    if not incoming_text:
        return {"status": "ok"}
        
    sender_name = data.get("pushName", "Student")
    phone_number = remote_jid.split("@")[0]
    
    # 1. تسجيل / جلب بيانات المستخدم
    user = get_or_create_user(phone_number, sender_name)
    current_state = user.get("current_state", "new")
    level = user.get("level", 0)
    points = user.get("points", 0)
    
    response_text = ""
    
    # تحكم بناءً على الحالة (State Machine البسيطة)
    if "كود" in incoming_text or "خطأ" in incoming_text or "حول" in incoming_text:
        # التعامل مع طلبات التصحيح أو تحويل المنطق إلى كود (النقاط 5 ، 6 ، 7)
        if "خطأ" in incoming_text:
            response_text = correct_code_and_explain(incoming_text, "يواجه خطأ برمجي")
        elif "حول" in incoming_text:
            response_text = logic_to_code(incoming_text)
        else:
            # مساعدة عامة في الكود
            response_text = generate_ai_response(f"الطالب يسأل عن كود: {incoming_text}. قم بمساعدته برمجياً وشرح التفاصيل.")
            
    elif current_state == "new":
        # 2. تحديد مستوى
        response_text = f"أهلاً المنقذ والمبرمج المستقبلي {sender_name}! \nأنا بوت الذكاء الاصطناعي لتعليم Flutter. \nسنبدأ باختبار تحديد المستوى 🚀\n\n"
        response_text += get_placement_test()
        update_user_state(phone_number, "assessing")
        
    elif current_state == "assessing":
        # الرد على اختبار تحديد المستوى (تغيير المستوى والنقاط)
        # سيقوم الذكاء بتقييم اجابته واعطاء مستوى 1 مبدئياً ومسار التعليم
        evaluation = generate_ai_response(f"الطالب أجاب على اختبار تحديد المستوى بـ: '{incoming_text}'. أعطه تقييماً سريعاً وأخبره أنه سيبدأ من المستوى 1.")
        response_text = f"ممتاز! 💪 كسبت 10 نقاط\n{evaluation}\n\n للبدء بالدرس الأول، اكتب 'درس'."
        update_user_state(phone_number, "learning", level=1, points_to_add=10)
        
    elif current_state == "learning":
        if "درس" in incoming_text:
            # 3. إعطاء دروس حسب المستوى 
            response_text = get_flutter_lesson(level)
            response_text += "\n\n💡 (كسبت 5 نقاط لقراءة الدرس) \nاستعد للاختبار بعد قليل! اكتب 'اختبار' عندما تكون جاهزاً."
            update_user_state(phone_number, "ready_for_quiz", points_to_add=5)
        elif "نقاطي" in incoming_text:
             response_text = f"🌟 مجموع نقاطك: {points} نقطة!"
        else:
            response_text = "اكتب 'درس' للحصول على درسك التالي، أو 'نقاطي' للتحقق من نقاطك."
            
    elif current_state == "ready_for_quiz":
        if "اختبار" in incoming_text:
            # 4. إجراء اختبار بعد كل درس
            response_text = generate_ai_response("أعط الطالب سؤال اختيار من متعدد بناء على مستواه في Flutter. واطلب منه الرد بالحل.")
            update_user_state(phone_number, "quiz_answering")
        else:
            response_text = "اكتب 'اختبار' لاختبار معلوماتك!"
            
    elif current_state == "quiz_answering":
        # 8 & 9. تقييم الاختبار وتغيير المسار واضافة نقاط التلعيب
        ai_eval = generate_ai_response(f"الطالب ذو المستوى {level} جاوب على اختبار بـ '{incoming_text}'. هل إجابته صحيحة؟ إذا صحيحة امدحه واطلب منه كتابة 'درس' للانتقال. إذا خاطئة، اشرح له الخطأ بلطف واطلب منه إعادة المحاولة.")
        
        response_text = ai_eval
        if "صحيح" in ai_eval or "أحسنت" in ai_eval or "ممتاز" in ai_eval:
             response_text += "\n\n🏆 لقد حصلت على 20 نقطة إضافية! اكتب 'درس' للانتقال للدرس التالي."
             update_user_state(phone_number, "learning", level=level+1, points_to_add=20)
        else:
             response_text += "\n\nلا بأس يا بطل، المحاولة هي طريق النجاح! 💪"
             update_user_state(phone_number, "learning") # إعادته لقراءة الدرس
             
    else:
        response_text = "مرحباً مجدداً! اكتب 'درس' للبدء."


    # إرسال الرسالة أخيراً لـ Evolution API
    send_whatsapp_message(remote_jid, response_text)
    
    return {"status": "success"}

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
