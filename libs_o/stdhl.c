#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<conio.h>

int read_mem(int* ptr) {
	return *ptr;
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

int* calloc_hl(int size) {
	return (int*)calloc(size,4);
}

char* to_string_hl(int val) {
	char* p = malloc(36);
	for(int i = 0;i < 37; i++) {
		p[i] = 0;
	}
	sprintf(p,"%d",val);
	return p;
}

int WinMain() {
	return 0;
}
