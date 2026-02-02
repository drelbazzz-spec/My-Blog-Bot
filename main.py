import os
import smtplib
import time
import random
import google.generativeai as genai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# إعدادات Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
generation_config = {"temperature": 0.8, "top_p": 0.95, "max_output_tokens": 8192}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

def get_tech_topic():
    # اختيار موضوع مربح
    prompts = ["أدوات ذكاء اصطناعي لزيادة الإنتاجية", "الربح من العمل الحر Freelancing", "شروحات تقنية للمبتدئين"]
    selected = random.choice(prompts)
    prompt = f"اقترح عنوان مقال واحد فقط جذاب جداً (Viral) في مجال: {selected}. الرد بالعنوان فقط."
    return model.generate_content(prompt).text.strip().replace('"','')

def write_article(topic):
    # كتابة المقال
    prompt = f"""
    اكتب مقالاً احترافياً عن: "{topic}".
    الشروط: 
    1. مقسم لعناوين فرعية (H2, H3) وفقرات.
    2. أسلوب خبير تقني يشرح خطوات عملية.
    3. المخرج كود HTML فقط (بدون markdown).
    4. اللغة عربية سهلة ومشوقة.
    """
    return model.generate_content(prompt).text.replace("```html","").replace("```","")

def send_email(subject, body):
    # إرسال لبلوجر
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_PASSWORD"]
    receiver = os.environ["BLOGGER_EMAIL"]
    
    # صورة
    img_prompt = model.generate_content(f"3 words description for tech image about: {subject}").text
    img_url = f"https://image.pollinations.ai/prompt/futuristic%20tech%20{img_prompt.strip()}?width=800&height=450&model=flux&seed={random.randint(1,999)}"
    
    html = f"""<div dir="rtl"><img src="{img_url}" style="width:100%;border-radius:10px;"><br>{body}<br><small>تم النشر بواسطة المساعد الذكي.</small></div>"""
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.send_message(msg)
    server.quit()
    print("Done!")

if __name__ == "__main__":
    t = get_tech_topic()
    c = write_article(t)
    send_email(t, c)
