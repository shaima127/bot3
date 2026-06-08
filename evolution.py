import httpx
from config import settings

def send_whatsapp_message(remote_jid: str, text: str):
    """
    إرسال رسالة نصية عبر Evolution API
    """
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
    
    headers = {
        "apikey": settings.EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": remote_jid,
        "text": text,
        "options": {
            "delay": 1200,
            "presence": "composing"
        }
    }
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        return response.json()
    except Exception as e:
        print(f"Error sending message via Evolution API: {e}")
        return None

def get_media_base64(message_data: dict):
    """
    جلب الـ Base64 الخاص بالرسالة الصوتية أو الوسائط من Evolution API
    """
    url = f"{settings.EVOLUTION_API_URL}/chat/getBase64FromMediaMessage/{settings.EVOLUTION_INSTANCE_NAME}"
    headers = {
        "apikey": settings.EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "message": message_data
    }
    
    try:
        # Using a slightly longer timeout since media extraction can take time
        response = httpx.post(url, json=payload, headers=headers, timeout=20.0)
        data = response.json()
        return data.get("base64")
    except Exception as e:
        print(f"Error fetching media base64: {e}")
        return None
