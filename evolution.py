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
