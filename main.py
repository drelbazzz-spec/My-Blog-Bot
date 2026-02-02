import os
import smtplib
import time
import random
import google.generativeai as genai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- كود التشخيص (Debugging) ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ مصيبة! المفتاح مش موجود أصلاً في GitHub Secrets.")
    exit(1)
else:
    # طباعة جزء صغير من المفتاح للتأكد أنه الجديد
    print(f"🔑 المفتاح المستخدم يبدأ بـ: {api_key[:5]}... وينتهي بـ: ...{api_key[-3:]}")

genai.configure(api_key=api_key)

def get_working_model():
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for m in models:
        try:
            print(f"🔄 جاري تجربة الموديل: {m}...")
            model = genai.GenerativeModel(m)
            model.generate_content("test")
            print(f"✅ نجح الاتصال مع: {m}")
            return model
        except Exception as e:
            # هنا التعديل: إظهار سبب الخطأ الحقيقي
            print(f"⚠️ فشل {m} والسبب: {str(e)}") 
            continue
            
    print("❌ كل المحاولات فشلت. راجع سبب الخطأ المكتوب فوق.")
    raise Exception("Critical Failure")

# تشغيل الموديل
try:
    model = get_working_model()
except:
    exit(1)

def get_topic():
    prompts = [
        "شرح تقنيات الذكاء الاصطناعي 2026",
        "الاستثمار في الذهب للمبتدئين",
        "تطبيقات تزيد الإنتاجية",
        "نصائح لتعلم البرمجة من الصفر"
    ]
    t = random.choice(prompts)
    return model.generate_content(f"اكتب عنوان مقال جذاب جداً عن: {t} (العنوان فقط)").text.strip().replace('"','')

def write_article(topic):
    prompt = f"""
    اكتب مقالاً طويلاً (1000 كلمة) عن: "{topic}".
    التنسيق HTML:
    - <h2>مقدمة</h2>
    - <h2>خطوات عملية</h2>
    - <h2>نصائح</h2>
    - <h2>خاتمة</h2>
    """
    return model.generate_content(prompt).text.replace("```html","").replace("```","")

def send_email(subject, body):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    img_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800"
    
    html = f"""
    <div dir="rtl">
        <img src="{img_url}" style="width:100%; border-radius:10px;">
        {body}
    </div>
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    print("🚀 بدء التشخيص والعمل...")
    for i in range(5):
        try:
            t = get_topic()
            print(f"📝 جاري كتابة: {t}")
            c = write_article(t)
            send_email(t, c)
            print("✅ تم النشر!")
            time.sleep(60)
        except Exception as e:
            print(f"❌ خطأ أثناء العمل: {e}")
            time.sleep(10)
