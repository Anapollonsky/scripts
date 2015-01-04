#include <iostream>
#include <cmath>
#include <vector>
#include <sstream>
#include <string>
#include <stdio.h>

using namespace std;

bool isprime(int num, vector<int> primes){
    for (int i: primes){
	if (num % i == 0){
	    return false;
	}
    }
    return true;
}

vector<int> genprimes(int maxnum){
    vector<int> primes_list;
    for(int i = 2; i < maxnum; i++){
	if (isprime(i, primes_list)){
	    primes_list.push_back(i);
	}
    }
    return primes_list;
}


template<typename T>
void printlist(T thelist){
    for (int i = 0; i < thelist.size(); i++){
	cout << thelist[i] << " ";
    }
    cout << endl;
}


int main(void) {
    vector<int> primes = genprimes(10000);
    vector<string> vec {"hey", "they"};
    printlist(primes);
}
