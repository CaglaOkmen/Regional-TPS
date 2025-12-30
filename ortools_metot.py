from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Ortool tam sayıya donuşturmesinden elde edilen 
# kayıpların olamamsı için Toplam yolun tekrar hesaplanır
def sum_distance(dist_matrix, path):
    total_dist = 0
    for i in range(len(path) - 1):
        try:
            total_dist += dist_matrix[path[i]][path[i+1]]
        except KeyError:
            pass 
    return total_dist

def create_data_matrix(all_nodes, dist_matrix):
    dis_matrix_list = []
    
    for node1 in all_nodes:
        row = []
        for node2 in all_nodes:
            if node1 == node2:
                row.append(0)
            else:
                try:
                    # Ortool  tam sayı kabul ettigi icin donusturuldu
                    val = int(dist_matrix[node1][node2] * 10000)
                    row.append(val)
                except KeyError:
                    # Yol yoksa çok buyuk ceza 
                    row.append(100000000)
        dis_matrix_list.append(row)
    
    return dis_matrix_list

# Or-tool ile TPS çözümü
def tps_ortool(dist_matrix, regions):
    all_nodes = []
    region_indices = []
    
    current_idx = 0
    # Her bölgedeki node'ların matristeki indekslerini grupla
    for center, nodes in regions.items():
        indices_in_this_region = []
        for node in nodes:
            all_nodes.append(node)
            indices_in_this_region.append(current_idx)
            current_idx += 1
        region_indices.append(indices_in_this_region)

    # Matris olusturma
    matris = create_data_matrix(all_nodes, dist_matrix)
    if not matris: return 0, []
    
    # Konum sayıları, mesafe matrisine ilişkin dizinlere karşılık gelir.
    manager = pywrapcp.RoutingIndexManager(len(matris), 1, 0) 
    routing = pywrapcp.RoutingModel(manager)

    # Mesafeyi geri cagirma
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matris[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Her bolgeden sadece 1 node seçer
    penalty = int(1e14) 
    for indices in region_indices:
        routing.AddDisjunction(indices, penalty)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    # Daha iyi sonuc icin local search metodu
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 5 # zaman siniri

    solution = routing.SolveWithParameters(search_parameters)

    # Sonuç
    if solution:
        index = routing.Start(0)
        path = []
        
        # Sadece node ID'lerini sırayla al
        while not routing.IsEnd(index):
            node_idx = manager.IndexToNode(index)
            path.append(all_nodes[node_idx])
            index = solution.Value(routing.NextVar(index))
        path.append(all_nodes[manager.IndexToNode(index)])

        real_total_dist = sum_distance(dist_matrix, path)
        return real_total_dist, path   
    else:
        return 0, []