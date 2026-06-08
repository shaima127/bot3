import os
from groq import Groq
from config import settings

# تهيئة Groq كمولد للذكاء الاصطناعي
client = Groq(api_key=settings.GROQ_API_KEY)

import re
import tempfile
import base64

def generate_ai_response(prompt: str, system_prompt: str = "أنت معلم فلاتر (Flutter) خبير، تعليمك عربي وممتع. أوامرك صارمة: تجيب فقط بما يخص Flutter و Dart وتعتذر بلطف عن غيرها. ملاحظة قوية: لا تكرر الترحيب بالطالب أبداً (لا تقل أهلاً ومرحباً في كل مرة)، اجعل ردودك مباشرة، وتفاعل معه بلطف وبدون رسميات زائدة."):
    """
    دالة موحدة للاتصال بالذكاء الاصطناعي
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # تم تحديث الموديل لأن القديم تم إيقافه من شركة Groq
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        raw_text = completion.choices[0].message.content
        
        # تنظيف الرموز الخاصة بالذكاء الاصطناعي (Markdown) لتتناسب مع خطوط الواتساب
        # تحويل الخط العريض **كلمة** إلى *كلمة* الخاص بالواتساب
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', raw_text)
        # إزالة رموز العناوين ### أو ##
        clean_text = re.sub(r'#{1,6}\s*', '', clean_text)
        
        return clean_text
    except Exception as e:
        print(f"Error from Groq AI: {e}")
        return "عذراً، أواجه مشكلة في التفكير حالياً. الرجاء المحاولة مرة أخرى."

def transcribe_audio(base64_audio: str):
    """
    تحويل الصوت إلى نص باستخدام Groq Whisper
    """
    try:
        audio_data = base64.b64decode(base64_audio)
        
        # حفظ الملف مؤقتاً بصيغة ogg
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
            temp_audio.write(audio_data)
            temp_file_path = temp_audio.name
            
        with open(temp_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_file_path, file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
            )
        
        os.remove(temp_file_path)
        return transcription.text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

def get_placement_test():
    prompt = "اكتب سؤالاً واحداً فقط بلغة عربية لتحديد مستوى الطالب في Flutter (اختيارات متعددة)، بحيث يمكنني تحديد مستواه المبتدئ، المتوسط، أو المتقدم."
    return generate_ai_response(prompt)

from database import retrieve_relevant_lesson
import httpx

# ─── مواضيع Flutter الرسمية حسب رقم الدرس ───
FLUTTER_DOC_TOPICS = {
    1: "https://docs.flutter.dev/get-started/install",
    2: "https://dart.dev/language",
    3: "https://docs.flutter.dev/get-started/codelab",
    4: "https://docs.flutter.dev/ui/widgets",
    5: "https://docs.flutter.dev/ui/interactivity",
    6: "https://docs.flutter.dev/cookbook/navigation/navigation-basics",
    7: "https://docs.flutter.dev/cookbook/networking/fetch-data",
}


def fetch_from_flutter_docs(lesson_number: int) -> str:
    """
    يجلب معلومات من موقع Flutter الرسمي كخطة بديلة.
    يحاول قراءة محتوى الصفحة وتلخيصه.
    """
    url = FLUTTER_DOC_TOPICS.get(lesson_number, "https://docs.flutter.dev/get-started/install")
    try:
        response = httpx.get(url, timeout=10.0, follow_redirects=True)
        if response.status_code == 200:
            # نأخذ أول 2000 حرف من الصفحة (نص خام)
            import re
            text = re.sub(r'<[^>]+>', ' ', response.text)  # إزالة HTML tags
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:2000]
    except Exception as e:
        print(f"⚠️ فشل جلب من Flutter docs: {e}")
    return ""


def get_flutter_lesson(level: int, lesson_number: int = None):
    """
    1. يبحث في قاعدة البيانات أولاً (برقم الدرس أو المستوى)
    2. إذا لم يجد → يجلب من موقع Flutter الرسمي
    3. يصيغ المحتوى بأسلوب ممتع عبر الذكاء الاصطناعي
    """
    # الخطوة 1: البحث في قاعدة البيانات
    db_lesson = retrieve_relevant_lesson(level, lesson_number=lesson_number)

    if db_lesson:
        prompt = (
            f"هذا محتوى الدرس من المنهج:\n'{db_lesson}'\n\n"
            f"صِغه للطالب (مستوى {level}) بأسلوب ممتع وتشجيعي مع أمثلة كود."
        )
        return generate_ai_response(prompt)

    # الخطوة 2: جلب من موقع Flutter الرسمي
    print(f"📡 الدرس غير موجود في الداتابيز — جاري البحث في موقع Flutter الرسمي...")
    flutter_content = fetch_from_flutter_docs(lesson_number or level)

    if flutter_content:
        prompt = (
            f"جلبت هذا المحتوى من موقع Flutter الرسمي:\n'{flutter_content}'\n\n"
            f"حوّله إلى درس عربي ممتع للطالب (مستوى {level}). "
            f"أضف أمثلة كود مبسطة وكلمات تشجيعية."
        )
        return generate_ai_response(prompt)

    # الخطوة 3: خطة بديلة أخيرة — AI يولّد الدرس
    prompt = (
        f"أعطني درساً قصيراً لتعلم Flutter يناسب المستوى {level}، "
        f"الدرس رقم {lesson_number or '؟'}. "
        f"مع مثال كود مبسط وكلمات تشجيعية."
    )
    return generate_ai_response(prompt)


def get_lesson_quiz(lesson_topic: str):
    prompt = f"بناءً على موضوع '{lesson_topic}' في فلاتر، أعطني سؤالاً قصيراً جداً لتقييم فهم الطالب مع 3 خيارات."
    return generate_ai_response(prompt)

def correct_code_and_explain(code: str, issue: str):
    prompt = f"الطالب يواجه مشكلة: '{issue}' في هذا الكود: \n{code}\n الرجاء تصحيح الكود وشرح المشكلة بالتفصيل باللغة العربية."
    return generate_ai_response(prompt)

def logic_to_code(logic_description: str):
    prompt = f"الطالب يطلب تحويل المنطق التالي إلى كود Flutter: \n{logic_description}\n يرجى كتابة الكود المناسب مع وضع شروحات داخل الكود (Comments)."
    return generate_ai_response(prompt)

