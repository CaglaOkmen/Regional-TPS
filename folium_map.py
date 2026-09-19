import folium 
from folium import plugins
import networkx as nx

# Folium Harita Çizimi
def draw_map(G, regions, paths_dict, lengths_dict, radius, name):
    # Harita merkezi
    centers = [r["center"] for r in regions.values()]
    lat = sum(G.nodes[n]['y'] for n in centers) / len(centers)
    lon = sum(G.nodes[n]['x'] for n in centers) / len(centers)
    m = folium.Map(location=[lat, lon], zoom_start=13)

    # Bölgeleri ciz
    for r_id, r in regions.items():
        c = r["center"]
        folium.Circle(
            location=[G.nodes[c]['y'], G.nodes[c]['x']],
            radius=radius, color="gray", fill=True, fill_opacity=0.1,
            popup=f"Bölge Merkezi: {c}"
        ).add_to(m)

    colors = {'Heuristic': 'blue', 'OR-Tools': 'red', 'Genetic': 'green'}
    
    legend_items = []

    # Her Yontem İçin Yolları ve Noktaları Çiz
    for method_name, path in paths_dict.items():
        if not path: continue
        
        c_code = colors.get(method_name, 'black')
        dist_km = lengths_dict.get(method_name, 0) / 1000.0
        
        legend_items.append(
            f'&nbsp; <i style="background:{c_code}; width:10px; height:10px; display:inline-block;"></i> '
            f'<b>{method_name}:</b> {dist_km:.2f} km')
        
        # Seçilen Noktaları İşaretle
        for node in path:
            folium.CircleMarker(
                location=[G.nodes[node]['y'], G.nodes[node]['x']],
                radius=4, color=c_code, fill=True, fill_opacity=1.0,
                popup=f"{method_name}: {node}"
            ).add_to(m)

        # Rotayı Çiz
        route_coords = []
        for i in range(len(path) - 1):
            try:
                sp = nx.shortest_path(G, path[i], path[i + 1], weight="length")
                for node_id in sp:
                    route_coords.append((G.nodes[node_id]['y'], G.nodes[node_id]['x']))
            except nx.NetworkXNoPath: 
                continue
        
        if route_coords:
            folium.PolyLine(
                route_coords, 
                color=c_code, 
                weight=3, 
                opacity=0.7, 
                # Yolun üzerine gelince mesafe yazar
                tooltip=f"{method_name} Yolu ({dist_km:.2f} km)"
            ).add_to(m)

    # Dinamik Lejant (Bilgi Kutusu) Oluşturma
    legend_html = f'''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 220px; height: auto; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white; opacity:0.9; padding: 10px;">
     <b>Sonuçlar (Toplam Mesafe):</b> <br>
     {"<br>".join(legend_items)}
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    import os
    os.makedirs(os.path.join("outputs", "maps"), exist_ok=True)
    filename = os.path.join("outputs", "maps", f"{name}.html")
    m.save(filename)