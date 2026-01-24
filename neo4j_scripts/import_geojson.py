import sys
import os
import json
import yaml
from py2neo import Graph, Node, Relationship
from pyproj import Transformer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.config_loader import load_config

# config.yaml 파일 읽기
cfg = load_config()
NEO4J_URI = os.environ.get("NEO4J_URI", cfg["neo4j"]["uri"])
NEO4J_USER = os.environ.get("NEO4J_USER", cfg["neo4j"]["user"])
NEO4J_PASS = os.environ.get("NEO4J_PASS", cfg["neo4j"]["password"])
GEOJSON_PATH = os.environ.get("GEOJSON_PATH", cfg["geojson_path"])

print(f"Neo4j 연결 시도: {NEO4J_URI}")
print(f"GeoJSON 데이터 경로: {GEOJSON_PATH}")

# Neo4j 서버 연결
try:
    graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
except Exception as e:
    print(f"Neo4j 연결 실패: {e}")
    sys.exit(1)

# GeoJSON 데이터 읽기
if not os.path.exists(GEOJSON_PATH):
    print(f"오류: GeoJSON 파일을 찾을 수 없습니다 ({GEOJSON_PATH})")
    sys.exit(1)

with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# 좌표계 변환 설정: EPSG:5179 (KOREA 2000) -> EPSG:4326 (WGS84, 위경도)
transformer = Transformer.from_crs(
    "EPSG:5179",
    "EPSG:4326",
    always_xy=True
)

# 노드 및 관계 생성 로직
print("데이터 Import를 시작합니다...")

count = 0
for feature in geojson_data["features"]:
    props = feature["properties"]

    # 좌표 변환 수행
    try:
        start_x, start_y = feature["geometry"]["coordinates"][0][0]
        end_x, end_y = feature["geometry"]["coordinates"][0][-1]
        start_lon, start_lat = transformer.transform(start_x, start_y)
        end_lon, end_lat = transformer.transform(end_x, end_y)
    except (IndexError, ValueError) as e:
        print(f"유효하지 않은 geometry 형태 건너뜀: {e}")
        continue

    # 역(Station) 노드 생성
    start_station = Node(
        "Station",
        name=props["F_NAME"],
        code=props["AF_F_N"],
        lat=start_lat,
        lon=start_lon
    )
    end_station = Node(
        "Station",
        name=props["T_NAME"],
        code=props["AF_T_N"],
        lat=end_lat,
        lon=end_lon
    )

    # 중복 방지를 위해 'code' 기준으로 병합(Merge)
    graph.merge(start_station, "Station", "code")
    graph.merge(end_station, "Station", "code")

    # 노선(RailLine) 노드 생성
    line_name = props.get("R_NAME_1") or "Unknown Line"
    rail_line = Node("RailLine", name=line_name)
    graph.merge(rail_line, "RailLine", "name")

    # 구간(Segment) 노드 생성
    segment = Node(
        "Segment",
        from_code=props["AF_F_N"],
        to_code=props["AF_T_N"],
        line=line_name,
        avg_dist=props.get("AVG_DIST"),
        avg_time=props.get("AVG_TIME"),
        speed=props.get("speed"),
        isKTX=props.get("isKTX")
    )

    # 구간은 출발지, 도착지, 노선명이 같으면 중복으로 간주
    graph.merge(segment, "Segment", ("from_code", "to_code", "line"))

    # Relationship 연결
    graph.merge(Relationship(start_station, "HAS_SEGMENT", segment))
    graph.merge(Relationship(segment, "TO", end_station))
    graph.merge(Relationship(segment, "ON_LINE", rail_line))

    # 경로 탐색용 직접 연결 관계
    graph.merge(Relationship(start_station, "CONNECTS", end_station))
    graph.merge(Relationship(end_station, "CONNECTS", start_station))

    # 메타 데이터 관계 (역(Station)이 노선(RailLine)에 속하게 함)
    graph.merge(Relationship(start_station, "ON_LINE", rail_line))
    graph.merge(Relationship(end_station, "ON_LINE", rail_line))

    count += 1
    if count % 1000 == 0:
        print(f"   {count}개 구간(Segment) 처리 중...")

print(f"데이터 Import 완료! 총 처리된 구간(Segment) 수: {count}")