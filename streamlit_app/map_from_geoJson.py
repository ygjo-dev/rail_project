import os
import json
import streamlit as st
import folium
from streamlit_folium import st_folium

# -----------------------------
# 환경 변수 및 설정 파일 로드
# -----------------------------
CONFIG_FILE = os.environ.get("CONFIG_FILE", "config.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    cfg = json.load(f)

GEOJSON_PATH = os.environ.get("GEOJSON_PATH", cfg["geojson_path"])

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("철도 데이터 Streamlit 테스트")

# GeoJSON 읽기
with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

st.success("GeoJSON 데이터 로드 완료!")

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=7)  # 서울 기준

# GeoJSON 레이어 추가
folium.GeoJson(geojson_data).add_to(m)

# Streamlit에 표시
st_folium(m, width=700, height=500)
