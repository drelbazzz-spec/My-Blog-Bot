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
# 1. إعداد المحرك (Engine Setup)
# -------------------------------------------------------------------
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# -------------------------------------------------------------------
# 2. أدوات المساعدة (Helper Functions)
# -------------------------------------------------------------------
def clean_html(text):
    """تنظيف وتنسيق HTML النهائي"""
    # تحويل الماركداون
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'##\s*(.*?)\n', r'<h2>\1</h2>\n', text)
    text = re.sub(r'###\s*(.*?)\n', r'<h3>\1</h3>\n', text)
    # تنظيف الشوائب
    text = text.replace("```html", "").replace("```", "")
    text = text.replace("html", "").replace("body", "")
    return text

def smart_llm(prompt, role="Assistant", temp=0.7):
    """دالة الاتصال الذكي بـ Groq"""
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=temp,
            max_tokens=6000 # السماح بإجابات طويلة جداً
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"⚠️ خطأ LLM: {e}")
        return ""

# -------------------------------------------------------------------
# 3. الوكلاء الأذكياء (The Super Agents)
# -------------------------------------------------------------------

def agent_seo_strategist():
    """العميل 1: خبير السيو واختيار النيش"""
    print("1️⃣ (SEO Agent): تحليل التريند والكلمات المفتاحية...")
    
    # نيشات دقيقة جداً لعام 2026 (High CPM)
    niches = [
        "تطبيقات التمويل اللامركزي (DeFi) للمبتدئين 2026",
        "علاج الشيخوخة بتقنيات الذكاء الاصطناعي",
        "الاستثمار في العقارات الافتراضية (Metaverse Real Estate)",
        "وظائف لا يمكن للذكاء الاصطناعي استبدالها في 2026",
        "دليل الهجرة الرقمية (Digital Nomad) لجنوب شرق آسيا",
        "أفضل السيارات الكهربائية الاقتصادية في السوق المصري 2026"
    ]
    topic_seed = random.choice(niches)
    
    prompt = f"""
    أنت خبير SEO عالمي. نحن في عام 2026.
    الموضوع المقترح: {topic_seed}
    
    المطلوب:
    1. صغ عنواناً "فيروسياً" (Clickbait محترم) يجذب النقرة.
    2. حدد الكلمة المفتاحية الأساسية (Focus Keyword).
    3. حدد 3 كلمات دلالية ثانوية (LSI Keywords).
    
    الرد بصيغة: العنوان | الكلمة المفتاحية | الكلمات الثانوية
    بدون أي مقدمات.
    """
    response = smart_llm(prompt, role="SEO Expert", temp=0.8)
    return response.split('|')

def agent_architect(title, keywords):
    """العميل 2: مهندس الهيكل"""
    print("2️⃣ (Architect): بناء الهيكل العظمي للمقال...")
    prompt = f"""
    الموضوع: {title}
    الكلمات المستهدفة: {keywords}
    
    ضع هيكلاً تفصيلياً لمقال طويل (Long-Form) يتكون من:
    1. مقدمة بخطاف (Hook) قوي.
    2. 4 أقسام رئيسية دسمة.
    3. قسم "مقارنة" أو "جدول".
    4. قسم الأسئلة الشائعة (FAQ) لتقوية السيو.
    5. خاتمة ودعوة لاتخاذ إجراء (CTA).
    فقط العناوين والنقاط.
    """
    return smart_llm(prompt, role="Content Architect")

def agent_writer(title, structure):
    """العميل 3: الكاتب المحترف"""
    print("3️⃣ (Writer): كتابة المحتوى الدسم...")
    prompt = f"""
    أنت كاتب محتوى تقني/مالي مخضرم. نحن في عام 2026.
    اكتب مقالاً طويلاً جداً (لا يقل عن 1500 كلمة) بناءً على هذا الهيكل:
    {structure}
    عن العنوان: {title}
    
    الشروط الصارمة:
    - استخدم لغة عربية قوية وسلسة (السهل الممتنع).
    - وزع الكلمات المفتاحية بذكاء.
    - اذكر أرقاماً، إحصائيات (تخيلية لعام 2026)، وأسماء أدوات.
    - ضع علامة [IMG_MID] في منتصف المقال وعلامة [IMG_END] قبل الخاتمة.
    - لا تستخدم مقدمات مملة مثل "مما لا شك فيه".
    """
    return smart_llm(prompt, role="Senior Writer", temp=0.8)

def agent_critic_and_fix(draft):
    """العميل 4: الناقد والمحرر (Feedback Loop)"""
    print("4️⃣ (Critic & Editor): النقد والمراجعة...")
    
    # خطوة النقد
    critique = smart_llm(f"انقد هذا المقال بقسوة: {draft[:2000]}... (استخرج نقاط الضعف والروبوتية)", role="Harsh Critic")
    
    # خطوة الإصلاح
    prompt = f"""
    أنت "د. محمد الباز"، رئيس التحرير.
    بناءً على هذا النقد: ({critique})
    
    أعد صياغة المقال ليصبح مثالياً:
    1. اجعل الفقرات قصيرة (3 أسطر بحد أقصى).
    2. استخدم <b> للكلمات الهامة.
    3. استخدم <h2> للعناوين.
    4. تأكد من وجود العلامات [IMG_MID] و [IMG_END].
    5. احذف أي جملة تشير للذكاء الاصطناعي.
    """
    return clean_html(smart_llm(prompt, role="Editor in Chief", temp=0.7))

