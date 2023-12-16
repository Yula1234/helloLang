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
	char* p = (char*)malloc(36);
	for(int i = 0;i < 37; i++) {
		p[i] = 0;
	}
	sprintf(p,"%d",val);
	return p;
}

char* concat_strings_hl(char* one, char* two) {
	int size = strlen(one) + strlen(two) + 12;
	char* p = (char*)malloc(size);
	for(int i = 0; i < size + 1; i++) {
		p[i] = 0;
	}
	sprintf(p,"%s%s",one,two);
	return p;
}

int string_to_number_hl(char* str) {
	return atoi(str);	
}

void file_write_hl(char* path, char* value) {
	FILE* f = fopen(path,"w");
	fputs(value, f);
	fclose(f);
}

char* file_read_hl(char* path) {
    FILE *fp = fopen(path, "r");

    char ch;
    char* buffer = (char*)malloc(1024);
    int c = 0;
    while ((ch = fgetc(fp)) != EOF) {
        buffer[c] = ch;
        c += 1;
    }
    buffer[c] = 0;

    fclose(fp);

    return buffer;
}

int WinMain() {
	return 0;
}
