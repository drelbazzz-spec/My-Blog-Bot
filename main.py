import os
import smtplib
import time
import random
import google.generativeai as genai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# تهيئة المفتاح
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_working_model():
    """هذه الدالة هي 'الجوكر'.. تجرب الموديلات لحد ما تلاقي واحد شغال"""
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for m in models:
        try:
            print(f"🔄 جاري تجربة الموديل: {m}...")
            model = genai.GenerativeModel(m)
            model.generate_content("test") # اختبار سريع
            print(f"✅ تم الاتصال بنجاح مع: {m}")
            return model
        except:
            print(f"⚠️ الموديل {m} مش شغال، نجرب اللي بعده...")
            continue
    raise Exception("❌ كل الموديلات مشغولة حالياً.")

# تشغيل الموديل المختار
model = get_working_model()

def get_topic():
    prompts = [
        "أدوات الذكاء الاصطناعي المجانية 2026",
        "طرق الاستثمار في الذهب والبورصة بمبالغ صغيرة",
        "مواقع توفر عليك ساعات عمل يومياً",
        "أفضل تطبيقات الموبايل لزيادة الإنتاجية"
    ]
    topic = random.choice(prompts)
    try:
        return model.generate_content(f"هات عنوان مقال 'فيروس' جذاب جداً عن: {topic}. العنوان فقط.").text.strip().replace('"','')
    except:
        return f"دليل شامل عن {topic}"

def write_article(topic):
    prompt = f"""
    اكتب مقالاً طويلاً وتفصيلياً (أكثر من 1000 كلمة) عن: "{topic}".
    
    الهيكل المطلوب (HTML Only):
    1. <h2>مقدمة قوية</h2> (ابدأ بقصة).
    2. <h2>التفاصيل والخطوات</h2> (شرح 5 نقاط عملية).
    3. <h2>المميزات والعيوب</h2>.
    4. <h2>أسئلة شائعة</h2> (3 أسئلة).
    5. <h2>الخاتمة</h2>.
    
    الأسلوب: ممتع، بسيط، وموجه للقارئ.
    """
    return model.generate_content(prompt).text.replace("```html","").replace("```","")

def send_email(subject, body):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    # صورة عشوائية لضمان عدم التكرار
    try:
        desc = model.generate_content(f"3 words description for image about: {subject}").text.strip()
        img_url = f"https://image.pollinations.ai/prompt/{desc.replace(' ','%20')}?width=1280&height=720&model=flux&seed={random.randint(1,9999)}"
    except:
        img_url = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800"

    html = f"""
    <div dir="rtl" style="font-family: Arial, sans-serif; font-size: 18px;">
        <img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">
        {body}
        <p style="text-align:center; color:gray;">تم النشر بواسطة المستثمر الذكي AI</p>
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
    print("🚀 بدء تشغيل المصنع الجديد (5 مقالات)...")
    for i in range(5):
        print(f"\n--- 📝 المقال رقم {i+1} ---")
        try:
            t = get_topic()
            print(f"العنوان: {t}")
            c = write_article(t)
            if len(c) > 100:
                send_email(t, c)
                print("✅ تم النشر!")
            time.sleep(60) # استراحة دقيقة
        except Exception as e:
            print(f"❌ خطأ بسيط: {e}")
            time.sleep(30)
            continue
