import streamlit as st
import openai
import supabase
from datetime import datetime
from supabase import create_client, Client
import PyPDF2
import io
import base64
import os
from docx import Document

# === 配置 Supabase ===
SUPABASE_URL = "https://svohknkyfpqahexvmsfs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2b2hrbmt5ZnBxYWhleHZtc2ZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcwMTk3MTMsImV4cCI6MjA2MjU5NTcxM30.h9Sry2rhCGTvwG5z3DRvhiCTKB6ZkkV6WxCl_-eXPiY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === 配置 GPT API ===
openai.api_key = "your_openai_api_key_here"

st.set_page_config(page_title="AI Resume & Interview Assistant", layout="wide")
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
    lang = st.radio("Language / 语言", ["English", "中文"])

    tab1, tab2, tab3, tab4 = st.tabs(["✍️ Resume Generator", "📊 Resume Analysis", "🎤 Interview", "📁 History"])

    with tab1:
        st.subheader("✍️ Resume Generator / 简历生成器")
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

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"resume_{timestamp}"
                docx_file = f"{base_filename}.docx"

                # Word 导出
                doc = Document()
                for line in resume_text.split("\n"):
                    doc.add_paragraph(line)
                doc.save(docx_file)

                with open(docx_file, "rb") as f:
                    st.download_button("📄 Download Resume as Word", f, file_name=docx_file)

    with tab2:
        st.subheader("📊 Resume Analysis / 简历优化建议")
        uploaded_file = st.file_uploader("Upload Resume (PDF) / 上传简历", type=["pdf"])

        if uploaded_file:
            with st.spinner("Reading your resume..."):
                reader = PyPDF2.PdfReader(uploaded_file)
                resume_content = "\n".join([page.extract_text() for page in reader.pages])
            st.text_area("Your Resume Text / 简历内容预览", resume_content, height=300)

            prompt = f"Please review and optimize the following resume:\n\n{resume_content}"
            with st.spinner("Generating suggestions..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert resume reviewer."},
                        {"role": "user", "content": prompt}
                    ]
                )
                suggestions = response.choices[0].message.content
                st.markdown("### ✅ Optimization Suggestions")
                st.markdown(suggestions)

    with tab3:
        st.subheader("🎤 Interview Simulation / 面试模拟")
        target_role = st.text_input("Target Role / 目标职位")
        if st.button("Generate Interview Questions / 生成面试问题"):
            prompt = f"Generate 5 interview questions for a {target_role} position. Provide ideal answers too."
            with st.spinner("Generating interview questions..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful interview coach."},
                        {"role": "user", "content": prompt}
                    ]
                )
                interview_qas = response.choices[0].message.content
                st.markdown("### 🗣️ Interview Q&A / 面试问答")
                st.markdown(interview_qas)

                st.markdown("---")
                st.subheader("📝 Answer Evaluation / 回答评估")
                user_answer = st.text_area("Your Answer to Q1 / 你对第一个问题的回答")
                if st.button("Evaluate Answer / 评估我的回答"):
                    eval_prompt = f"Here is a model interview question and answer:\n\n{interview_qas}\n\nNow evaluate this user answer to question 1:\n\n{user_answer}\n\nGive feedback and a score out of 10."
                    with st.spinner("Evaluating your answer..."):
                        eval_response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "You are an expert HR interviewer."},
                                {"role": "user", "content": eval_prompt}
                            ]
                        )
                        feedback = eval_response.choices[0].message.content
                        st.markdown("### 🧾 Feedback / 反馈与评分")
                        st.markdown(feedback)

    with tab4:
        st.subheader("📁 History / 使用记录（开发中）")
        st.info("This feature will let you view and restore previous resumes. Coming soon!")

else:
    st.warning("🔑 Please login to use the AI resume generator. / 请先登录后再使用简历生成功能。")
