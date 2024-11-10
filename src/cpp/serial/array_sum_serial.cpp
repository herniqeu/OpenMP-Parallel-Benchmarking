#include <iostream>
#include <vector>
#include <random>
#include <chrono>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <array_size>" << std::endl;
        return 1;
    }

    size_t size = std::stoull(argv[1]);
    
    // Generate random numbers
    std::vector<int> numbers(size);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 100);
    
    for (size_t i = 0; i < size; ++i) {
        numbers[i] = dis(gen);
    }
    
    long long sum = 0;
    auto start_time = std::chrono::high_resolution_clock::now();
    
    for (size_t i = 0; i < size; ++i) {
        sum += numbers[i];
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::duration<double>>(
        end_time - start_time);
    
    std::cout << sum << "," << duration.count() << std::endl;
    return 0;
} 