# -------------------------------------------------------------------
# 4. نظام الصور المتعددة (Multi-Image System)
# -------------------------------------------------------------------
def fetch_image(prompt_desc):
    """جلب صورة مع معالجة الأخطاء"""
    try:
        # تحسين الوصف ليكون سينمائياً
        enhanced_prompt = f"editorial photography of {prompt_desc}, 2026 futuristic style, 8k resolution, cinematic lighting, photorealistic"
        encoded = urllib.parse.quote(enhanced_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&model=flux&seed={random.randint(1,9999)}"
        
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            return resp.content
    except:
        return None
    return None

def send_blog_email(title, content, keywords):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    msg = MIMEMultipart('related')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = title
    
    # --- توليد 3 صور ---
    print("📸 جاري توليد 3 صور حصرية...")
    # صورة 1: تعبر عن العنوان
    img1 = fetch_image(f"{title} concept art")
    # صورة 2: تعبر عن التكنولوجيا/التفاصيل
    img2 = fetch_image(f"detailed visualization of {keywords} technology")
    # صورة 3: تعبر عن النجاح/المستقبل
    img3 = fetch_image(f"happy person using {keywords} in 2026")

    # --- معالجة المحتوى لزرع الصور ---
    # نستبدل العلامات بكود الصورة الداخلي (CID)
    content = content.replace("[IMG_MID]", '<br><div style="text-align:center"><img src="cid:img2" style="width:100%; border-radius:10px; margin:20px 0;"></div><br>')
    content = content.replace("[IMG_END]", '<br><div style="text-align:center"><img src="cid:img3" style="width:100%; border-radius:10px; margin:20px 0;"></div><br>')

    # --- تصميم القالب (Premium Template) ---
    html_body = f"""
    <div dir="rtl" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 18px; line-height: 1.9; color: #1a1a1a; background-color: #ffffff; padding: 20px;">
        
        <!-- الهيدر والصورة الأولى -->
        <div style="margin-bottom: 40px; text-align: center;">
            <img src="cid:img1" style="width:100%; max-width: 800px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
        </div>

        <!-- المحتوى -->
        <div style="max-width: 800px; margin: auto;">
            {content}
        </div>

        <!-- بطاقة المؤلف (Author Box) -->
        <div style="margin-top: 60px; padding: 25px; background: linear-gradient(45deg, #f1f2f6, #ffffff); border-right: 6px solid #2980b9; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 22px;">✍️ بقلم: د. محمد الباز</h3>
            <p style="margin: 0; color: #576574; font-size: 16px;">
                خبير التقنيات الحديثة والاستثمار | طبيب ورائد أعمال.
                <br><em>جميع الحقوق محفوظة © 2026</em>
            </p>
        </div>
    </div>
    """
    
    msg.attach(MIMEText(html_body, 'html'))

    # --- إرفاق الصور (The Attachment Logic) ---
    images_map = {
        'img1': img1,
        'img2': img2,
        'img3': img3
    }
    
    for cid, img_bytes in images_map.items():
        if img_bytes:
            try:
                # الحيلة السحرية لإجبار البوت على قبول الصورة
                image_part = MIMEImage(img_bytes, _subtype='jpeg') 
                image_part.add_header('Content-ID', f'<{cid}>')
                msg.attach(image_part)
            except Exception as e:
                print(f"⚠️ فشل إرفاق {cid}: {e}")

    # الإرسال النهائي
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

# -------------------------------------------------------------------
# 5. التشغيل الرئيسي
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 بدء نظام الوكالة الإعلامية (Super Agent V2)...")
    
    # سننشر مقالين فقط بجودة فائقة بدلاً من 5 مقالات ضعيفة
    for i in range(2): 
        try:
            print(f"\n--- ⏳ بدء العمل على المشروع رقم {i+1} ---")
            
            # الخطوة 1: استراتيجية السيو
            seo_data = agent_seo_strategist()
            title = seo_data[0].strip()
            keywords = seo_data[1].strip() if len(seo_data) > 1 else "Tech 2026"
            print(f"📌 العنوان المعتمد: {title}")
            
            # الخطوة 2: الهندسة
            structure = agent_architect(title, keywords)
            
            # الخطوة 3: الكتابة
            draft = agent_writer(title, structure)
            
            # الخطوة 4: النقد والتحسين
            final_article = agent_critic_and_fix(draft)
            
            # الخطوة 5: النشر مع الصور
            if len(final_article) > 1000:
                send_blog_email(title, final_article, keywords)
                print(f"✅ تم نشر المقال {i+1} بنجاح باهر!")
            else:
                print("⚠️ المقال لم يجتز معايير الجودة (قصير).")
            
            print("☕ استراحة لتجهيز المقال القادم...")
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
