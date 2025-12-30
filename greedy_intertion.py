import random

# Ziyaret edilmemiş Nodlar arasından eklenmesi en ucuz Node u seçer ve yola ekleyerek dondurur.
def best_node_add(dist_matrix, path, unvisited_regions, regions):
    sm_dis = float('inf')
    best_region = None
    best_node_in_region = None
    insert_index = -1
    
    for region_center in unvisited_regions:
        candidates = regions[region_center]
        for candidate_node in candidates:
            # Mevcut yoldaki aralıklara ekleme maliyeti
            for i in range(len(path) - 1):
                n1 = path[i]
                n2 = path[i + 1]
                
                try:
                    d1 = dist_matrix[n1][candidate_node]
                    d2 = dist_matrix[candidate_node][n2]
                    base_dist = dist_matrix[n1][n2]
                    
                    distance = d1 + d2 - base_dist
                    
                    if distance < sm_dis:
                        sm_dis = distance
                        insert_index = i + 1
                        best_node_in_region = candidate_node
                        best_region = region_center
                except KeyError:
                    continue

    if best_region is not None:
        path.insert(insert_index, best_node_in_region)
        return path, best_region
    return path, None

# heuristic algoritma uygulamasi
def tps_insertion(N, dist_matrix, regions):
    unvisited_regions = list(regions.keys()) 

    # Random 3 Node belirle
    init_centers = random.sample(unvisited_regions, 3)
    path = [random.choice(regions[c]) for c in init_centers]
    
    for c in init_centers:
        unvisited_regions.remove(c)

    path.append(path[0]) 

    # Tum Nodelar ziyaret edilene kadar calistir. En iyi node veren yolu gunceller
    while unvisited_regions:
        path, visited_region = best_node_add(dist_matrix, path, unvisited_regions, regions)
        if visited_region:
            unvisited_regions.remove(visited_region)
            
    # Toplam yolu hesapla
    total_dist = 0
    for i in range(len(path)-1):
        total_dist += dist_matrix[path[i]][path[i+1]]
        
    return total_dist, path