import os
from groq import Groq
from config import settings

# تهيئة Groq كمولد للذكاء الاصطناعي
client = Groq(api_key=settings.GROQ_API_KEY)

def generate_ai_response(prompt: str, system_prompt: str = "أنت معلم فلاتر (Flutter) خبير، تقوم بتعليم الطلاب باللغة العربية بأسلوب ممتع ومشجع."):
    \"\"\"
    دالة موحدة للاتصال بالذكاء الاصطناعي
    \"\"\"
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192", # يمكنك تغييره بناءً على ما تفضله
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
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error from Groq AI: {e}")
        return "عذراً، أواجه مشكلة في التفكير حالياً. الرجاء المحاولة مرة أخرى."

def get_placement_test():
    prompt = "اكتب سؤالاً واحداً فقط بلغة عربية لتحديد مستوى الطالب في Flutter (اختيارات متعددة)، بحيث يمكنني تحديد مستواه المبتدئ، المتوسط، أو المتقدم."
    return generate_ai_response(prompt)

from database import retrieve_relevant_lesson

def get_flutter_lesson(level: int):
    # 1. جلب الدرس المخزن من قاعدة البيانات بواسطة RAG
    db_lesson_content = retrieve_relevant_lesson(level)
    
    if db_lesson_content:
        # 2. إعطاء الذكاء الاصطناعي محتوى الدرس ليقوم بصياغته بشكل محفز وأكاديمي
        prompt = f"هذا هو محتوى الدرس من المنهج الخاص بي: \n'{db_lesson_content}'\n الرجاء صياغته وشرحه للطالب ذو المستوى {level} بأسلوب ممتع مع استخدام كلمات تشجيعية وعمل مثال كود (Gamification)."
    else:
        # في حال لم يتم العثور على درس في الداتا بيز (خطة بديلة)
        prompt = f"أعطني درساً قصيراً لتعلم Flutter يناسب الطالب ذو المستوى {level}، مع مثال كود صغير ومبسط. استخدم Gamification بإضافة كلمات تشجيعية."
        
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
