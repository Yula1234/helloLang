#include<iostream>
#include<vector>

using namespace std;

vector<int>* init_list_hl() {
	vector<int>* p = new vector<int>();
	return p;
}

void add_list_hl(vector<int>* p, int value) {
	p->push_back(value);
}

int get_list_hl(vector<int>* p, int index) {
	return p->operator[](index);
}

int WinMain() {
	return 0;
}
