import os
import json
from py2neo import Graph, Node, Relationship
from pyproj import Transformer

# -----------------------------
# 환경 변수 및 설정 파일 로드
# -----------------------------
CONFIG_FILE = os.environ.get("CONFIG_FILE", "../config/config.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    cfg = json.load(f)

NEO4J_URI = os.environ.get("NEO4J_URI", cfg["neo4j"]["uri"])
NEO4J_USER = os.environ.get("NEO4J_USER", cfg["neo4j"]["user"])
NEO4J_PASS = os.environ.get("NEO4J_PASS", cfg["neo4j"]["password"])
GEOJSON_PATH = os.environ.get("GEOJSON_PATH", cfg["geojson_path"])

# -----------------------------
# Neo4j 연결
# -----------------------------
graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# -----------------------------
# GeoJSON 읽기
# -----------------------------
with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# 좌표계 변환 EPSG:5179 -> EPSG:4326
transformer = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)

# -----------------------------
# 노드 / 관계 생성
# -----------------------------
for feature in geojson_data["features"]:
    props = feature["properties"]

    # 출발 / 도착 좌표
    start_x, start_y = feature["geometry"]["coordinates"][0][0]
    end_x, end_y = feature["geometry"]["coordinates"][0][-1]
    start_lon, start_lat = transformer.transform(start_x, start_y)
    end_lon, end_lat = transformer.transform(end_x, end_y)

    # -----------------------------
    # Station 노드
    # -----------------------------
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

    graph.merge(start_station, "Station", "code")
    graph.merge(end_station, "Station", "code")

    # -----------------------------
    # RailLine 노드
    # -----------------------------
    line_name = props.get("R_NAME_1") or "Unknown Line"
    rail_line = Node("RailLine", name=line_name)
    graph.merge(rail_line, "RailLine", "name")

    # -----------------------------
    # Segment 노드 (속성 전담, merge 기준 명확)
    # -----------------------------
    segment = Node(
        "Segment",
        from_code=props["AF_F_N"],
        to_code=props["AF_T_N"],
        line=line_name,
        avg_dist=props["AVG_DIST"],
        avg_time=props["AVG_TIME"],
        speed=props["speed"],
        isKTX=props["isKTX"]
    )

    graph.merge(segment, "Segment", ("from_code", "to_code", "line"))

    # -----------------------------
    # Segment 관계
    # -----------------------------
    graph.merge(Relationship(start_station, "HAS_SEGMENT", segment))
    graph.merge(Relationship(segment, "TO", end_station))
    graph.merge(Relationship(segment, "ON_LINE", rail_line))

    # -----------------------------
    # Station ↔ Station (경로 탐색용 핵심)
    # -----------------------------
    graph.merge(Relationship(start_station, "CONNECTS", end_station))
    graph.merge(Relationship(end_station, "CONNECTS", start_station))

    # -----------------------------
    # Station ↔ RailLine (보조 질의용)
    # -----------------------------
    graph.merge(Relationship(start_station, "ON_LINE", rail_line))
    graph.merge(Relationship(end_station, "ON_LINE", rail_line))

print("GeoJSON → Neo4j (CONNECTS + Segment 모델) 변환 완료!")
