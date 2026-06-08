from fastapi import FastAPI, Request, BackgroundTasks
from database import get_or_create_user, update_user_state, save_last_lesson, get_next_lesson_number, increment_lessons_completed
from evolution import send_whatsapp_message, get_media_base64
from ai_handler import (
    get_flutter_lesson,
    correct_code_and_explain, logic_to_code, generate_ai_response,
    transcribe_audio
)
import httpx, base64, tempfile, os

app = FastAPI(title="Flutter AI Tutor Bot")


# ─────────────────────────────────────────
#  مساعد: جلب الصوت وتحويله نصاً
# ─────────────────────────────────────────
def extract_audio_text(data: dict, message_info: dict, remote_jid: str) -> str:
    """
    يحاول جلب صوت الرسالة وتحويله نصاً.
    يجرب أولاً Evolution API ثم تحميل مباشر.
    """
    print("🎤 رسالة صوتية — جاري التحويل إلى نص...")

    # الطريقة 1: عبر Evolution API
    try:
        base64_audio = get_media_base64(message_info)
        if base64_audio:
            text = transcribe_audio(base64_audio)
            if text:
                print(f"📝 النص (Evolution): {text}")
                return text
    except Exception as e:
        print(f"⚠️ Evolution base64 failed: {e}")

    # الطريقة 2: تحميل مباشر من URL
    try:
        audio_url = message_info.get("audioMessage", {}).get("url", "")
        if audio_url:
            resp = httpx.get(audio_url, timeout=15.0)
            if resp.status_code == 200:
                audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                text = transcribe_audio(audio_b64)
                if text:
                    print(f"📝 النص (direct): {text}")
                    return text
    except Exception as e:
        print(f"⚠️ Direct download failed: {e}")

    return ""


# ─────────────────────────────────────────
#  Webhook الرئيسي
# ─────────────────────────────────────────
@app.post("/webhook")
@app.post("/")
async def evolution_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    print("====================================")
    print("🔔 استلام Webhook:")
    background_tasks.add_task(process_message, payload)
    return {"status": "success"}


