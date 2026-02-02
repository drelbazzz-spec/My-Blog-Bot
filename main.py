import os
import smtplib
import time
import random
import google.generativeai as genai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# --- إعدادات الذكاء الاصطناعي (تم التحديث لتفادي الأخطاء) ---
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# نستخدم موديل Pro لأنه أذكى في المقالات الطويلة
# إذا واجهت خطأ، يمكن تغييره إلى "gemini-pro" فقط
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", 
    generation_config={
        "temperature": 0.9,  # إبداع عالي
        "top_p": 0.95,
        "max_output_tokens": 8192, # يسمح بكتابة مقال طويل جداً
    }
)

def get_tech_topic():
    """اختيار موضوع تريند"""
    prompts = [
        "شرح أدوات الذكاء الاصطناعي الجديدة 2026",
        "طرق الربح من الانترنت للمبتدئين بدون رأس مال",
        "أفضل تطبيقات تنظيم الوقت والإنتاجية",
        "مقارنة بين أحدث الهواتف الذكية في الفئة المتوسطة"
    ]
    selected = random.choice(prompts)
    prompt = f"اقترح عنوان مقال 'فيروس' (Viral) وجذاب جداً في مجال: {selected}. الرد بالعنوان فقط."
    return model.generate_content(prompt).text.strip().replace('"','').replace('*', '')

def write_massive_article(topic):
    """كتابة مقال عملاق (+1500 كلمة)"""
    prompt = f"""
    تصرف ككاتب تقني محترف وخبير SEO. اكتب "دليلاً شاملاً" عن: "{topic}".
    
    المطلوب: مقال ضخم، دسم، ومليء بالتفاصيل (لا يقل عن 1500 كلمة).
    
    الهيكل الإجباري للمقال (استخدم وسوم HTML للتنسيق):
    1. <h2>مقدمة تخطف الأنفاس</h2>: ابدأ بقصة قصيرة أو إحصائية صادمة تجذب القارئ.
    2. <h2>ما هو هذا الشيء؟</h2>: شرح بسيط ومفصل للمفهوم.
    3. <h2>5 خطوات عملية للتطبيق</h2>: (هنا قلب المقال) اشرح 5 نقاط أو أدوات بالتفصيل الممل.
    4. <h2>المميزات والعيوب (بكل صراحة)</h2>: اذكر الإيجابيات والسلبيات.
    5. <h2>أسئلة شائعة (FAQ)</h2>: اكتب 3 أسئلة يسألها الناس عادةً مع إجاباتها.
    6. <h2>الخاتمة والنصيحة الذهبية</h2>: لخص الموضوع وحفز القارئ.

    التنسيق:
    - استخدم <b>للكلمات المهمة</b>.
    - استخدم <ul> و <li> للقوائم لسهولة القراءة.
    - الأسلوب: ممتع، قصصي، وموجه للقارئ (استخدم كلمة "أنت").
    """
    try:
        response = model.generate_content(prompt)
        return response.text.replace("```html", "").replace("```", "")
    except Exception as e:
        return f"<p>عذراً، حدث خطأ أثناء الكتابة: {str(e)}</p>"

def send_email(subject, body):
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    # تصميم صورة حصرية للمقال
    try:
        img_prompt = model.generate_content(f"Describe a futuristic, cyberpunk tech illustration for a blog post about: {subject}. Reply with 3 english words only.").text
        safe_prompt = img_prompt.strip().replace(" ", "%20")
        img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&model=flux&seed={random.randint(1,9999)}"
    except:
        img_url = "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800" # صورة احتياطية

    html_content = f"""
    <div dir="rtl" style="font-family: sans-serif; font-size: 18px; line-height: 1.8; color: #222;">
        <div style="text-align: center; margin-bottom: 30px;">
            <img src="{img_url}" alt="{subject}" style="width: 100%; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        </div>
        {body}
        <hr style="margin: 40px 0; border-top: 1px solid #ddd;">
        <p style="text-align: center; font-size: 0.9em; color: #666;">
            <em>تم إعداد هذا الدليل الشامل بواسطة فريق التحرير الذكي.</em>
        </p>
    </div>
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    print("🚀 بدء المولد العملاق...")
    
    # حلقة تكرار لكتابة 5 مقالات (كما طلبت)
    for i in range(5):
        print(f"--- جاري العمل على المقال رقم {i+1} ---")
        try:
            topic = get_tech_topic()
            print(f"📌 العنوان: {topic}")
            
            content = write_massive_article(topic)
            if len(content) > 500: # تأكد أن المقال كتب فعلاً
                send_email(topic, content)
                print("✅ تم النشر!")
            else:
                print("⚠️ المقال قصير جداً أو فارغ، تخطي...")
            
            # استراحة 2 دقيقة لمنع الحظر
            print("☕ استراحة قصيرة...")
            time.sleep(120) 
            
        except Exception as e:
            print(f"❌ خطأ في المقال {i+1}: {e}")
            time.sleep(60)
            continue
            
    print("🎉 انتهت المهمة: 5 مقالات دسمة جاهزة!")
