import os
import smtplib
import time
import random
import requests
import re  # مكتبة معالجة النصوص
import urllib.parse
from groq import Groq
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# الاتصال بـ Groq
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
            model="llama-3.3-70b-versatile", 
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"⚠️ خطأ في Groq: {e}")
        return ""

def clean_format(text):
    """دالة لتنظيف النص وتحويل الرموز إلى HTML صحيح لبلوجر"""
    # تحويل **نص** إلى <b>نص</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # تحويل ## عنوان إلى <h2>عنوان</h2>
    text = re.sub(r'##\s*(.*?)\n', r'<h2>\1</h2>\n', text)
    # تنظيف كود الـ Markdown
    text = text.replace("```html", "").replace("```", "").replace("* ", "• ")
    return text

def get_topic():
    prompts = [
        "أسرار الذكاء الاصطناعي 2026",
        "طرق الربح من الانترنت للمبتدئين",
        "مقارنة هواتف الفئة المتوسطة",
        "نصائح لتعلم اللغات بسرعة",
        "كيفية البدء في التجارة الإلكترونية"
    ]
    t = random.choice(prompts)
    return generate_text(f"اقترح عنوان مقال جذاب جداً عن: {t}. (اكتب العنوان فقط بدون أي مقدمات)").strip().replace('"','')

def write_article(topic):
    prompt = f"""
    اكتب مقالاً طويلاً وتفصيلياً (لا يقل عن 1200 كلمة) عن: "{topic}".
    
    تعليمات صارمة للتنسيق (HTML Only):
    1. لا تستخدم علامات Markdown أبداً (مثل ** أو ##).
    2. استخدم <b> للكلمات العريضة والمهمة.
    3. استخدم <h2> للعناوين الرئيسية والفرعية.
    4. استخدم <br> للفصل بين الفقرات.
    5. استخدم <ul> و <li> للقوائم والنقاط.
    
    الهيكل:
    1. مقدمة قوية.
    2. التفاصيل (استخدم قوائم ونقاط).
    3. الخاتمة.
    
    الأسلوب: عربي فصحى سلس، منسق، وجاهز للنشر فوراً.
    """
    raw_text = generate_text(prompt)
    return clean_format(raw_text) # تنظيف النص قبل الإرسال

def send_email(subject, body):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    msg = MIMEMultipart('related')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    
    # تنسيق الرسالة النهائي (CSS لبلوجر)
    html_template = f"""
    <div dir="rtl" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 18px; line-height: 1.8; color: #333;">
        <img src="cid:topimage" style="width:100%; max-width: 800px; height: auto; border-radius:15px; margin-bottom:25px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        
        {body}
        
        <br><hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="text-align:center; color:#888; font-size: 14px;">
            تم إعداد هذا المقال بواسطة المساعد الذكي (AI Writer) 🤖
        </p>
    </div>
    """
    
    msg.attach(MIMEText(html_template, 'html'))
    
    # تحميل الصورة
    try:
        encoded_query = urllib.parse.quote(subject)
        img_url = f"https://image.pollinations.ai/prompt/hyper-realistic photo of {encoded_query}?width=1280&height=720&model=flux&seed={random.randint(1,9999)}"
        print("📸 جاري تحميل الصورة...")
        img_data = requests.get(img_url).content
        image = MIMEImage(img_data)
        image.add_header('Content-ID', '<topimage>')
        msg.attach(image)
    except Exception as e:
        print(f"⚠️ فشل تحميل الصورة: {e}")

    # الإرسال
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    print("🚀 بدء تشغيل البوت (إصدار بلوجر المحسن)...")
    
    for i in range(5):
        print(f"\n--- 📝 جاري العمل على المقال {i+1} ---")
        try:
            topic = get_topic()
            if not topic: continue
                
            print(f"العنوان: {topic}")
            content = write_article(topic)
            
            if len(content) > 500:
                send_email(topic, content)
                print("✅ تم النشر بتنسيق HTML سليم!")
            else:
                print("⚠️ المحتوى فارغ!")
            
            time.sleep(10) 
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(5)
