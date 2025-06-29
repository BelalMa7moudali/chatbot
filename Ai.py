import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime


# --- Gemini API Configuration ---
genai.configure(api_key="AIzaSyB-BWue3gUosUyliLgZt_1KnuiNESvY8aQ")  # Replace with your real Gemini API key
model = genai.GenerativeModel('gemini-2.5-flash')
chat = model.start_chat(history=[])

# --- Streamlit Page Settings ---
st.set_page_config(page_title="Smart LUCAS Simulator", page_icon="💓", layout="centered")
st.title("💓 Smart LUCAS Simulator & First Aid Chatbot")

# --- Current Time ---
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"🕒 **Session Time:** `{now}`")

# --- Description ---
st.markdown("""
This AI-powered tool simulates CPR instructions using a LUCAS device and provides live first aid guidance via chatbot.

Please enter patient data below or ask a question in the chatbot.
""")

# --- Educational Video ---
st.markdown("### 🎥 First Aid Educational Video")
st.video("https://www.youtube.com/watch?v=6yQ5JZEUe3I")

# --- CPR Input Section ---
st.header("🧠 Smart CPR Generator")

age = st.number_input("Patient Age", min_value=0, step=1)
gender = st.selectbox("Patient Gender", ["Male", "Female"])
weight = st.number_input("Weight (kg)", min_value=1)
heart_rate = st.number_input("Heart Rate (bpm)", min_value=0)
condition = st.text_area("Describe the patient's condition")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.button("🧠 Get Smart CPR Instructions"):
    with st.spinner("Generating AI recommendations..."):

        prompt = f"""
        You are a professional assistant in emergency medicine.

        Based on the following patient info:
        - Age: {age}
        - Gender: {gender}
        - Weight: {weight} kg
        - Heart Rate: {heart_rate} bpm
        - Condition: {condition}

        Reply with ONLY a clear and structured checklist for configuring a LUCAS CPR device, with maximum 50 sentences.

        Format:
        Smart LUCAS CPR Summary:
        - Compression Rate: [value] bpm
        - Compression Depth: [value] cm
        - Session Duration: [value] mins
        - Pad Position: [description]
        - Special Notes: [short tip]

        Keep it short and clinical.
        """

        try:
            response = model.generate_content(prompt)
            instructions = response.text.strip()
            st.session_state.last_result = instructions

            st.subheader("✅ AI-Generated CPR Instructions")
            st.code(instructions, language="markdown")

            def generate_pdf(text):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Smart LUCAS CPR Instructions", ln=True, align="C")
                pdf.cell(200, 10, txt=f"Generated at: {now}", ln=True, align="C")
                pdf.ln(10)
                for line in text.split("\n"):
                    pdf.multi_cell(0, 10, line)
                return pdf.output(dest='S').encode('latin-1')

            pdf_bytes = generate_pdf(instructions)
            st.download_button("📄 Download as PDF", data=pdf_bytes, file_name="CPR_Instructions.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# --- Show Last CPR Result ---
if st.session_state.last_result:
    st.markdown("### 📋 Last Generated CPR Instructions")
    st.code(st.session_state.last_result, language="markdown")

# -------------------------------
# --- First Aid Chatbot Section
# -------------------------------
st.divider()
st.header("💬 First Aid Chatbot")

# Display previous conversation
for msg in chat.history:
    with st.chat_message(msg.role):
        st.markdown(msg.parts[0].text)

# Input box
user_msg = st.chat_input("Ask anything about first aid...")

if user_msg:
    with st.chat_message("user"):
        st.markdown(user_msg)

    prompt = f"""
    You are a helpful first aid assistant chatbot.
    The user is asking: {user_msg}

    Provide simple, clear, step-by-step instructions (in plain English).
    Do not diagnose. Just guide them practically based on the emergency.
    Limit to 5 short steps if possible.
    """

    try:
        reply = chat.send_message(prompt).text
        with st.chat_message("assistant"):
            st.markdown(reply)
    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"⚠️ Error: {str(e)}")
