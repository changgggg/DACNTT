import time
import os
import psutil
import pandas as pd
import matplotlib.pyplot as plt
from ThreeP_Eclat import ThreePEclat
from ThreeP_Eclat_Pruning import ThreePEclatPruning

def run_experiment(algorithm_class, algorithm_name, base_output_dir, dataset_path, min_ps, period):
    print(f"\n--- Running {algorithm_name} on {os.path.basename(dataset_path)} (minPS={min_ps}, period={period}) ---")
    
    algo_output_dir = os.path.join(base_output_dir, algorithm_name)
    os.makedirs(algo_output_dir, exist_ok=True)
    
    stats_file = os.path.join(algo_output_dir, f"{os.path.splitext(os.path.basename(dataset_path))[0]}_stats_minPS_{str(min_ps).replace('.', '_')}_per_{str(period).replace('.', '_')}.txt")
    patterns_file = os.path.join(algo_output_dir, f"{os.path.splitext(os.path.basename(dataset_path))[0]}_patterns_minPS_{str(min_ps).replace('.', '_')}_per_{str(period).replace('.', '_')}.txt")

    miner = algorithm_class(minPS=min_ps, period=period)
    start_time = time.time()
    
    stats, (num_patterns, exec_time, mem_uss, mem_rss) = miner.startMine(dataset_path, stats_file, patterns_file)
    end_time = time.time()
    total_exec_time = end_time - start_time
    
    print(f"   Số lượng mẫu tìm được: {num_patterns}")
    print(f"   Thời gian thực thi (tổng): {total_exec_time:.4f} giây")
    print(f"   Thời gian thực thi (trong mine): {exec_time:.4f} giây")
    print(f"   Bộ nhớ sử dụng (USS): {mem_uss:.2f} MB")
    print(f"   Bộ nhớ sử dụng (RSS): {mem_rss:.2f} MB")

    with open(stats_file, "w", encoding="utf-8") as f:
        f.write(stats)
    print(f"   Đã lưu thống kê vào file: {stats_file}")

    return {
        'algorithm': algorithm_name,
        'dataset': os.path.basename(dataset_path),
        'minPS': min_ps,
        'period': period,
        'num_patterns': num_patterns,
        'execution_time': total_exec_time,
        'memory_uss': mem_uss,
        'memory_rss': mem_rss
    }

def plot_results(df, dataset_name, y, x, x_ticks, y_label, x_label, output_filename, title_prefix=""):
    plt.figure(figsize=(10, 6))

    color_map = {
        '3P-ECLAT': 'C1',
        '3P-ECLAT Pruning': 'red'
    }

    for algorithm in df['algorithm'].unique():
        subset = df[(df['dataset'] == dataset_name) & (df['algorithm'] == algorithm)]
        subset = subset.sort_values(by=x)
        plt.plot(subset[x] * 1000, subset[y], marker='o', label=algorithm, color=color_map.get(algorithm))

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f'{title_prefix}{y} vs. {x} on {dataset_name}')
    plt.xticks(x_ticks)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(output_filename)
    plt.close()
    print(f"Đã lưu biểu đồ vào: {output_filename}")

