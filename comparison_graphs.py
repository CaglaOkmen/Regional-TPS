import matplotlib.pyplot as plt
import numpy as np

# Grafik Çizdirme
def comparison(heur_sums, heur_times, ortool_sums, ortool_times, gen_sums, gen_times):
    num_topologies = len(heur_sums)
    x_axis = range(1, num_topologies + 1)

    # Yol Grafigi
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, heur_sums, label='Regional Heuristic', marker='o', linestyle='--')
    plt.plot(x_axis, ortool_sums, label='Regional OR-Tools', marker='o', linestyle='-.')
    plt.plot(x_axis, gen_sums, label='Regional Genetic', marker='o', markerfacecolor='none', linestyle=':')

    plt.xlabel('Topoloji Numarası')
    plt.ylabel('Toplam Mesafe')
    plt.title('Bölgesel TSP Yol Karşılaştırması')
    plt.legend()
    plt.grid(True, alpha=0.3)

    import os
    os.makedirs("outputs", exist_ok=True)

    plt.savefig(os.path.join("outputs", "karsilastirma_mesafe.png"), dpi=150)

    # Zaman Grafiği
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, heur_times, label='Regional Heuristic', marker='o', linestyle='--')
    plt.plot(x_axis, ortool_times, label='Regional OR-Tools', marker='o', linestyle='-.')
    plt.plot(x_axis, gen_times, label='Regional Genetic', marker='o', markerfacecolor='none', linestyle=':')
    
    plt.yscale('symlog', linthresh=1e-4) # çok küçükleri görünür yapar

    plt.xlabel('Topoloji Numarası')
    plt.ylabel('Süre (saniye) - symlog')
    plt.title('Algoritma Çalışma Süreleri')
    plt.legend()
    plt.xticks(x_axis)
    plt.grid(True, which="both", linestyle='--', linewidth=0.5, alpha=0.7)

    plt.savefig(os.path.join("outputs", "karsilastirma_zaman.png"), dpi=150)

    # Ortool ile diğer metotların karşılaştırması (y=x)
    plt.figure(figsize=(8, 8))
    
    # Scatter noktaları
    plt.scatter(ortool_sums, heur_sums, c='blue', label='Heuristic vs OR-Tools')
    plt.scatter(ortool_sums, gen_sums, c='green', label='Genetic vs OR-Tools')
    
    # y=x Referans Çizgisi
    # Eksen limitlerini belirle
    all_values = heur_sums + ortool_sums + gen_sums
    min_val = min(all_values) * 0.95
    max_val = max(all_values) * 1.05
    
    plt.plot([min_val, max_val], [min_val, max_val], color='orange', linestyle='--', linewidth=2, label='y=x (Or-Tools)')
    
    plt.xlim(min_val, max_val)
    plt.ylim(min_val, max_val)
    plt.xlabel('OR-Tools Maliyeti (km)')
    plt.ylabel('Diğer Metotların Maliyeti (km)')
    plt.title('OR-Tools Referansına Göre Yakınsama Analizi')
    plt.legend()
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join("outputs", "karsilastirma_dagilim.png"), dpi=150)
