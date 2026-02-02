import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import pandas as pd
from datetime import datetime

# --- הגדרות API (המפתח שלך) ---
MY_API_KEY = "AIzaSyDJdiYe4VmudGKFQzoCI_MmngD26D4wm1Q" 
genai.configure(api_key=MY_API_KEY)

st.set_page_config(page_title="FitCheck AI 🏋️‍♂️", layout="wide")

# --- עיצוב טכנולוגי צהוב-שחור ---
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .main-header { text-align: center; color: #ccff00; font-family: 'Orbitron', sans-serif; font-size: 3rem; text-shadow: 0px 0px 15px #ccff00; }
    .stButton > button { background: linear-gradient(90deg, #ccff00 0%, #99ff00 100%); color: black; font-weight: bold; border-radius: 12px; border: none; }
    .stats-box { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>FITCHECK AI ⚡</h1>", unsafe_allow_html=True)

# יצירת תיקיות לנתונים
if not os.path.exists("exercises"): os.makedirs("exercises")
if not os.path.exists("history.csv"):
    df = pd.DataFrame(columns=["Date", "Exercise", "Score"])
    df.to_csv("history.csv", index=False)

# --- סרגל צד: ניהול תרגילים והיסטוריה ---
with st.sidebar:
    st.header("⚙️ הגדרות אימון")
    ex_name = st.text_input("שם התרגיל:")
    pro_image = st.file_uploader("העלה תמונה מקצועית (מחוון):", type=['jpg', 'jpeg', 'png'])
    
    if st.button("שמור תרגיל"):
        if ex_name and pro_image:
            Image.open(pro_image).save(f"exercises/{ex_name}.png")
            st.success("התרגיל נשמר!")
            st.rerun()

    st.markdown("---")
    st.subheader("📈 היסטוריית ביצועים")
    history_df = pd.read_csv("history.csv")
    if not history_df.empty:
        st.line_chart(history_df.set_index("Date")["Score"])
    else:
        st.write("עוד לא נרשמו אימונים.")

# --- מסך ראשי ---
exercises = [f.replace(".png", "") for f in os.listdir("exercises")]

if not exercises:
    st.info("העלה תרגיל בסרגל הצד כדי להתחיל לנתח את הביצועים שלך.")
else:
    col1, col2 = st.columns(2)
    with col1:
        target_ex = st.selectbox("בחר תרגיל:", exercises)
        st.image(f"exercises/{target_ex}.png", caption="הביצוע המצופה (Pro)")
    
    with col2:
        user_img = st.camera_input("צלם את עצמך מבצע")

    if st.button("נתח ביצוע 🚀"):
        if user_img:
            with st.spinner("AI מנתח יציבה..."):
                try:
                    pro_img = Image.open(f"exercises/{target_ex}.png")
                    user_img_file = Image.open(user_img)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # פנייה ל-AI לקבלת ציון מספרי והערות
                    prompt = f"Analyze workout form for {target_ex}. Compare user to pro. Return a numeric score (0-100) first, then feedback in Hebrew."
                    response = model.generate_content([prompt, pro_img, user_img_file])
                    
                    # חילוץ ציון (פשוט לוקחים את המספר הראשון שמופיע בטקסט)
                    full_text = response.text
                    score = [int(s) for s in full_text.split() if s.isdigit()][0] if any(s.isdigit() for s in full_text.split()) else 70
                    
                    # שמירה להיסטוריה
                    new_data = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Exercise": target_ex, "Score": score}])
                    new_data.to_csv("history.csv", mode='a', header=False, index=False)
                    
                    st.markdown(f"## ציון ביצוע: {score}/100")
                    st.info(full_text)
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה: {e}")
