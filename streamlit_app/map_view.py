import folium
from streamlit_folium import st_folium


def render_map(graph):

    stations = graph.run(
        """
        MATCH (s:Station)
        WHERE s.lat IS NOT NULL
          AND s.lon IS NOT NULL
        RETURN
            s.name AS name,
            s.lat AS lat,
            s.lon AS lon
        """
    ).data()

    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=7
    )

    for station in stations:

        folium.Marker(
            location=[
                station["lat"],
                station["lon"]
            ],
            popup=station["name"],
            icon=folium.Icon(
                color="blue",
                icon="train",
                prefix="fa"
            )
        ).add_to(m)

    st_folium(
        m,
        width=750,
        height=500
    )