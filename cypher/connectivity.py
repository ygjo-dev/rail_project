# cypher/connectivity.py
def check_connectivity(graph, from_station: str, to_station: str) -> bool:
    """
    Neo4j에서 출발역 -> 도착역 연결 가능 여부 확인
    최대 10단계까지 연결 탐색, 순환 제거 없이 경로 존재만 확인
    """
    query = """
    MATCH (a:Station)-[:CONNECTS*1..5]->(b:Station)
    WHERE a.name CONTAINS $from_station
      AND b.name CONTAINS $to_station
    RETURN count(*) > 0 AS is_connected
    """

    result = graph.run(
        query,
        from_station=from_station,
        to_station=to_station
    ).data()

    return bool(result and result[0]["is_connected"])
