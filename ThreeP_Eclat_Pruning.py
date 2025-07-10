import pandas as pd
import time
import psutil
import os
from urllib.request import urlopen as _urlopen
import validators as _validators
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import array

class ThreePEclatPruning:
    def __init__(self, minPS, period, sep='\t'):
        self._minPS = minPS
        self._period = period
        self._sep = sep
        self._Database = []
        self._finalPatterns = {}
        self._startTime = 0
        self._endTime = 0
        self._memoryUSS = 0
        self._memoryRSS = 0
        self._tidList = {}
        self._lno = 0
        self._item_frequencies = {}
        self._transaction_lengths = []
        self._timestamps = []
        self._current_file = None

    def _convert_support_period(self, value):
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(len(self._Database) * value)
        if isinstance(value, str):
            try:
                if '.' in value:
                    return int(len(self._Database) * float(value))
                else:
                    return int(value)
            except ValueError:
                raise ValueError(f"Không thể chuyển đổi giá trị: {value}")
        return value

    def _creatingItemSets(self, iFile):
        self._Database = []
        self._lno = 0
        all_items = []
        self._transaction_lengths = []
        self._timestamps = []

        if isinstance(iFile, pd.DataFrame):
            data, tids = [], []
            if iFile.empty:
                print(f"DataFrame đầu vào rỗng.")
                return
            cols = iFile.columns.values.tolist()
            if 'TS' in cols:
                tids = iFile['TS'].tolist()
            if 'Transactions' in cols:
                data = iFile['Transactions'].tolist()
            for i in range(len(data)):
                transaction = data[i]
                tr = [tids[i]] + transaction
                self._Database.append(tr)
                all_items.extend(transaction)
                self._transaction_lengths.append(len(transaction))
                self._timestamps.append(tids[i])
            self._lno = len(self._Database)
        elif isinstance(iFile, str):
            def process_line(line):
                line = line.strip()
                temp = [i.strip() for i in line.split(self._sep) if i.strip()]
                if temp:
                    timestamp_str = temp[0]
                    items = temp[1:]
                    try:
                        timestamp = int(timestamp_str)
                        transaction = [timestamp] + items
                        self._Database.append(transaction)
                        all_items.extend(items)
                        self._transaction_lengths.append(len(items))
                        self._timestamps.append(timestamp)
                    except ValueError:
                        print(f"Cảnh báo: Không thể chuyển đổi timestamp '{timestamp_str}' thành số trong dòng: {line}")

            if _validators.url(iFile):
                try:
                    with _urlopen(iFile) as f:
                        for line_bytes in f:
                            line = line_bytes.decode("utf-8")
                            self._lno += 1
                            process_line(line)
                except Exception as e:
                    print(f"Lỗi khi đọc dữ liệu từ URL: {e}")
                    quit()
            else:
                try:
                    with open(iFile, 'r', encoding='utf-8') as f:
                        for line in f:
                            self._lno += 1
                            process_line(line)
                except IOError:
                    print(f"Không tìm thấy file: {iFile}")
                    quit()
        else:
            raise ValueError("Định dạng đầu vào không được hỗ trợ.")

        self._item_frequencies = Counter(all_items)
        print(f"Đã đọc {self._lno} giao dịch từ nguồn.")

    def _calculate_database_stats(self, output_file, num_patterns, execution_time, memory_uss, memory_rss):
        num_transactions = len(self._Database)
        num_items = len(self._item_frequencies)
        min_transaction_size = min(self._transaction_lengths) if self._transaction_lengths else 0
        max_transaction_size = max(self._transaction_lengths) if self._transaction_lengths else 0
        avg_transaction_size = np.mean(self._transaction_lengths) if self._transaction_lengths else 0
        std_dev_transaction_size = np.std(self._transaction_lengths) if self._transaction_lengths else 0
        variance_transaction_size = np.var(self._transaction_lengths) if self._transaction_lengths else 0

        min_period = self._period
        max_period = self._period
        avg_period = self._period

        total_item_occurrences = sum(self._item_frequencies.values())
        sparsity = 1 - (total_item_occurrences / (num_transactions * num_items)) if num_transactions * num_items > 0 else 0

        output = f"--- Thống kê Cơ Sở Dữ Liệu ---\n"
        output += f"Database file : {os.path.basename(self._current_file)}\n"
        output += f"Database size : {num_transactions}\n"
        output += f"Number of items : {num_items}\n"
        output += f"Minimum Transaction Size : {min_transaction_size}\n"
        output += f"Average Transaction Size : {avg_transaction_size:.10f}\n"
        output += f"Maximum Transaction Size : {max_transaction_size}\n"
        output += f"Minimum period : {min_period}\n"
        output += f"Average period : {avg_period:.1f}\n"
        output += f"Maximum period : {max_period}\n"
        output += f"Standard Deviation Transaction Size : {std_dev_transaction_size:.10f}\n"
        output += f"Variance : {variance_transaction_size:.10f}\n"
        output += f"Sparsity : {sparsity:.10f}\n"
        output += "\n"
        output += "--- Thống kê Khai Thác Mẫu ---\n"
        output += f"Số lượng mẫu tìm được: {num_patterns}\n"
        output += f"Thời gian thực thi: {execution_time:.4f} giây\n"
        output += f"Bộ nhớ sử dụng (USS): {memory_uss:.2f} MB\n"
        output += f"Bộ nhớ sử dụng (RSS): {memory_rss:.2f} MB\n"
        output += "-----------------------------\n"
        return output

    def _plot_database_stats(self):
        if not self._Database:
            print("Không có dữ liệu để vẽ biểu đồ.")
            return

        output_dir = "output"
        file_name = os.path.basename(self._current_file)
        plot_file_prefix = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_stats_plot")

        plt.figure(figsize=(15, 10))

        # Biểu đồ tần suất item phổ biến
        top_n = 20
        most_common_items = self._item_frequencies.most_common(top_n)
        item_names = [item[0] for item in most_common_items]
        frequencies = [item[1] for item in most_common_items]

        plt.subplot(2, 2, 1)
        plt.bar(item_names, frequencies)
        plt.xlabel('Item')
        plt.ylabel('Tần suất')
        plt.title(f'Top {top_n} Item Phổ Biến Nhất')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Biểu đồ phân phối độ dài giao dịch
        plt.subplot(2, 2, 2)
        plt.hist(self._transaction_lengths, bins=20, edgecolor='black')
        plt.xlabel('Độ dài giao dịch')
        plt.ylabel('Số lượng giao dịch')
        plt.title('Phân Phối Độ Dài Giao Dịch')
        plt.tight_layout()

        # Biểu đồ đường tần suất theo số lượng item
        item_value_counts = Counter(self._item_frequencies.values())
        sorted_item_counts = sorted(item_value_counts.items())
        frequencies = [count for count, freq in sorted_item_counts]
        no_of_items = [freq for count, freq in sorted_item_counts]

        plt.subplot(2, 2, 3)
        plt.plot(no_of_items, frequencies, marker='o', linestyle='-')
        plt.xlabel('Số lượng item')
        plt.ylabel('Tần suất')
        plt.title('Tần Suất theo Số Lượng Item')
        plt.grid(True)
        plt.tight_layout()

        # Biểu đồ đường tần suất theo độ dài giao dịch
        transaction_length_counts = Counter(self._transaction_lengths)
        sorted_transaction_lengths = sorted(transaction_length_counts.items())
        transaction_lengths = [length for length, freq in sorted_transaction_lengths]
        frequencies = [freq for length, freq in sorted_transaction_lengths]

        plt.subplot(2, 2, 4)
        plt.plot(transaction_lengths, frequencies, marker='o', linestyle='-')
        plt.xlabel('Độ dài giao dịch')
        plt.ylabel('Tần suất')
        plt.title('Tần Suất theo Độ Dài Giao Dịch')
        plt.grid(True)
        plt.tight_layout()

        plot_file_name = f"{plot_file_prefix}.png"
        plt.savefig(plot_file_name)
        plt.close()
        print(f"Đã lưu biểu đồ thống kê vào file: {plot_file_name}")

    def _plot_periodic_patterns(self, patterns, output_path):
        if not patterns:
            print("Không có mẫu tuần hoàn nào để vẽ biểu đồ.")
            return

        pattern_lengths = [len(pattern) for pattern in patterns.keys()]
        supports = list(patterns.values())

        plt.figure(figsize=(10, 6))
        plt.plot(pattern_lengths, supports, marker='o', linestyle='-')
        plt.xlabel('Độ dài mẫu tuần hoàn')
        plt.ylabel('Periodic Support')
        plt.title('Biểu đồ Periodic Support theo Độ dài Mẫu')
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(output_path)
        plt.close()
        print(f"Đã lưu biểu đồ mẫu tuần hoàn vào file: {output_path}")

    def _creatingOneitemSets(self):
        tid_lists = {}
        _mapSupport = {}
        period = self._convert_support_period(self._period)
        for line in self._Database:
            if not line:
                continue
            try:
                n = int(line[0])
                for i in range(1, len(line)):
                    si = line[i]
                    if si not in _mapSupport:
                        _mapSupport[si] = [0, n]
                        tid_lists[si] = [n]
                    else:
                        lp = n - _mapSupport[si][1]
                        if lp <= period:
                            _mapSupport[si][0] += 1
                        _mapSupport[si][1] = n
                        tid_lists[si].append(n)
            except ValueError:
                print(f"Cảnh báo: Lỗi định dạng timestamp trong giao dịch: {line}")
                continue

        minPS = self._convert_support_period(self._minPS)
        self._tidList = {k: np.array(v, dtype=np.int32) for k, v in tid_lists.items() if _mapSupport[k][0] >= minPS}
        plist = sorted(self._tidList.keys(), key=lambda k: _mapSupport[k][0], reverse=True)
        return plist

    def getPeriodicSupport(self, timeStamps):
        if len(timeStamps) < 2:
            return 0
        timeStamps_sorted = np.sort(timeStamps)
        diffs = np.diff(timeStamps_sorted)
        return np.sum(diffs <= self._convert_support_period(self._period))

    def _save(self, prefix, suffix, tidSetX):
        if prefix is None:
            pattern = tuple(suffix)
        else:
            pattern = tuple(sorted(prefix + suffix))

        val = self.getPeriodicSupport(tidSetX)
        if val >= self._convert_support_period(self._minPS):
            self._finalPatterns[pattern] = val

    def _generation(self, prefix, itemSets, tidSets):
        num_items = len(itemSets)
        for i in range(num_items):
            itemI = itemSets[i]
            if itemI is None:
                continue
            tidSetX = tidSets[i]
            itemSetX = [itemI]
            classItemSets = []
            classTidSets = []
            for j in range(i + 1, num_items):
                itemJ = itemSets[j]
                tidSetJ = tidSets[j]
                common_tids = np.intersect1d(tidSetX, tidSetJ)
                val = self.getPeriodicSupport(common_tids)
                if val >= self._convert_support_period(self._minPS):
                    classItemSets.append(itemJ)
                    classTidSets.append(common_tids)

            newprefix = sorted(prefix + itemSetX)
            if classItemSets:
                self._generation(newprefix, classItemSets, classTidSets)

            actual_support = self.getPeriodicSupport(tidSetX)
            if actual_support >= self._convert_support_period(self._minPS):
                self._save(prefix, itemSetX, tidSetX)

    def startMine(self, iFile, stats_output_file, patterns_output_file):
        self._current_file = iFile
        self._finalPatterns = {}
        self._startTime = time.time()
        self._creatingItemSets(iFile)
        num_patterns, exec_time, mem_uss, mem_rss = self._mine_patterns(iFile, patterns_output_file)
        database_stats = self._calculate_database_stats(stats_output_file, num_patterns, exec_time, mem_uss, mem_rss)
        self._plot_database_stats() # Lưu biểu đồ thống kê vào file
        return database_stats, (num_patterns, exec_time, mem_uss, mem_rss)

    def _mine_patterns(self, iFile, patterns_output_file):
        self._finalPatterns = {}
        start_time_mine = time.time()
        plist = self._creatingOneitemSets()
        initial_itemSets = []
        initial_tidSets = []
        print("--- Creating initial itemsets ---")
        for itemI in plist:
            tidSetX = self._tidList[itemI]
            actual_support = self.getPeriodicSupport(tidSetX)
            if actual_support >= self._convert_support_period(self._minPS):
                initial_itemSets.append(itemI)
                initial_tidSets.append(tidSetX)
                self._save(None, [itemI], tidSetX)
                print(f"  Initial frequent item: {itemI}, support: {actual_support}, TID count: {len(tidSetX)}")

        print("--- Starting generation ---")
        self._generation([], initial_itemSets, initial_tidSets)

        end_time_mine = time.time()
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_uss_mine = getattr(memory_info, 'uss', memory_info.rss)
        memory_rss_mine = memory_info.rss

        # Gán lại vào self để sử dụng ở nơi khác
        self._memoryUSS = memory_uss_mine / (1024 * 1024)
        self._memoryRSS = memory_rss_mine / (1024 * 1024)

        num_patterns_found = len(self._finalPatterns)
        execution_time_mine = end_time_mine - start_time_mine

        with open(patterns_output_file, "w", encoding="utf-8") as f:
            f.write(f"--- Mẫu Tuần Hoàn Cục Bộ từ {os.path.basename(iFile)} ---\n")
            for pattern, support in self._finalPatterns.items():
                f.write(f"{pattern}: {support}\n")
            f.write("-------------------------------------------------------\n")
        print(f"Đã ghi nhận {num_patterns_found} mẫu tuần hoàn vào file: {patterns_output_file}")

        output_dir = "output1"
        file_name = os.path.basename(iFile)
        patterns_plot_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_patterns_plot.png")
        self._plot_periodic_patterns(self._finalPatterns, patterns_plot_file)

        return num_patterns_found, execution_time_mine, self._memoryUSS, self._memoryRSS