# ─────────────────────────────────────────
#  منطق معالجة الرسائل
# ─────────────────────────────────────────
def process_message(payload: dict):
    event_type = payload.get("event")
    if event_type != "messages.upsert":
        return

    data = payload.get("data", {})
    message_info = data.get("message", {})

    if not message_info:
        return

    remote_jid = data.get("key", {}).get("remoteJid", "")
    from_me = data.get("key", {}).get("fromMe", False)

    # تجاهل رسائل المجموعات والنظام والبوت نفسه
    if not remote_jid or "status" in remote_jid or "g.us" in remote_jid or from_me:
        return

    # ── جلب النص من الرسالة ──
    conversation = message_info.get("conversation")
    extended_msg = message_info.get("extendedTextMessage", {}).get("text")
    incoming_text = conversation or extended_msg

    # ── إذا لم يوجد نص، تحقق من وجود صوت ──
    if not incoming_text:
        audio_info = message_info.get("audioMessage")
        if audio_info:
            incoming_text = extract_audio_text(data, message_info, remote_jid)
            if not incoming_text:
                send_whatsapp_message(
                    remote_jid,
                    "عذراً، لم أتمكن من فهم الرسالة الصوتية 🎙️\n"
                    "جرب إعادة التسجيل بصوت واضح، أو اكتب رسالتك نصياً."
                )
                return
        else:
            # رسالة من نوع آخر (صورة، ملف...) — تجاهل
            return

    sender_name = data.get("pushName") or "صديقي"
    phone_number = str(remote_jid).split("@")[0]

    # ── جلب أو إنشاء ملف الطالب ──
    user = get_or_create_user(phone_number, sender_name)
    current_state = user.get("current_state", "new")
    level = user.get("level", 1)
    points = user.get("points", 0)
    last_lesson = user.get("last_lesson", "")

    response_text = ""

    # ── أولوية: أسئلة الكود بأي حالة ──
    lower_text = incoming_text.lower()
    if "كود" in incoming_text or "خطأ" in incoming_text or "error" in lower_text or "حول" in incoming_text:
        if "خطأ" in incoming_text or "error" in lower_text:
            response_text = correct_code_and_explain(incoming_text, "يواجه خطأ برمجي")
        elif "حول" in incoming_text:
            response_text = logic_to_code(incoming_text)
        else:
            response_text = generate_ai_response(
                f"الطالب يسأل عن كود Flutter: {incoming_text}. ساعده وشرح التفاصيل."
            )

    # ══ رسالة جديدة: ترحيب حار ثم سؤال المستوى مباشرة ══
    elif current_state == "new":
        first_name = sender_name.split()[0] if sender_name else "صديقي"
        response_text = (
            f"أهلاً وسهلاً يا {first_name}! 🌟\n"
            f"أنا بوت تعليم Flutter، وسأكون معلمك في رحلتك نحو الاحتراف 🚀\n\n"
            f"قبل ما نبدأ، أخبرني: ما مستواك الحالي في Flutter؟\n\n"
            f"1️⃣ مبتدئ — أبدأ من الصفر\n"
            f"2️⃣ أساسيات — أعرف الأساسيات\n"
            f"3️⃣ متوسط — أريد الاحتراف\n\n"
            f"أرسل رقم مستواك لنبدأ مشوارنا 💪"
        )
        update_user_state(phone_number, "assessing")

    # ══ تحديد المستوى ══
    elif current_state == "assessing":
        if "1" in incoming_text or "مبتدئ" in incoming_text or "صفر" in incoming_text:
            assigned_level = 1
            level_name = "المبتدئ"
        elif "2" in incoming_text or "اساسيات" in incoming_text or "أساسيات" in incoming_text:
            assigned_level = 2
            level_name = "الأساسيات"
        elif "3" in incoming_text or "متوسط" in incoming_text or "احتراف" in incoming_text:
            assigned_level = 3
            level_name = "المتوسط"
        else:
            assigned_level = 1
            level_name = "المبتدئ"

        first_name = sender_name.split()[0] if sender_name else "صديقي"
        response_text = (
            f"ممتاز يا {first_name}! 💪 تم تسجيل مستواك: *{level_name}*\n"
            f"🎉 كسبت 10 نقاط كبداية!\n\n"
            f"عندما تكون جاهزاً اكتب: *درس* لتبدأ درسك الأول 📚"
        )
        update_user_state(phone_number, "learning", level=assigned_level, points_to_add=10)

    # ══ حالة التعلم ══
    elif current_state == "learning":
        if "درس" in incoming_text:
            # حساب رقم الدرس التالي للطالب
            next_lesson = get_next_lesson_number(phone_number)
            lesson_content = get_flutter_lesson(level, lesson_number=next_lesson)
            response_text = f"📖 *الدرس رقم {next_lesson}*\n\n"
            response_text += lesson_content
            response_text += "\n\n⭐ (كسبت 5 نقاط)\nاكتب *اختبار* عندما تكون جاهزاً للتحدي!"
            increment_lessons_completed(phone_number)
            update_user_state(phone_number, "ready_for_quiz", points_to_add=5, last_lesson=lesson_content[:300])
        elif "نقاطي" in incoming_text:
            response_text = f"🌟 رصيدك الحالي: *{points}* نقطة!"
        elif "ذاكرة" in incoming_text or "آخر درس" in incoming_text or "اخر درس" in incoming_text:
            if last_lesson:
                response_text = f"📚 آخر درس تعلمته:\n\n{last_lesson}\n\nاكتب *درس* للمتابعة."
            else:
                response_text = "لم تدرس أي درس بعد! اكتب *درس* لتبدأ 🚀"
        else:
            response_text = generate_ai_response(
                f"الطالب في مرحلة التعلم، مستواه {level}، قال: '{incoming_text}'.\n"
                f"رد عليه مباشرة وبلطف، وذكره في النهاية بأنه يستطيع كتابة 'درس' لمواصلة التعلم."
            )

    # ══ جاهز للاختبار ══
    elif current_state == "ready_for_quiz":
        if "اختبار" in incoming_text:
            ai_question = generate_ai_response(
                f"الطالب مستواه {level}. أعطه سؤال اختيار من متعدد واحد فقط عن Flutter."
            )
            response_text = ai_question
            update_user_state(phone_number, f"quiz_answering|{ai_question}")
        else:
            response_text = generate_ai_response(
                f"الطالب قال: '{incoming_text}'. رد عليه باختصار وذكره بكتابة 'اختبار' للبدء."
            )

    # ══ الإجابة على الاختبار ══
    elif current_state.startswith("quiz_answering"):
        parts = current_state.split("|", 1)
        last_question = parts[1] if len(parts) > 1 else "سؤال غير معروف"

        prompt = (
            f"السؤال الذي طرحته: '{last_question}'\n"
            f"إجابة الطالب: '{incoming_text}'.\n"
            f"قيّم الإجابة بصدق. إن كانت صحيحة استخدم كلمة 'صحيح' أو 'ممتاز'. "
            f"إن كانت خاطئة اشرح الجواب بلطف."
        )
        ai_eval = generate_ai_response(prompt)
        response_text = ai_eval

        if any(w in ai_eval for w in ["صحيح", "أحسنت", "ممتاز", "رائع", "بالضبط"]):
            response_text += "\n\n🏆 حصلت على 20 نقطة! اكتب *درس* للانتقال للدرس التالي."
            update_user_state(phone_number, "learning", level=level + 1, points_to_add=20)
        else:
            response_text += "\n\nلا بأس، المحاولة طريق النجاح! 💪 اكتب *درس* لمراجعة الدرس."
            update_user_state(phone_number, "learning")

    # ══ حالة غير معروفة ══
    else:
        response_text = generate_ai_response(
            f"الطالب قال: '{incoming_text}'. رد عليه مباشرة وذكره بكتابة 'درس' للعودة للتعلم."
        )

    if response_text:
        send_whatsapp_message(remote_jid, response_text)


# ─────────────────────────────────────────
#  لوحة الأدمن
# ─────────────────────────────────────────
@app.get("/admin/stats")
def get_admin_stats():
    from database import supabase
    res = supabase.table("students").select("*").execute()
    students = res.data if res.data else []
    total_points = sum(s.get("points", 0) for s in students if isinstance(s.get("points"), int))
    return {
        "total_students": len(students),
        "total_points_earned": total_points,
        "students_data": students
    }
