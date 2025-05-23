import json
import matplotlib.pyplot as plt
import numpy as np

def load_results(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

def extract_metrics(data):
    metrics = {"read": {"iops": [], "mean_latency_ns": [], "p99_9_latency_ns": []},
               "write": {"iops": [], "mean_latency_ns": [], "p99_9_latency_ns": []}}
    labels = []
    
    for entry in data:
        param_label = f"iodepth={entry['parameters']['iodepth']}, numjobs={entry['parameters']['numjobs']}, {entry['parameters']['Type']}"
        labels.append(param_label)
        
        for op in ["read", "write"]:
            metrics[op]["iops"].append(entry["metrics"][op]["iops"])
            metrics[op]["mean_latency_ns"].append(entry["metrics"][op]["mean_latency_ns"])
            metrics[op]["p99_9_latency_ns"].append(entry["metrics"][op]["p99_9_latency_ns"])
    
    return metrics, labels

def plot_metrics(metrics_dict, labels):
    categories = ["iops", "mean_latency_ns", "p99_9_latency_ns"]
    operations = ["read", "write"]
    
    x = np.arange(len(labels))
    width = 0.2  # Bar width
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for idx, (op, category) in enumerate([(op, cat) for op in operations for cat in categories]):
        ax = axes[idx]
        for i, (engine, metrics) in enumerate(metrics_dict.items()):
            ax.bar(x + i * width, metrics[op][category], width, label=engine)
        
        ax.set_title(f"{op.capitalize()} {category.replace('_', ' ')}")
        ax.set_xticks(x + width)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_ylabel(category)
        ax.legend()
    
    plt.tight_layout()
    plt.show()

def main():
    file_names = {"libaio": "libaio_results.json", "io_uring": "io_uring_results.json", "spdk": "spdk_results.json"}
    metrics_dict = {}
    labels = None
    
    for engine, file in file_names.items():
        data = load_results(file)
        metrics, labels = extract_metrics(data)
        metrics_dict[engine] = metrics
    
    plot_metrics(metrics_dict, labels)

if __name__ == "__main__":
    main()

