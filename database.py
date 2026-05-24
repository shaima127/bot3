import os
import httpx
from supabase import create_client, Client
from config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_embedding(text: str) -> list:
    \"\"\"
    تحويل النص إلى متجهات (Embedding) باستخدام HuggingFace.
    (يخفف الضغط عن الاستضافة بدلاً من تثبيت مكتبات الذكاء الاصطناعي الثقيلة محلياً)
    \"\"\"
    model_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"}
    try:
        response = httpx.post(model_url, headers=headers, json={"inputs": text}, timeout=10.0)
        # HuggingFace يُرجع مصفوفة من المتجهات
        return response.json()
    except Exception as e:
        print("Error getting embedding:", e)
        return []

def retrieve_relevant_lesson(level: int, limit: int = 1) -> str:
    \"\"\"
    البحث في الدروس المخزنة في Supabase باستخدام RAG (Vector Search)
    نبحث عن الدرس الذي يناسب مستوى الطالب.
    \"\"\"
    # تجهيز النص المراد البحث عنه بناء على المستوى
    query = f"درس برمجة فلاتر Flutter مناسب للطالب في المستوى رقم {level}"
    query_embedding = get_embedding(query)
    
    if not query_embedding:
        return ""
    
    # استدعاء دالة RPC من قاعدة بيانات Supabase (تحتاج إنشاءها لاحقاً في SQL)
    try:
        response = supabase.rpc("match_lessons", {
            "query_embedding": query_embedding,
            "match_threshold": 0.5, # قوة التطابق
            "match_count": limit,
            "student_level": level # فلترة إضافية لمستوى الطالب إن أمكن
        }).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['content'] # إعادة نص الدرس من قاعدة البيانات
    except Exception as e:
        print("Error fetching from supabase vectors:", e)
        
    return ""

def get_or_create_user(phone_number: str, name: str = "Student"):
    \"\"\"
    يقوم بالبحث عن المستخدم، إن لم يجده يقوم بتسجيله.
    \"\"\"
    response = supabase.table("students").select("*").eq("phone_number", phone_number).execute()
    
    if len(response.data) > 0:
        return response.data[0]
    
    new_user = {
        "phone_number": phone_number,
        "name": name,
        "level": 0,
        "points": 0,
        "current_state": "new"
    }
    insert_response = supabase.table("students").insert(new_user).execute()
    return insert_response.data[0]

def update_user_state(phone_number: str, new_state: str, level: int = None, points_to_add: int = 0):
    update_data = {"current_state": new_state}
    if level is not None:
        update_data["level"] = level
    
    if points_to_add > 0:
        current_points = supabase.table("students").select("points").eq("phone_number", phone_number).execute().data[0]['points']
        update_data["points"] = current_points + points_to_add

    res = supabase.table("students").update(update_data).eq("phone_number", phone_number).execute()
    return res.data[0] if res.data else None
