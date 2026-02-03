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

# إعداد العميل
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- دوال المساعدة ---
def clean_format(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'##\s*(.*?)\n', r'<h2>\1</h2>\n', text)
    text = re.sub(r'###\s*(.*?)\n', r'<h3>\1</h3>\n', text)
    text = text.replace("```html", "").replace("```", "")
    return text

def llm_call(prompt, system_role="Assistant", temp=0.7):
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

# --- الخوارزمية الذكية (The Agents) ---

def step1_planner(topic):
    print("1️⃣ جاري التخطيط للمقال...")
    prompt = f"""
    أنت رئيس تحرير. ضع خطة تفصيلية (Outline) لمقال عن: "{topic}".
    اريد 4 عناوين رئيسية قوية تغطي الموضوع من زاوية عملية ونادرة.
    لا تكتب مقدمة ولا خاتمة، فقط العناوين والنقاط تحتها.
    """
    return llm_call(prompt, system_role="Expert Planner")

def step2_writer(topic, outline):
    print("2️⃣ جاري كتابة المسودة الأولى...")
    prompt = f"""
    اكتب مسودة أولية لمقال عن "{topic}" بناءً على هذه الخطة:
    {outline}
    
    اكتب بلهجة مصرية بيضاء (فصحى بسيطة قريبة للعامية الراقية).
    ركز على المعلومات فقط. لا يهم التنسيق الآن.
    """
    return llm_call(prompt, system_role="Writer", temp=0.8)

def step3_critic(draft):
    print("3️⃣ جاري نقد ومراجعة المحتوى (Feedback Loop)...")
    prompt = f"""
    اقرأ هذه المسودة وانقدها بشدة:
    {draft}
    
    حدد 3 مشاكل فيها (مثلاً: حشو، تكرار، كلمات روبوتية مثل "في خضم"، ملل).
    اكتب ملاحظاتك للمحرر ليقوم بتحسينها.
    """
    return llm_call(prompt, system_role="Harsh Critic")

def step4_editor(topic, draft, critique):
    print("4️⃣ جاري إعادة الصياغة والتحسين النهائي (Final Polish)...")
    prompt = f"""
    أنت محرر محترف (Copywriter). 
    لديك مسودة لمقال عن "{topic}"، وتقرير نقد عليها.
    
    النقد: {critique}
    المسودة: {draft}
    
    المطلوب: أعد كتابة المقال بالكامل ليصبح "تحفة فنية".
    - تخلص من أي كلمات روبوتية.
    - استخدم تنسيق HTML (h2, b, ul).
    - اجعل الأسلوب بشرياً 100%، شيقاً، ومفيداً.
    - لا تضع توقيعاً في النهاية.
    """
    final_content = llm_call(prompt, system_role="Senior Editor", temp=0.7)
    return clean_format(final_content)

def get_topic():
    seeds = ["الذكاء الاصطناعي", "العمل الحر", "التجارة الالكترونية", "الصحة النفسية", "تطوير الذات"]
    seed = random.choice(seeds)
    return llm_call(f"اقترح عنوان مقال فيرال (Viral) وجذاب جداً عن {seed}. العنوان فقط بدون علامات.", temp=0.9).strip().replace('"','')

# --- الإرسال (مع إصلاح الصور) ---
def send_email(subject, body):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    msg = MIMEMultipart('related')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    
    html_template = f"""
    <div dir="rtl" style="font-family: 'Segoe UI', sans-serif; font-size: 18px; line-height: 1.8; color: #333;">
        <img src="cid:topimage" style="width:100%; border-radius:12px; margin-bottom:20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        {body}
    </div>
    """
    msg.attach(MIMEText(html_template, 'html'))
    
    # محاولة تحميل الصورة (التعديل الجديد)
    img_data = None
    try:
        # المحاولة الأولى: صور الذكاء الاصطناعي
        encoded_query = urllib.parse.quote(f"cinematic shot of {subject}, 4k, realistic")
        img_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1280&height=720&model=flux&seed={random.randint(1,999)}"
        print("📸 جاري تحميل صورة AI...")
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            img_data = response.content
        else:
            raise Exception("AI Image failed")
            
    except Exception as e:
        print(f"⚠️ فشل AI، جاري استخدام البديل: {e}")
        try:
            # المحاولة الثانية: صور طبيعية عشوائية (Backup)
            img_url = "https://picsum.photos/800/600"
            img_data = requests.get(img_url, timeout=10).content
        except:
            print("❌ فشل تحميل جميع الصور")

    # إرفاق الصورة (لو نجح التحميل)
    if img_data:
        try:
            # التعديل الهام هنا: _subtype='jpeg'
            # ده بيجبر البوت يقبل الصورة حتى لو مش عارف نوعها
            image = MIMEImage(img_data, _subtype='jpeg') 
            image.add_header('Content-ID', '<topimage>')
            msg.attach(image)
            print("✅ تم إرفاق الصورة بنجاح!")
        except Exception as e:
            print(f"❌ خطأ تقني في إرفاق الصورة: {e}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    print("🚀 بدء نظام الوكلاء الأذكياء (مع إصلاح الصور)...")
    
    for i in range(5): 
        try:
            topic = get_topic()
            print(f"\n🌟 الموضوع: {topic}")
            
            # تشغيل المصنع (Planner -> Writer -> Critic -> Editor)
            outline = step1_planner(topic)
            draft = step2_writer(topic, outline)
            critique = step3_critic(draft)
            final_article = step4_editor(topic, draft, critique)
            
            if len(final_article) > 500:
                send_email(topic, final_article)
                print("✅ تم النشر!")
            
            time.sleep(10)
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(5)
