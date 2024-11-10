#include <iostream>
#include <vector>
#include <random>
#include <omp.h>

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <array_size> <num_threads>" << std::endl;
        return 1;
    }

    size_t size = std::stoull(argv[1]);
    int num_threads = std::stoi(argv[2]);
    
    // Generate random numbers
    std::vector<int> numbers(size);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 100);
    
    for (size_t i = 0; i < size; ++i) {
        numbers[i] = dis(gen);
    }
    
    long long sum = 0;
    double start_time = omp_get_wtime();
    
    #pragma omp parallel num_threads(num_threads) reduction(+:sum)
    {
        #pragma omp for
        for (size_t i = 0; i < size; ++i) {
            sum += numbers[i];
        }
    }
    
    double end_time = omp_get_wtime();
    
    std::cout << sum << "," << (end_time - start_time) << std::endl;
    return 0;
} 