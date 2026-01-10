# cypher/connectivity.py

def check_connectivity(graph, from_station: str, to_station: str) -> bool:
    query = """
    MATCH (a:Station)-[:CONNECTS]->(b:Station)
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
