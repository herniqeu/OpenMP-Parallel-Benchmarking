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
from tqdm import tqdm

class BenchmarkRunner:
    def __init__(self):
        self.input_sizes = [
            1000,          # 1K
            5000,          # 5K
            10000,         # 10K
            50000,         # 50K
            100000,        # 100K
            500000,        # 500K
            1000000,       # 1M
            5000000,       # 5M
            10000000,      # 10M
            50000000,      # 50M
            100000000      # 100M
        ]
        self.thread_counts = [1, 2, 4, 8, 16]
        self.iterations = 5
        self.results_dir = Path("results")
        self.json_dir = self.results_dir / "json"
        self.plots_dir = self.results_dir / "plots"
        
        self.results_dir.mkdir(exist_ok=True)
        self.json_dir.mkdir(exist_ok=True)
        self.plots_dir.mkdir(exist_ok=True)
        
    def compile_programs(self):
        print("Compiling programs...")
        try:
            compilation_steps = [
                ("C++ Parallel", [
                    "g++", "-fopenmp", "-O3",
                    "src/cpp/parallel/array_sum_parallel.cpp",
                    "-o", "src/cpp/parallel/array_sum_parallel"
                ]),
                ("C++ Serial", [
                    "g++", "-O3",
                    "src/cpp/serial/array_sum_serial.cpp",
                    "-o", "src/cpp/serial/array_sum_serial"
                ]),
                ("Fortran Parallel", [
                    "gfortran", "-fopenmp", "-O3",
                    "src/fortran/parallel/array_sum_parallel.f90",
                    "-o", "src/fortran/parallel/array_sum_parallel"
                ]),
                ("Fortran Serial", [
                    "gfortran", "-O3",
                    "src/fortran/serial/array_sum_serial.f90",
                    "-o", "src/fortran/serial/array_sum_serial"
                ])
            ]
            
            for name, command in tqdm(compilation_steps, desc="Compiling"):
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                
        except subprocess.CalledProcessError as e:
            print(f"Compilation error: {e.stderr}")
            raise

    def run_benchmark(self):
        results = {
            "system_info": self.get_system_info(),
            "benchmarks": []
        }

        total_runs = len(self.input_sizes) * len(self.thread_counts)
        print(f"\nTotal configurations to test: {total_runs}")
        print(f"Input sizes: {self.input_sizes}")
        print(f"Thread counts: {self.thread_counts}")
        print(f"Iterations per configuration: {self.iterations}\n")

        with tqdm(total=total_runs, desc="Running benchmarks") as pbar:
            for size in self.input_sizes:
                for threads in self.thread_counts:
                    pbar.set_description(f"Size: {size:,}, Threads: {threads}")
                    
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
                    
                    # Run Fortran serial
                    if threads == 1:
                        fortran_serial_times = self.run_program(
                            "./src/fortran/serial/array_sum_serial",
                            size, None, self.iterations
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
                        },
                        "fortran_serial": {
                            "mean": np.mean(fortran_serial_times),
                            "std": np.std(fortran_serial_times),
                            "times": fortran_serial_times
                        } if threads == 1 else None
                    })
                    pbar.update(1)
        
        self.save_results(results)
        self.generate_plots(results)

    def run_program(self, executable, size, threads, iterations):
        times = []
        for _ in range(iterations):
            try:
                args = [executable, str(size)]
                if threads is not None:
                    args.append(str(threads))
                
                result = subprocess.run(args, capture_output=True, text=True, check=True)
                _, time_taken = result.stdout.strip().split(",")
                times.append(float(time_taken))
                
            except subprocess.CalledProcessError as e:
                print(f"Error running {executable}: {e.stderr}")
                raise
            except ValueError as e:
                print(f"Error parsing output from {executable}: {e}")
                raise
                
        return times

    def get_system_info(self):
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total
        }

    def save_results(self, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/json/benchmark_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")

    def generate_plots(self, results):
        print("Generating plots...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare data structures for plotting
        data = {
            'size': [],
            'threads': [],
            'implementation': [],
            'time': []
        }
        
        # Extract data from results
        for benchmark in results['benchmarks']:
            size = benchmark['size']
            threads = benchmark['threads']
            
            # Add C++ parallel data
            data['size'].append(size)
            data['threads'].append(threads)
            data['implementation'].append('C++ Parallel')
            data['time'].append(benchmark['cpp_parallel']['mean'])
            
            # Add Fortran parallel data
            data['size'].append(size)
            data['threads'].append(threads)
            data['implementation'].append('Fortran Parallel')
            data['time'].append(benchmark['fortran_parallel']['mean'])
            
            # Add C++ serial data (only when threads == 1)
            if benchmark['cpp_serial']:
                data['size'].append(size)
                data['threads'].append(1)
                data['implementation'].append('C++ Serial')
                data['time'].append(benchmark['cpp_serial']['mean'])
            
            # Add Fortran serial data (only when threads == 1)
            if benchmark['fortran_serial']:
                data['size'].append(size)
                data['threads'].append(1)
                data['implementation'].append('Fortran Serial')
                data['time'].append(benchmark['fortran_serial']['mean'])
        
        # Create plots for each input size
        for size in self.input_sizes:
            plt.figure(figsize=(10, 6))
            
            # Filter data for current size
            size_data = {
                'threads': [t for i, t in enumerate(data['threads']) if data['size'][i] == size],
                'time': [t for i, t in enumerate(data['time']) if data['size'][i] == size],
                'implementation': [imp for i, imp in enumerate(data['implementation']) if data['size'][i] == size]
            }
            
            # Create line plot
            sns.lineplot(
                data=size_data,
                x='threads',
                y='time',
                hue='implementation',
                marker='o'
            )
            
            plt.title(f'Performance Comparison - Array Size: {size:,}')
            plt.xlabel('Number of Threads')
            plt.ylabel('Execution Time (seconds)')
            plt.xscale('log', base=2)
            plt.yscale('log')
            plt.grid(True)
            
            # Save plot
            plt.savefig(f'results/plots/benchmark_{timestamp}_size_{size}.png')
            plt.close()
        
        print(f"Plots saved in results/plots/")

if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.compile_programs()
    runner.run_benchmark() 