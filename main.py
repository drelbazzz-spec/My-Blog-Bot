import os
import smtplib
import time
import random
import requests
import re
import urllib.parse
from groq import Groq
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# -------------------------------------------------------------------
# إعداد العميل (تأكد من وجود GROQ_API_KEY في GitHub Secrets)
# -------------------------------------------------------------------
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# -------------------------------------------------------------------
# دوال المساعدة والتنظيف
# -------------------------------------------------------------------
def clean_format(text):
    # تحويل Markdown إلى HTML
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'##\s*(.*?)\n', r'<h2>\1</h2>\n', text)
    text = re.sub(r'###\s*(.*?)\n', r'<h3>\1</h3>\n', text)
    text = text.replace("```html", "").replace("```", "")
    return text

def llm_call(prompt, system_role="Assistant", temp=0.7):
    """دالة الاتصال بـ Groq"""
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=temp,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"⚠️ خطأ في الاتصال: {e}")
        return ""

# -------------------------------------------------------------------
# خوارزمية "مصنع المحتوى" (Agentic Workflow)
# -------------------------------------------------------------------

def step1_planner(topic):
    print("1️⃣ (المخطط): وضع هيكل المقال...")
    prompt = f"""
    أنت مدير تحرير لموقع تقني ومالي كبير. الموضوع هو: "{topic}".
    ضع خطة (Outline) لمقال طويل جداً (Long-form) يغطي:
    1. مشكلة حديثة تواجه الناس في 2026.
    2. حلول عملية وأدوات بالاسم.
    3. دراسة حالة أو مثال واقعي.
    4. الأسئلة الشائعة.
    فقط اكتب العناوين الرئيسية والفرعية.
    """
    return llm_call(prompt, system_role="Expert Planner")

def step2_writer(topic, outline):
    print("2️⃣ (الكاتب): كتابة المسودة الأولى...")
    prompt = f"""
    اكتب مقالاً تفصيلياً (2000 كلمة) عن "{topic}" بناءً على الخطة:
    {outline}
    
    التعليمات:
    - اكتب بلهجة "الخبير الصديق" (Friendly Expert).
    - استخدم مصطلحات 2026 (Web3, AI Agents, DeFi).
    - اذكر أسماء أدوات وبرامج حقيقية.
    - اكتب محتوى دسم وليس حشو.
    """
    return llm_call(prompt, system_role="Senior Writer", temp=0.8)

def step3_critic(draft):
    print("3️⃣ (الناقد): مراجعة الجودة...")
    prompt = f"""
    انقد هذه المسودة بشدة:
    {draft}
    
    ابحث عن:
    1. الجمل المكررة.
    2. لغة الذكاء الاصطناعي (مثل: في خضم، مما لا شك فيه).
    3. المعلومات السطحية.
    أعطني قائمة بالتعديلات المطلوبة فقط.
    """
    return llm_call(prompt, system_role="Harsh Critic")

def step4_editor(topic, draft, critique):
    print("4️⃣ (المحرر): الصياغة النهائية...")
    prompt = f"""
    أنت "د. محمد الباز"، كاتب وخبير.
    أعد صياغة المقال بناءً على النقد: {critique}
    
    شروط التنسيق الصارمة (HTML):
    - استخدم <h2> للعناوين.
    - استخدم <b> للكلمات المهمة.
    - ضع <br> للفصل بين الفقرات.
    - ضع علامة [IMG1] بعد المقدمة.
    - ضع علامة [IMG2] في منتصف المقال.
    
    أسلوب الكتابة:
    - ابدأ بقصة شخصية أو سؤال صادم.
    - اجعل الجمل قصيرة وقوية.
    - لا تذكر أنك ذكاء اصطناعي أبداً.
    """
    content = llm_call(prompt, system_role="Editor-in-Chief", temp=0.7)
    return clean_format(content)

def get_trendy_topic():
    # قائمة نيشات (Niches) مربحة جداً (High CPC)
    niches = [
        "الاستثمار في العملات الرقمية الجديدة 2026",
        "أدوات الذكاء الاصطناعي للأطباء والمهندسين",
        "الربح من محتوى الفيديو القصير (Shorts)",
        "شركات التداول الموثوقة في مصر والخليج",
        "الهجرة والعمل في الخارج للمبرمجين"
    ]
    selected = random.choice(niches)
    return llm_call(f"هات عنوان مقال 'فيروس' (Clickbait بس صادق) عن: {selected}. (العنوان فقط)", temp=0.9).strip().replace('"','')

# -------------------------------------------------------------------
# نظام الصور والبريد (Email & Images System)
# -------------------------------------------------------------------

def get_image_data(prompt_desc):
    """دالة ذكية لجلب صورة ومحاولة إصلاح أخطاء MIME"""
    try:
        # تحسين وصف الصورة ليكون واقعياً
        encoded = urllib.parse.quote(f"high quality photography, {prompt_desc}, 4k, cinematic lighting, photorealistic")
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&model=flux&seed={random.randint(1,9999)}"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            return resp.content
    except:
        return None
    return None

