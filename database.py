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
    model_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    
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

def retrieve_relevant_lesson(level: int, limit: int = 1) -> str:
    """
    تطبيق تقنية RAG الحقيقية للبحث (Vector Semantic Search) داخل قاعدة البيانات.
    """
    query = f"درس برمجة فلاتر Flutter مناسب للطالب في المستوى رقم {level}"
    query_embedding = get_embedding(query)
    
    if not query_embedding:
        print("⚠️ لم نجد نظام Vectors (نقوم بالبحث العادي).")
        response = supabase.table("lessons").select("content").eq("level", level).limit(limit).execute()
        return response.data[0]['content'] if (response.data and len(response.data) > 0) else ""
    
    try:
        # استدعاء معادلة المتجهات RAG من Supabase SQL
        response = supabase.rpc("match_lessons", {
            "query_embedding": query_embedding,
            "match_threshold": 0.1,    # للبحث عن الأقرب دائماً
            "match_count": limit,
            "student_level": level
        }).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['content'] 
    except Exception as e:
        print("Error with Supabase Vectors:", e)
        
    return ""

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
