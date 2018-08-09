#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>

// Using C++11
// Compile with >g++ -std=c++11 -O3 stationary.cpp

int main(int argc, char* argv[])
{
    int iterations = std::stoi(argv[2]);
    bool verbose = true;
    int N;
    int n;
    // n(n-1) + 1 = n*n -n + 1 < n*n

    // Read in the values
    std::string input_filename(argv[1]);
    std::ifstream input_file (input_filename, std::ifstream::in);
    if (!input_file.is_open())
    {
        std::cout << "Unable to open file\n";
        return 0;
    }

    // First line contains the total number of states.
    std::string line;
    std::getline(input_file, line);
    N = std::stoi(line);
    // Second line contains the number of types n.
    std::getline(input_file, line);
    n = std::stoi(line);
    if (verbose) {
        std::cout << N << std::endl << n << std::endl;
    }

    // Load transitions and cache neighbors
    std::vector< std::map<int, double> > transitions(N);
    // Subsequent lines are of the form int,int,float
    std::string source;
    std::string target;
    std::string weight;
    std::vector< std::vector<int> > in_neighbors(N);

    while (std::getline(input_file,line))
    {
        std::stringstream splitstream(line);
        getline(splitstream, source, ',');
        getline(splitstream, target, ',');
        getline(splitstream, weight, '\n');
        int i = std::stoi(source);
        int j = std::stoi(target);
        double w = std::stod(weight);
        transitions[i][j] = w;
        in_neighbors[j].push_back(i);
    }

    // Initialize vectors
    std::vector<double> s(N);
    std::vector<double> t(N, 0);
    for (int i=0; i < N; i++)
    {
        s[i] = double(1.0) / double(N);
    }

    // Iterate sparse multiplication of the transition matrix
    // This converges to the stationary distribution
    int in_index;
    for (int k=0; k < iterations; k++)
    {
        if (verbose) {
            std::cout << k << std::endl;
        }
        t.clear();
        t.resize(N, 0);
        for (int i = 0; i < N; i++)
        {
            for ( int j = 0; j < in_neighbors[i].size(); j++)
            {
                in_index = in_neighbors[i][j];
                t[i] += transitions[in_index][i] * s[in_index];
            }
        }
        s = t;
    }

    // Output stationary distribution to a text file
    std::string output_filename("enumerated_stationary.txt");
    std::ofstream output_file (output_filename, std::ofstream::out);
    for (int i=0; i < N; i++)
    {
        output_file << i << ',' << s[i] << std::endl;
    }

    return 0;
}
