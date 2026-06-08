import os
import httpx
from supabase import create_client, Client
from config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

import httpx

def get_embedding(text: str) -> list:
    """
    تحويل النص إلى متجهات (Embedding) لعمل RAG حقيقي.
    نستخدم نموذجاً مجانياً ومفتوحاً من HuggingFace.
    """
    model_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
    
    headers = {}
    if hasattr(settings, "HUGGINGFACE_TOKEN") and settings.HUGGINGFACE_TOKEN:
        headers["Authorization"] = f"Bearer {settings.HUGGINGFACE_TOKEN}"
        
    try:
        response = httpx.post(model_url, headers=headers, json={"inputs": text}, timeout=10.0)
        result = response.json()
        # تنسيق المتجهات
        if isinstance(result, list) and len(result) > 0:
            return result[0] if isinstance(result[0], list) else result
        return []
    except Exception as e:
        print("Error getting embedding:", e)
        return []

def retrieve_relevant_lesson(level: int, lesson_number: int = None, limit: int = 1) -> str:
    """
    تطبيق تقنية RAG الحقيقية للبحث (Vector Semantic Search) داخل قاعدة البيانات.
    إذا وُجد lesson_number يبحث به أولاً.
    """
    # الطريقة 1: بحث برقم الدرس مباشرة
    if lesson_number:
        try:
            response = supabase.table("lessons").select("content, title").eq("lesson_number", lesson_number).limit(1).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]['content']
        except Exception as e:
            print(f"⚠️ خطأ في البحث برقم الدرس: {e}")

    # الطريقة 2: بحث بالمستوى
    try:
        response = supabase.table("lessons").select("content, title").eq("level", level).order("lesson_number").limit(limit).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['content']
    except Exception as e:
        print(f"⚠️ خطأ في البحث بالمستوى: {e}")

    # الطريقة 3: RAG بالمتجهات
    query = f"درس برمجة فلاتر Flutter مناسب للطالب في المستوى رقم {level}"
    query_embedding = get_embedding(query)

    if not query_embedding:
        return ""

    try:
        response = supabase.rpc("match_lessons", {
            "query_embedding": query_embedding,
            "match_threshold": 0.1,
            "match_count": limit,
            "student_level": level
        }).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]['content']
    except Exception as e:
        print("Error with Supabase Vectors:", e)

    return ""


def get_next_lesson_number(phone_number: str) -> int:
    """
    يحسب رقم الدرس التالي للطالب بناءً على مستواه.
    """
    try:
        user = supabase.table("students").select("level, lessons_completed").eq("phone_number", phone_number).execute()
        if user.data and len(user.data) > 0:
            completed = user.data[0].get("lessons_completed", 0)
            return completed + 1
    except:
        pass
    return 1


def increment_lessons_completed(phone_number: str):
    """
    يزيد عداد الدروس المكتملة بـ 1.
    """
    try:
        user = supabase.table("students").select("lessons_completed").eq("phone_number", phone_number).execute()
        current = user.data[0].get("lessons_completed", 0) if user.data else 0
        supabase.table("students").update({"lessons_completed": current + 1}).eq("phone_number", phone_number).execute()
    except Exception as e:
        print(f"Error incrementing lessons_completed: {e}")

def get_or_create_user(phone_number: str, name: str = "Student"):
    """
    يقوم بالبحث عن المستخدم، إن لم يجده يقوم بتسجيله.
    """
    response = supabase.table("students").select("*").eq("phone_number", phone_number).execute()
    
    if len(response.data) > 0:
        return response.data[0]
    
    new_user = {
        "phone_number": phone_number,
        "name": name,
        "level": 0,
        "points": 0,
        "current_state": "new",
        "last_lesson": ""
    }
    insert_response = supabase.table("students").insert(new_user).execute()
    return insert_response.data[0]

def update_user_state(phone_number: str, new_state: str, level: int = None, points_to_add: int = 0, last_lesson: str = None):
    update_data = {"current_state": new_state}
    if level is not None:
        update_data["level"] = level
    if last_lesson is not None:
        update_data["last_lesson"] = last_lesson

    if points_to_add > 0:
        current_points = supabase.table("students").select("points").eq("phone_number", phone_number).execute().data[0]['points']
        update_data["points"] = current_points + points_to_add

    res = supabase.table("students").update(update_data).eq("phone_number", phone_number).execute()
    return res.data[0] if res.data else None

def save_last_lesson(phone_number: str, lesson_text: str):
    """
    حفظ آخر درس تعلمه الطالب في قاعدة البيانات.
    """
    supabase.table("students").update({"last_lesson": lesson_text[:500]}).eq("phone_number", phone_number).execute()
