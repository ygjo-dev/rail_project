# 1. GPU 지원을 위해 CUDA가 포함된 베이스 이미지 사용
FROM nvidia/cuda:12.1.0-base-ubuntu22.04

# 2. 필수 시스템 패키지 및 파이썬 설치
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python-is-python3 \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. 라이브러리 설치 (Clean 버전 사용 권장)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사
COPY . .

# 5. 실행 명령
CMD ["streamlit", "run", "streamlit_app/map_from_neo4j.py"]