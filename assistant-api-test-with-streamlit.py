import streamlit as st
import time
from openai import OpenAI


def analyze_log_with_custom_gpt(log_content):
    try:
        thread_response = client.beta.threads.create()
        thread_id = thread_response.id
        message = client.beta.threads.messages.create(thread_id=thread_id, role="user", content=f"Analyze log: {log_content}")
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)

        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            time.sleep(0.5)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return messages
    except Exception as e:
        st.error(f"Error: {e}")
        return None


# OpenAI API 키 세팅
OPENAI_API_KEY = 'KEY'
ASSISTANT_ID = 'ASSISTANT_ID'
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit 인터페이스
st.title("서버 로그 파일 분석")
st.write("로그 파일을 OpenAI GPT 모델을 사용해 분석합니다.")

# 파일 선택
log_file = st.file_uploader("로그 파일을 선택하세요", type=['txt', 'log', 'rtf'])

if log_file is not None:
    log_content = log_file.read().decode("utf-8")
    st.write("로그 파일 내용:")
    st.text(log_content)

    if st.button("Analyze Log"):
        with st.spinner("Analyzing..."):
            analysis_result = analyze_log_with_custom_gpt(log_content)
        if analysis_result:
            st.success("분석 완료!")
            st.write(analysis_result.data[0].content[0].text.value)
        else:
            st.error("분석 실패!")
