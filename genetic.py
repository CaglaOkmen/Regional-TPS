import random
import numpy as np

# Yolun Toplam uzunlugunu hesapla
def sum_distance(dist_matrix, path):
    sum = 0
    for i in range(len(path) - 1):
        sum += dist_matrix[path[i]][path[i + 1]]
    
    # son node ile ilk noduda hesaplama
    sum += dist_matrix[path[-1]][path[0]]

    return sum

# Populasyon oluşturma  
def create_population(pop_size, regions):
    population = []
    region_keys = list(regions.keys()) 
    for _ in range(pop_size):
        individual = []
        random.shuffle(region_keys) 
        for r_key in region_keys:
            selected_node = random.choice(regions[r_key])
            individual.append((r_key, selected_node)) 
        population.append(individual)
    return population

# Populasyonu değerlendirme
def evaluate_population(population, dist_matrix):
    fitness_scores = []
    for indiv in population:
        path_nodes = [node for _, node in indiv]
        fitness_scores.append(sum_distance(dist_matrix, path_nodes))
    return fitness_scores

# Seçim işlemi
def select(population, fitness_scores, num_best):
    selected_indices = np.argsort(fitness_scores)[:num_best]
    return [population[i] for i in selected_indices]

# Çaprazlama işlemi
def crossover(parent1, parent2):
    start, end = sorted(random.sample(range(len(parent1)), 2))
    child = [None] * len(parent1)
    child[start:end] = parent1[start:end]
    current_regions = set(x[0] for x in child if x is not None)
    pointer = 0
    for i in parent2:
        r_id, _ = i
        if r_id not in current_regions:
            while child[pointer] is not None: pointer += 1
            child[pointer] = i
            current_regions.add(r_id)
    return child

# Mutasyon işlemi
def mutate(individual, mutation_rate, regions):
    # bolge siralamasi degistirme
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
    # bolge icerisinden farkli node ile degistirme
    if random.random() < mutation_rate:
        idx = random.randint(0, len(individual) - 1)
        r_id, _ = individual[idx]
        new_node = random.choice(regions[r_id])
        individual[idx] = (r_id, new_node)

# Genetik algoritma ana fonksiyonu
def tps_genetic(dist_matrix, regions, pop_size, mutation_rate, generations):
    population = create_population(pop_size, regions)
    best_path_nodes = None
    best_fitness = float('inf')

    elite_ratio = 0.1
    elit_count = max(1, int(pop_size * elite_ratio))

    for _ in range(generations):
        fitness_scores = evaluate_population(population, dist_matrix)
        
        min_idx = np.argmin(fitness_scores)
        if fitness_scores[min_idx] < best_fitness:
            best_fitness = fitness_scores[min_idx]
            best_path_nodes = [node for _, node in population[min_idx]]
        
        elite_indices = np.argsort(fitness_scores)[:elit_count]
        new_population = [population[i].copy() for i in elite_indices]

        selected = select(population, fitness_scores, pop_size // 2)

        while len(new_population) < pop_size:
            parent1, parent2 = random.sample(selected, 2)
            child = crossover(parent1, parent2)
            mutate(child, mutation_rate, regions)
            new_population.append(child)
        population = new_population

    best_path_nodes.append(best_path_nodes[0])
    return best_path_nodes, best_fitness