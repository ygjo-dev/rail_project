from py2neo import Graph, Node, Relationship
import json
from pyproj import Transformer

# Neo4j 연결
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "password"))

# GeoJSON 읽기
with open("../data/2020_전국철도_utmk.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# 좌표계 변환 EPSG:5179 -> EPSG:4326 (위도/경도)
transformer = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)

# 노드/관계 생성
for feature in geojson_data['features']:
    props = feature['properties']

    # 출발/도착 좌표 평균 계산
    start_x, start_y = feature['geometry']['coordinates'][0][0]
    end_x, end_y = feature['geometry']['coordinates'][0][-1]
    start_lon, start_lat = transformer.transform(start_x, start_y)
    end_lon, end_lat = transformer.transform(end_x, end_y)

    # Station 노드 생성 
    start_station = Node("Station",
                         name=props["F_NAME"],
                         code=props["AF_F_N"],
                         lat=start_lat,
                         lon=start_lon)
    end_station = Node("Station",
                       name=props["T_NAME"],
                       code=props["AF_T_N"],
                       lat=end_lat,
                       lon=end_lon)

    graph.merge(start_station, "Station", "code")
    graph.merge(end_station, "Station", "code")

    # RailLine 노드 생성
    line_name = props.get("R_NAME_1") or "Unknown Line"
    rail_line = Node("RailLine", name=line_name)
    graph.merge(rail_line, "RailLine", "name")

    # 역 <-> 노선 연결
    graph.merge(Relationship(start_station, "ON_LINE", rail_line))
    graph.merge(Relationship(end_station, "ON_LINE", rail_line))

    # 역 <-> 역 관계
    connect_props = {
        "avg_dist": props["AVG_DIST"],
        "avg_time": props["AVG_TIME"],
        "speed": props["speed"],
        "isKTX": props["isKTX"]
    }

    rel1 = Relationship(start_station, "CONNECTS", end_station, **connect_props)
    rel2 = Relationship(end_station, "CONNECTS", start_station, **connect_props)
    graph.merge(rel1)
    graph.merge(rel2)

print("GeoJSON → Neo4j 완료!")
