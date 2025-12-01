import streamlit as st
import json
import folium
from streamlit_folium import st_folium

st.title("철도 데이터 Streamlit 테스트")

# GeoJSON 읽기
with open("../data/2020_전국철도_utmk.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

st.write("GeoJSON 데이터 로드 완료!")

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=7)  # 서울 기준

# GeoJSON 레이어 추가
folium.GeoJson(geojson_data).add_to(m)

st_folium(m, width=700, height=500)