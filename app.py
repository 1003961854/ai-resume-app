import streamlit as st
import openai
import pdfkit
import supabase
from datetime import datetime
from supabase import create_client, Client

# === 配置 Supabase ===
SUPABASE_URL = "https://svohknkyfpqahexvmsfs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2b2hrbmt5ZnBxYWhleHZtc2ZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcwMTk3MTMsImV4cCI6MjA2MjU5NTcxM30.h9Sry2rhCGTvwG5z3DRvhiCTKB6ZkkV6WxCl_-eXPiY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === 配置 GPT API ===
openai.api_key = "your_openai_api_key_here"

st.set_page_config(page_title="AI Resume & Interview Assistant", layout="centered")
st.title("🧠 AI Resume & Interview Assistant / AI 简历与面试助手")

# === 登录模块 ===
st.sidebar.header("🔐 Login / 登录")
email = st.sidebar.text_input("📧 Email 邮箱", key="email")

if st.sidebar.button("Send Login Code / 发送验证码"):
    try:
        response = supabase.auth.sign_in_with_otp({"email": email})
        st.sidebar.success("✅ Verification code sent! / 验证码已发送，请检查邮箱")
    except Exception as e:
        st.sidebar.error(f"❌ Error sending code: {e}")

code = st.sidebar.text_input("🔢 Enter Code / 输入验证码", key="otp")
if st.sidebar.button("Verify Code / 验证登录"):
    try:
        session = supabase.auth.verify_otp({"email": email, "token": code, "type": "email"})
        st.session_state["user"] = session.user.email
        st.sidebar.success(f"🎉 Welcome, {session.user.email}!")
    except Exception as e:
        st.sidebar.error(f"❌ Login failed: {e}")

# === 登录后显示内容 ===
if "user" in st.session_state:
    st.success(f"👋 Logged in as: {st.session_state['user']}")

    # Language toggle
    lang = st.radio("Language / 语言", ["English", "中文"])

    # Resume Generator
    st.header("📄 Resume Generator / 简历生成器")

    name = st.text_input("Name / 姓名")
    position = st.text_input("Target Position / 目标岗位")
    experience = st.text_area("Work or Project Experience / 工作或项目经历")
    skills = st.text_area("Skills / 技能")

    if st.button("Generate Resume / 生成简历"):
        prompt = f"""
        Create a professional resume in {lang}.
        Name: {name}
        Position: {position}
        Experience: {experience}
        Skills: {skills}
        Format it clearly with bullet points and sections.
        """

        with st.spinner("Generating resume..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional resume writing assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            resume_text = response.choices[0].message.content
            st.markdown("### ✨ Generated Resume / 生成的简历")
            st.markdown(resume_text)

            # Save to HTML and convert to PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = f"resume_{timestamp}.html"
            pdf_file = f"resume_{timestamp}.pdf"

            with open(html_file, "w", encoding="utf-8") as f:
                f.write(f"<html><body>{resume_text}</body></html>")

            try:
                pdfkit.from_file(html_file, pdf_file)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF 简历", f, file_name=pdf_file)
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
else:
    st.warning("🔑 Please login to use the AI resume generator. / 请先登录后再使用简历生成功能。")
