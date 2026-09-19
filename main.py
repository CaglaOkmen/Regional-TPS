import osmnx as ox
import networkx as nx
import random
import time
import pandas as pd
import numpy as np
import os

from ortools_metot import tps_ortool
from greedy_intertion import tps_insertion
from genetic import tps_genetic
from folium_map import draw_map
from comparison_graphs import comparison

random.seed(9)
np.random.seed(9)

def neighborhoods(point_node, G, radius):
    lengths = nx.single_source_dijkstra_path_length(G, point_node, cutoff=radius, weight="length")
    return list(lengths.keys())

def generate_graph(G, size):
    nodes = list(G.nodes())
    N = nx.Graph() 
    point_nodes = []

    # Baglanti kontrolu eklendi Eklendi
    # Bağlantısı Olmayan Nodeları Alma
    while len(point_nodes) < size:
        candidate = random.choice(nodes)
        # Eger daha once secilmisse gec
        if candidate in point_nodes: 
            continue
        ok = True
        for n in point_nodes:
            if not (nx.has_path(G, candidate, n)):
                ok = False
                break      
        if ok:
            point_nodes.append(candidate)

    # Node icerigi {'y': 40.1961554, 'x': 28.9545733, 'street_count': 3}
    # Rastgele alınan Node larla yeni graf olustur 
    for i in range(len(point_nodes)):
       N.add_node(point_nodes[i], x = G.nodes[point_nodes[i]]['x'], y = G.nodes[point_nodes[i]]['y'])
    return N

# Mesafe matrisini önceden hesaplayarak islem süresini azaltma
def precompute_distances(G, all_candidate_nodes):
    dist_matrix = {}
    print(f"Mesafe Matrisi Önbelleğe Alınıyor ({len(all_candidate_nodes)} düğüm)...")

    for source in all_candidate_nodes:
        lengths = nx.single_source_dijkstra_path_length(G, source, weight="length")
        dist_matrix[source] = lengths
        
    return dist_matrix

# Ana program
if __name__ == '__main__':
    place = "Nilüfer, Bursa, Turkey"
    map_file = "bursa_nilufer_static.graphml" # Sabit Harita Dosyası
    
    # Harita yukleme
    if os.path.exists(map_file):
        print(f"Sabit harita '{map_file}' dosyasından yükleniyor...")
        G = ox.load_graphml(map_file)
    else:
        print("Harita internetten indiriliyor ve sabitleniyor (Sadece 1 kez)...")
        G = ox.graph_from_place(place, network_type='drive')
        G = ox.truncate.largest_component(G, strongly=True)
        
        # Haritayı kaydet
        ox.save_graphml(G, map_file)
        print(f"Harita '{map_file}' olarak kaydedildi.")
    
    print("Harita hazır.")

    # Sonuçları tutacak listeler
    heur_sums, heur_times = [], []
    ortool_sums, ortool_times = [], []
    gen_sums, gen_times = [], []

    for i in range(30):
        # seed ayarla
        random.seed(i + 1)
        np.random.seed(i + 1)
        print(f"\n{i + 1}.Topoloji Çalışıyor...")
        
        N = generate_graph(G, 10) 
        
        search_radius = 200 
        regions_dict = {} 
        regions_info = {} 
        all_involved_nodes = set() 
        
        # bolgeleri olusturma
        for center in N.nodes():
            neighbors = neighborhoods(center, G, search_radius)
            if not neighbors: 
                neighbors = [center]
            regions_dict[center] = neighbors
            regions_info[f"R{center}"] = {"center": center, "nodes": neighbors}
            all_involved_nodes.update(neighbors)
        
        # Mesafeleri onceden hesapla
        t0 = time.time()
        dist_matrix = precompute_distances(G, list(all_involved_nodes))

        # heuristic yontemi
        start_heur = time.time()
        heuristic_sum, heuristic_path = tps_insertion(N, dist_matrix, regions_dict)
        heur_times.append(time.time() - start_heur)
        heur_sums.append(heuristic_sum / 1000)

        # Or-tool yontemi
        start_ortool = time.time()
        ortool_sum, ortool_path = tps_ortool(dist_matrix, regions_dict) 
        ortool_times.append(time.time() - start_ortool)
        ortool_sums.append(ortool_sum / 1000)

        # Genetik yontemi
        start_gen = time.time()
        gen_path, gen_fit = tps_genetic(dist_matrix, regions_dict, pop_size=50, mutation_rate=0.1, generations=20)
        gen_times.append(time.time() - start_gen)
        gen_sums.append(gen_fit / 1000)

        # 5 topoloji de bir harita çizdir
        if (i + 1) % 5 == 0:
            print(f"   > {i+1}. Topoloji için Haritalar oluşturuluyor...")
            
            current_lengths = {
                'Heuristic': heuristic_sum,
                'OR-Tools': ortool_sum,
                'Genetic': gen_fit
            }
            paths_combined = {
                'Heuristic': heuristic_path,
                'OR-Tools': ortool_path,
                'Genetic': gen_path
            }
            draw_map(G, regions_info, paths_combined, current_lengths, search_radius, f"Topoloji_{i+1}_Karsilastirma")

            # Ayrı ayrı haritalar
            if heuristic_path:
                draw_map(G, regions_info, {'Heuristic': heuristic_path}, current_lengths, search_radius, f"Topoloji_{i+1}_Heuristic")
            if ortool_path:
                draw_map(G, regions_info, {'OR-Tools': ortool_path}, current_lengths, search_radius, f"Topoloji_{i+1}_ORTools")   
            if gen_path:
                draw_map(G, regions_info, {'Genetic': gen_path}, current_lengths, search_radius, f"Topoloji_{i+1}_Genetic")
            
            print(f"Haritalar kaydedildi (T{i+1})")
    # Pandas ile Sonucları kaydetme
    df = pd.DataFrame({
        'Topoloji_No': range(1, len(heur_sums) + 1),
        'Heuristic_Sum_km': heur_sums,
        'Heuristic_Time_s': heur_times,
        'OR_Tools_Sum_km': ortool_sums,
        'OR_Tools_Time_s': ortool_times,
        'Genetic_Sum_km': gen_sums,
        'Genetic_Time_s': gen_times
    })
    
    os.makedirs("outputs", exist_ok=True)
    df.to_csv(os.path.join("outputs", "regional_tsp_results.csv"), index=False)
    print("\nVeriler 'outputs/regional_tsp_results.csv' dosyasına kaydedildi.")
    comparison(heur_sums, heur_times, ortool_sums, ortool_times, gen_sums, gen_times)