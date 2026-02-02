import os
import smtplib
import time
import random
from groq import Groq
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# الاتصال بـ Groq
# تأكد إن السر في جيت هب اسمه: GROQ_API_KEY
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def generate_text(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "أنت كاتب محتوى محترف وتكتب بالعربية بطلاقة."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192", # موديل فيسبوك القوي جداً
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"⚠️ خطأ في Groq: {e}")
        return ""

def get_topic():
    prompts = [
        "أسرار الذكاء الاصطناعي 2026",
        "طرق الربح من الانترنت للمبتدئين",
        "مقارنة هواتف الفئة المتوسطة",
        "نصائح لتعلم اللغات بسرعة"
    ]
    t = random.choice(prompts)
    return generate_text(f"اقترح عنوان مقال جذاب جداً عن: {t}. (اكتب العنوان فقط بدون أي مقدمات)").strip().replace('"','')

def write_article(topic):
    prompt = f"""
    اكتب مقالاً طويلاً وتفصيلياً (لا يقل عن 1200 كلمة) عن: "{topic}".
    
    التنسيق المطلوب (HTML):
    - <h2> للمقدمة والعناوين.
    - <ul> للنقاط.
    - <b> للكلمات المهمة.
    
    الهيكل:
    1. مقدمة تجذب الانتباه.
    2. شرح المشكلة والحل.
    3. خطوات عملية بالتفصيل.
    4. نصيحة ختامية.
    
    الأسلوب: شيق، عربي فصحى بسيط، ومفيد.
    """
    return generate_text(prompt).replace("```html", "").replace("```", "")

def send_email(subject, body):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    # صورة عشوائية
    img_url = f"https://image.pollinations.ai/prompt/{subject.replace(' ','%20')}?width=1280&height=720&model=flux&seed={random.randint(1,999)}"
    
    html = f"""
    <div dir="rtl" style="font-family: Tahoma, sans-serif; font-size: 18px; line-height: 1.6; color: #222;">
        <img src="{img_url}" style="width:100%; border-radius:10px; margin-bottom:20px;">
        {body}
        <hr>
        <p style="text-align:center; color:gray; font-size: small;">تم النشر بواسطة: Llama 3 (Groq AI)</p>
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
    print("🚀 بدء تشغيل Groq Bot (المجاني والسريع)...")
    
    for i in range(5):
        print(f"\n--- ⚡ جاري كتابة المقال {i+1} ---")
        try:
            topic = get_topic()
            print(f"العنوان: {topic}")
            
            content = write_article(topic)
            if len(content) > 500:
                send_email(topic, content)
                print("✅ تم الإرسال!")
            
            time.sleep(10) # Groq سريع جداً مش محتاج راحة طويلة
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(5)