if __name__ == '__main__':
    os.makedirs("output", exist_ok=True)
    os.makedirs("output1", exist_ok=True)
    database_dir = "database"
    results = []

    all_datasets = [
        {'id': 1, 'name': 'Temporal_T10I4D100K.csv', 'minPS_fixed': 0.008, 'period_fixed': 0.001},
        {'id': 2, 'name': 'Temporal_T20I6D100K.csv', 'minPS_fixed': 0.0034, 'period_fixed': 0.006},
        {'id': 3, 'name': 'Transactional_connect.csv', 'minPS_fixed': 0.0002, 'period_fixed': 0.01},
        {'id': 4, 'name': 'Transactional_retail.csv', 'minPS_fixed': 0.0015, 'period_fixed': 0.0045}
    ]

    algorithms = [
        {'name': '3P-ECLAT', 'class': ThreePEclat},
        {'name': '3P-ECLAT Pruning', 'class': ThreePEclatPruning}
    ]

    print("Chọn chế độ thử nghiệm:")
    print("1. Giữ minPS cố định, thay đổi Period")
    print("2. Giữ Period cố định, thay đổi minPS")

    while True:
        mode_choice = input("Nhập lựa chọn của bạn (1 hoặc 2): ")
        if mode_choice in ['1', '2']:
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng nhập '1' hoặc '2'.")

    print("\nChọn bộ dữ liệu để chạy thử nghiệm:")
    for ds in all_datasets:
        print(f"{ds['id']}. {ds['name']}")

    while True:
        dataset_choice_id = input("Nhập số của bộ dữ liệu bạn muốn chọn: ")
        try:
            dataset_choice_id = int(dataset_choice_id)
            selected_dataset_info = next((ds for ds in all_datasets if ds['id'] == dataset_choice_id), None)
            if selected_dataset_info:
                break
            else:
                print("Lựa chọn bộ dữ liệu không hợp lệ. Vui lòng nhập lại.")
        except ValueError:
            print("Đầu vào không hợp lệ. Vui lòng nhập một số.")

    dataset_path = os.path.join(database_dir, selected_dataset_info['name'])
    dataset_name_without_ext = os.path.splitext(selected_dataset_info['name'])[0]

    if not os.path.exists(dataset_path):
        print(f"Không tìm thấy dataset: {dataset_path}")
    else:
        if mode_choice == '1':
            current_min_ps = selected_dataset_info['minPS_fixed']
            periods_to_test = [0.001, 0.005, 0.007, 0.01, 0.05, 0.07]
            base_output_for_mode = f"output_{dataset_name_without_ext}_minPS_fixed"
            os.makedirs(base_output_for_mode, exist_ok=True)

            print(f"\n--- Chạy thử nghiệm với minPS cố định ({current_min_ps}) và thay đổi Period ---")
            for period in periods_to_test:
                for algo_info in algorithms:
                    result = run_experiment(algo_info['class'], algo_info['name'], base_output_for_mode, dataset_path, current_min_ps, period)
                    results.append(result)

            df_results = pd.DataFrame(results)
            output_csv_file = os.path.join(base_output_for_mode, f"comparison_results_minPS_fixed_{dataset_name_without_ext}.csv")
            df_results.to_csv(output_csv_file, index=False)

            x_ticks = [p * 1000 for p in periods_to_test]
            plot_results(df_results, selected_dataset_info['name'], 'execution_time', 'period', x_ticks, "Runtime (second)", "per ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_runtime_vs_per.png"), 
                         title_prefix="Runtime ")
            plot_results(df_results, selected_dataset_info['name'], 'num_patterns', 'period', x_ticks, "Number of patterns", "per ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_patterns_vs_per.png"), 
                         title_prefix="Number of Patterns ")
            plot_results(df_results, selected_dataset_info['name'], 'memory_uss', 'period', x_ticks, "Memory USS (MB)", "per ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_memory_uss_vs_per.png"), 
                         title_prefix="Memory USS ")
            plot_results(df_results, selected_dataset_info['name'], 'memory_rss', 'period', x_ticks, "Memory RSS (MB)", "per ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_memory_rss_vs_per.png"), 
                         title_prefix="Memory RSS ")

        elif mode_choice == '2':
            current_period = selected_dataset_info['period_fixed']
            min_ps_to_test = [0.001, 0.005, 0.007, 0.01, 0.05, 0.07]
            base_output_for_mode = f"output_{dataset_name_without_ext}_period_fixed"
            os.makedirs(base_output_for_mode, exist_ok=True)

            print(f"\n--- Chạy thử nghiệm với Period cố định ({current_period}) và thay đổi minPS ---")
            for min_ps in min_ps_to_test:
                for algo_info in algorithms:
                    result = run_experiment(algo_info['class'], algo_info['name'], base_output_for_mode, dataset_path, min_ps, current_period)
                    results.append(result)

            df_results = pd.DataFrame(results)
            output_csv_file = os.path.join(base_output_for_mode, f"comparison_results_period_fixed_{dataset_name_without_ext}.csv")
            df_results.to_csv(output_csv_file, index=False)

            x_ticks = [p * 1000 for p in min_ps_to_test]
            plot_results(df_results, selected_dataset_info['name'], 'execution_time', 'minPS', x_ticks, "Runtime (second)", "minPS ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_runtime_vs_minPS.png"), 
                         title_prefix="Runtime ")
            plot_results(df_results, selected_dataset_info['name'], 'num_patterns', 'minPS', x_ticks, "Number of patterns", "minPS ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_patterns_vs_minPS.png"), 
                         title_prefix="Number of Patterns ")
            plot_results(df_results, selected_dataset_info['name'], 'memory_uss', 'minPS', x_ticks, "Memory USS (MB)", "minPS ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_memory_uss_vs_minPS.png"), 
                         title_prefix="Memory USS ")
            plot_results(df_results, selected_dataset_info['name'], 'memory_rss', 'minPS', x_ticks, "Memory RSS (MB)", "minPS ($\\times 10^{-3}$)",
                         os.path.join(base_output_for_mode, f"{dataset_name_without_ext}_memory_rss_vs_minPS.png"), 
                         title_prefix="Memory RSS ")