def send_email(subject, body):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    msg = MIMEMultipart('related')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    
    # 1. توليد الصور الثلاثة
    print("📸 جاري توليد الصور الحصرية...")
    img1_data = get_image_data(f"concept art for {subject} header")
    img2_data = get_image_data(f"detailed chart or futuristic office for {subject}")
    img3_data = get_image_data(f"person happy with success {subject}") # صورة للخاتمة إن أردت أو نكتفي باثنين
    
    # 2. استبدال العلامات في النص بالصور (CID placeholders)
    # سنضع الصورة الأولى في الهيدر دائماً
    # ونستبدل [IMG1] و [IMG2] في النص إذا وجدوا
    
    # تنظيف العلامات لو المحرر نسي يحطها أو حطها غلط
    body = body.replace("[IMG1]", '<br><img src="cid:midimage" style="width:100%; border-radius:10px;"><br>')
    body = body.replace("[IMG2]", '<br><img src="cid:footerimage" style="width:100%; border-radius:10px;"><br>')

    # 3. تصميم القالب النهائي (Blogger Template)
    html_template = f"""
    <div dir="rtl" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 18px; line-height: 1.8; color: #222; max-width: 900px; margin: auto;">
        
        <!-- صورة الغلاف الرئيسية -->
        <div style="margin-bottom: 30px;">
            <img src="cid:headerimage" style="width:100%; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.15);">
        </div>

        <!-- جسم المقال -->
        <div style="padding: 10px;">
            {body}
        </div>

        <!-- التوقيع الاحترافي -->
        <div style="margin-top: 50px; padding: 20px; background-color: #f9f9f9; border-right: 5px solid #2ecc71; border-radius: 5px;">
            <h3 style="margin: 0; color: #2c3e50;">بقلم: د. محمد الباز</h3>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #7f8c8d;">خبير التقنية والاستثمار | طبيب ورائد أعمال</p>
        </div>
    </div>
    """
    
    msg.attach(MIMEText(html_template, 'html'))
    
    # 4. إرفاق الصور فعلياً (Attaching Images)
    
    # صورة 1 (Header)
    if img1_data:
        try:
            img = MIMEImage(img1_data, _subtype='jpeg') # إجبار النوع JPEG
            img.add_header('Content-ID', '<headerimage>')
            msg.attach(img)
        except: pass
        
    # صورة 2 (Middle)
    if img2_data:
        try:
            img = MIMEImage(img2_data, _subtype='jpeg')
            img.add_header('Content-ID', '<midimage>')
            msg.attach(img)
        except: pass

    # صورة 3 (Footer/Extra) - لو حبيت تضيفها مستقبلاً
    if img3_data:
        try:
            img = MIMEImage(img3_data, _subtype='jpeg')
            img.add_header('Content-ID', '<footerimage>')
            msg.attach(img)
        except: pass

    # الإرسال
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

# -------------------------------------------------------------------
# التشغيل
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 بدء نظام النشر الاحترافي (Dr. Mohamed El-Baz Edition)...")
    
    for i in range(5):
        try:
            print(f"\n--- ⏳ العمل على المقال رقم {i+1} ---")
            topic = get_trendy_topic()
            print(f"📌 الموضوع: {topic}")
            
            # دورة العمل الكاملة
            outline = step1_planner(topic)
            draft = step2_writer(topic, outline)
            critique = step3_critic(draft)
            final_article = step4_editor(topic, draft, critique)
            
            if len(final_article) > 500:
                send_email(topic, final_article)
                print(f"✅ تم نشر المقال {i+1} بنجاح!")
            else:
                print("⚠️ فشل في توليد محتوى كافٍ.")
            
            # استراحة أطول قليلاً لأن المقال دسم
            time.sleep(20)
            
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
            time.sleep(10)
```

### 💡 مميزات هذا الكود (لماذا هو الأفضل؟):

1.  **3 صور في المقال:** صورة في الأول (Header)، وصورة في النص (Middle)، وصورة إضافية، وكلها تتولد بالذكاء الاصطناعي وتُدمج تلقائياً.
2.  **حل مشكلة `MIME Type`:** استخدمت دالة `MIMEImage(data, _subtype='jpeg')` لإجبار البايثون على قبول الصور حتى لو كانت بدون امتداد واضح.
3.  **التوقيع:** تم تصميم "بطاقة تعريف" في نهاية المقال باسمك وصفاتك (طبيب ورائد أعمال) بشكل أنيق جداً.
4.  **النقد:** البوت ينتقد نفسه ويرفض الجمل الركيكة، مما يرفع مستوى اللغة العربية.

توكل على الله واضغط **Run**.. هذه المرة ستكون النتيجة "مجلة" وليس مجرد مدونة! 🚀👨‍⚕️
