import subprocess
import json
import os
import psutil
import platform
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

class BenchmarkRunner:
    def __init__(self):
        self.input_sizes = [1000]
        self.thread_counts = [1, 2, 4, 8, 16]
        self.iterations = 5
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
    def compile_programs(self):
        # Compile C++ parallel
        subprocess.run([
            "g++", "-fopenmp", "-O3",
            "src/cpp/parallel/array_sum_parallel.cpp",
            "-o", "src/cpp/parallel/array_sum_parallel"
        ])
        
        # Compile C++ serial
        subprocess.run([
            "g++", "-O3",
            "src/cpp/serial/array_sum_serial.cpp",
            "-o", "src/cpp/serial/array_sum_serial"
        ])
        
        # Compile Fortran parallel
        subprocess.run([
            "gfortran", "-fopenmp", "-O3",
            "src/fortran/parallel/array_sum_parallel.f90",
            "-o", "src/fortran/parallel/array_sum_parallel"
        ])

    def run_benchmark(self):
        results = {
            "system_info": self.get_system_info(),
            "benchmarks": []
        }

        for size in self.input_sizes:
            for threads in self.thread_counts:
                # Run C++ parallel
                cpp_parallel_times = self.run_program(
                    "./src/cpp/parallel/array_sum_parallel",
                    size, threads, self.iterations
                )
                
                # Run C++ serial (only once per size)
                if threads == 1:
                    cpp_serial_times = self.run_program(
                        "./src/cpp/serial/array_sum_serial",
                        size, None, self.iterations
                    )
                
                # Run Fortran parallel
                fortran_parallel_times = self.run_program(
                    "./src/fortran/parallel/array_sum_parallel",
                    size, threads, self.iterations
                )
                
                results["benchmarks"].append({
                    "size": size,
                    "threads": threads,
                    "cpp_parallel": {
                        "mean": np.mean(cpp_parallel_times),
                        "std": np.std(cpp_parallel_times),
                        "times": cpp_parallel_times
                    },
                    "cpp_serial": {
                        "mean": np.mean(cpp_serial_times),
                        "std": np.std(cpp_serial_times),
                        "times": cpp_serial_times
                    } if threads == 1 else None,
                    "fortran_parallel": {
                        "mean": np.mean(fortran_parallel_times),
                        "std": np.std(fortran_parallel_times),
                        "times": fortran_parallel_times
                    }
                })
        
        self.save_results(results)
        self.generate_plots(results)

    def get_system_info(self):
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total
        }

    def run_program(self, executable, size, threads, iterations):
        times = []
        for _ in range(iterations):
            args = [executable, str(size)]
            if threads is not None:
                args.append(str(threads))
            
            result = subprocess.run(args, capture_output=True, text=True)
            _, time_taken = result.stdout.strip().split(",")
            times.append(float(time_taken))
        return times

    def save_results(self, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"results/json/benchmark_{timestamp}.json", "w") as f:
            json.dump(results, f, indent=2)

    def generate_plots(self, results):
        # Create plots directory
        plots_dir = Path("results/plots")
        plots_dir.mkdir(exist_ok=True)

        # Extract data for plotting
        sizes = []
        threads = []
        cpp_parallel_times = []
        cpp_serial_times = []
        fortran_parallel_times = []

        for benchmark in results["benchmarks"]:
            sizes.append(benchmark["size"])
            threads.append(benchmark["threads"])
            cpp_parallel_times.append(benchmark["cpp_parallel"]["mean"])
            if benchmark["cpp_serial"]:
                cpp_serial_times.append(benchmark["cpp_serial"]["mean"])
            fortran_parallel_times.append(benchmark["fortran_parallel"]["mean"])

        # Generate plots
        self.plot_scaling_by_size(sizes, threads, cpp_parallel_times,
                                cpp_serial_times, fortran_parallel_times)
        self.plot_speedup_by_threads(sizes, threads, cpp_parallel_times,
                                   cpp_serial_times, fortran_parallel_times)

if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.compile_programs()
    runner.run_benchmark() 