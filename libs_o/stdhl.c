#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int read_ptr(int* ptr) {
	return *ptr;
}

void write_ptr(int* ptr, int val) {
	*ptr = val;
}

int strlen_hl(char* ptr) {
	return strlen(ptr);
}

int strcmp_hl(char* one, char* two) {
	return strcmp(one, two);
}

int fib_hl(int n) {
	if(n <= 1) {
		return n;
	}
	return fib_hl(n-1) + fib_hl(n-2);
}

int WinMain() {
	return 0;
}
