import asyncio
from database import supabase, get_embedding

def insert_single_lesson():
    print("=== إضافة درس بتقنية RAG لقاعدة البيانات ===")
    level = int(input("أدخل مستوى الدرس (رقم من 1 إلى 5): "))
    content = input("أدخل محتوى الدرس (النص والشرح الذي تريده): ")
        
    print("🤖 جاري تحويل الدرس لـ متجهات (Vectors) ليعمل عبر الـ RAG الذكي...")
    embedding = get_embedding(content)
    
    if not embedding:
        print("❌ فشل الاتصال بخادم الذكاء الاصطناعي.. سيتم حفظ الدرس كنص عادي ولن يعمل بنظام الـ RAG.")
        lesson_data = {"level": level, "content": content}
    else:
        lesson_data = {"level": level, "content": content, "embedding": embedding}
    
    try:
        supabase.table("lessons").insert(lesson_data).execute()
        print("✅ تم حفظ الدرس بنجاح في قاعدة البيانات!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الحفظ: {e}")

if __name__ == "__main__":
    insert_single_lesson()
