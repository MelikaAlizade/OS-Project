import subprocess
import json

def run_fio(iodepth, numjobs, test_type, size):
    cmd = [
        "sudo", "fio", "--name=test", "--filename=/dev/nvme1n1", "--direct=1",
        "--rw={}".format(test_type), "--bs=4k", "--iodepth={}".format(iodepth),
        "--numjobs={}".format(numjobs), "--size={}".format(size),
        "--ioengine=libaio", "--group_reporting", "--norandommap=1", "--output-format=json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running fio:", e)
        return None

def extract_metrics(fio_output):
    if not fio_output:
        return None
    
    jobs = fio_output.get("jobs", [])
    if not jobs:
        return None
    
    read_stats = jobs[0].get("read", {})
    write_stats = jobs[0].get("write", {})
    
    return {
        "read": {
            "iops": read_stats.get("iops", 0),
            "mean_latency_ns": read_stats.get("lat_ns", {}).get("mean", 0),
            "p99_9_latency_ns": read_stats.get("clat_ns", {}).get("percentile", {}).get("99.900000", 0),
        },
        "write": {
            "iops": write_stats.get("iops", 0),
            "mean_latency_ns": write_stats.get("lat_ns", {}).get("mean", 0),
            "p99_9_latency_ns": write_stats.get("clat_ns", {}).get("percentile", {}).get("99.900000", 0),
        }
    }

def main():
    parameters = [
        {"iodepth": 1, "numjobs": 1, "Type": "randrw", "size": "4G"},
        {"iodepth": 1, "numjobs": 4, "Type": "randrw", "size": "1G"},
        {"iodepth": 1, "numjobs": 1, "Type": "randwrite", "size": "4G"},
        {"iodepth": 1, "numjobs": 4, "Type": "randwrite", "size": "1G"},
        {"iodepth": 1, "numjobs": 1, "Type": "randread", "size": "4G"},
        {"iodepth": 1, "numjobs": 4, "Type": "randread", "size": "1G"},
    ]
    
    results = []
    
    for param in parameters:
        print(f"Running test: {param}")
        fio_output = run_fio(param["iodepth"], param["numjobs"], param["Type"], param["size"])
        metrics = extract_metrics(fio_output)
        if metrics:
            results.append({"parameters": param, "metrics": metrics})
        else:
            results.append({"parameters": param, "metrics": "Failed to extract metrics."})
    
    with open("libaio_results.json", "w") as f:
        json.dump(results, f, indent=4)
    
if __name__ == "__main__":
    main()
