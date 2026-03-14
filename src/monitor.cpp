#include <iostream>
#include <fstream>
#include <string>
#include <unistd.h>

extern "C" {
    float get_memory_usage() {
        long pages = sysconf(_SC_PHYS_PAGES);
        long page_size = sysconf(_SC_PAGE_SIZE);
        long total_memory = pages * page_size;

        std::ifstream file("/proc/meminfo");
        std::string line;
        long free_memory = 0;
        if (file.is_open()) {
            while (std::getline(file, line)) {
                if (line.find("MemAvailable:") == 0) {
                    sscanf(line.c_str(), "MemAvailable: %ld kB", &free_memory);
                    break;
                }
            }
            file.close();
        }

        // Convert free_memory from kB to bytes
        long free_bytes = free_memory * 1024;
        float available_gb = (float)free_bytes / (1024 * 1024 * 1024);
        return available_gb;
    }

    float get_total_memory() {
        long pages = sysconf(_SC_PHYS_PAGES);
        long page_size = sysconf(_SC_PAGE_SIZE);
        long total_memory = pages * page_size;
        return (float)total_memory / (1024 * 1024 * 1024);
    }
}
