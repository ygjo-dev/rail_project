# cypher/transfers.py
from py2neo import Graph

def count_transfers(graph: Graph, from_station: str, to_station: str, max_hops: int = 5) -> int:
    """
    출발역 -> 도착역 최소 환승 횟수 계산
    APOC 없이 구현, 순환 경로 방지
    max_hops: 탐색 최대 단계
    반환값:
        최소 환승 횟수 (0이면 직행, 경로 없으면 -1)
    """
    query = f"""
    MATCH p=(a:Station)-[:CONNECTS*1..{max_hops}]->(b:Station)
    WHERE a.name CONTAINS $from_station AND b.name CONTAINS $to_station
    RETURN [n IN nodes(p) | n.name] AS path_nodes
    """

    results = graph.run(query, from_station=from_station, to_station=to_station).data()

    if not results:
        return -1  # 경로 없음

    # 순환 제거 및 최소 환승 계산
    min_transfers = None
    for record in results:
        nodes = record["path_nodes"]
        if len(nodes) != len(set(nodes)):
            continue  # 순환 경로 무시
        transfers = len(nodes) - 2  # 출발-도착 제외
        if min_transfers is None or transfers < min_transfers:
            min_transfers = transfers

    return min_transfers if min_transfers is not None else -1
