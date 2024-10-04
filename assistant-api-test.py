import paramiko
from openai import OpenAI
import os
import time

# OpenAI API 키 세팅
OPENAI_API_KEY = 'KEY'
# ASSISTANT_ID 세팅
ASSISTANT_ID = 'ASSISTANT_ID'

client = OpenAI(api_key=OPENAI_API_KEY)

# 서버 접속 정보 설정
SERVER_HOST = 'your-server-ip'
SERVER_PORT = 22
USERNAME = 'your-username'
PASSWORD = 'your-password'  # 또는 SSH 키를 사용할 경우 경로로 대체 가능
REMOTE_LOG_PATH = '/path/to/remote/logfile.log'
LOCAL_LOG_PATH = 'logfile-path'

def fetch_log_file_from_server():
    """
    서버에 SSH로 접속하여 로그 파일을 로컬로 다운로드하는 함수.
    """
    # Paramiko 클라이언트 설정
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 서버에 SSH 접속
        ssh_client.connect(SERVER_HOST, port=SERVER_PORT, username=USERNAME, password=PASSWORD)

        # SFTP 세션 시작
        sftp = ssh_client.open_sftp()
        print("서버에서 로그 파일 다운로드 중...")

        # 원격 로그 파일을 로컬로 다운로드
        sftp.get(REMOTE_LOG_PATH, LOCAL_LOG_PATH)
        print(f"로그 파일 다운로드 완료: {LOCAL_LOG_PATH}")
        
        # SFTP 및 SSH 세션 종료
        sftp.close()
        ssh_client.close()

    except Exception as e:
        print(f"로그 파일 다운로드 중 오류 발생: {e}")
        return None

def read_log_file(file_path):
    """
    로그 파일을 읽어 내용 반환.
    """
    with open(file_path, 'r') as file:
        return file.read()

def analyze_log_with_custom_gpt(log_content):
    """
    OpenAI GPTs 모델을 사용하여 로그 파일을 분석하는 함수.
    """
    try:
        # 새로운 스레드 생성
        thread_response = client.beta.threads.create()

        # 생성된 스레드의 ID
        thread_id = thread_response.id
        print(f"New thread created with ID: {thread_id}")
        
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"다음 서버 로그 파일의 내용을 분석해줘: {log_content}"
        )
        
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            time.sleep(0.5)
        
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="asc"
        )
        return messages
    except Exception as e:
        print(f"GPT 모델을 통한 분석 중 오류 발생: {e}")
        return None


def print_message(response):
    for res in response:
        print(f"==>{res.content[0].text.value}\n")


def main():
    """
    전체 흐름을 처리하는 메인 함수.
    1. 서버에 접속하여 로그 파일 다운로드
    2. 로그 파일 읽기
    3. GPT 모델을 통해 분석 수행
    """
    # 서버에서 로그 파일을 가져옴
    fetch_log_file_from_server()

    # 로그 파일이 존재하면 내용을 읽음
    if os.path.exists(LOCAL_LOG_PATH):
        log_content = read_log_file(LOCAL_LOG_PATH)
        print("로그 파일 내용 읽기 완료.")
        
        # GPT 모델을 통해 로그 파일 분석
        analysis_result = analyze_log_with_custom_gpt(log_content)
        
        if analysis_result:
            print("분석 결과:")
            print_message(analysis_result.data[-2:])
        else:
            print("분석 실패.")
    else:
        print(f"로그 파일을 찾을 수 없습니다: {LOCAL_LOG_PATH}")

if __name__ == "__main__":
    main()
