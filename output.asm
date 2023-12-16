section .text

global main

extern printf
extern scanf
extern malloc
extern free
extern ExitProcess@4
extern calloc_hl
extern write_mem
extern read_mem

nullptr:
	; ptr nullptr()
	push ebp
	mov ebp, esp
	sub esp, 8
	push 0
	pop eax
	add esp, 8
	pop ebp
	ret

exit:
	; void exit(int code)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	call ExitProcess@4
	add esp, 4
	xor eax, eax
	add esp, 16
	pop ebp
	ret

print:
	; void print(int num)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	push dword numfmt
	call printf
	add esp, 8
	xor eax, eax
	add esp, 16
	pop ebp
	ret

println:
	; void println(int num)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	push dword numfmt
	call printf
	add esp, 8
	push newline
	call printf
	add esp, 4
	xor eax, eax
	add esp, 16
	pop ebp
	ret

prints:
	; void prints(string str)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	call printf
	add esp, 4
	xor eax, eax
	add esp, 16
	pop ebp
	ret

printfmt:
	; void printfmt(string fmt,int num)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], edx
	push dword [ebp-12]
	push dword [ebp-8]
	call printf
	add esp, 8
	xor eax, eax
	add esp, 24
	pop ebp
	ret

prints_p:
	; void prints_p(ptr str)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	push strfmt
	call printf
	add esp, 8
	xor eax, eax
	add esp, 16
	pop ebp
	ret

input_number:
	; void input_number(ptr p)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	push numfmt
	call scanf
	add esp, 8
	xor eax, eax
	add esp, 16
	pop ebp
	ret

input_str:
	; void input_str(ptr p)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	push strfmt
	call scanf
	add esp, 8
	mov edx, [ebp-8]
	xor eax, eax
	add esp, 16
	pop ebp
	ret

alloc:
	; ptr alloc(int size)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	call nullptr
	push eax
	pop eax
	mov dword [ebp-12], eax
	push dword [ebp-8]
	call malloc
	add esp, 4
	mov [ebp-12], eax
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret

dealloc:
	; void dealloc(ptr p)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	call free
	add esp, 4
	xor eax, eax
	add esp, 16
	pop ebp
	ret

throw:
	; void throw(ptr str,int excode)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], edx
	mov edx, [ebp-8]
	push dword [edx]
	call printf
	add esp, 4
	push dword newline
	call printf
	add esp, 4
	push dword [ebp-12]
	call ExitProcess@4
	add esp, 4
	xor eax, eax
	add esp, 24
	pop ebp
	ret

calloc:
	; ptr calloc(int size)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	push 0
	pop eax
	mov dword [ebp-12], eax
	push dword [ebp-8]
	call calloc_hl
	add esp, 4
	mov dword [ebp-12], eax
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret

__write:
	; void __write(ptr p,int val)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], edx
	mov esi, dword [ebp-8]
	mov edx, dword [ebp-12]
	mov dword [esi], edx
	xor eax, eax
	add esp, 24
	pop ebp
	ret

__read:
	; int __read(ptr p)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], dword 0
	push dword [ebp-8]
	call read_mem
	add esp, 4
	mov dword [ebp-12], eax
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret
extern strlen_hl
extern strcmp_hl
extern to_string_hl
extern concat_strings_hl
extern string_to_number_hl

strlen:
	; int strlen(ptr p)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], dword 0
	push dword [ebp-12]
	call strlen_hl
	add esp, 4
	mov dword [ebp-16], eax
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret

strcmp:
	; int strcmp(ptr one,ptr two)
	push ebp
	mov ebp, esp
	sub esp, 32
	mov dword [ebp-8], ecx
	mov dword [ebp-12], edx
	mov dword [ebp-16], dword 0
	push dword [ebp-8]
	push dword [ebp-12]
	call strcmp_hl
	mov dword [ebp-16], eax
	add esp, 8
	push dword [ebp-16]
	mov ebx, 0
	pop eax
	cmp eax, ebx
	je L0
	jne L1
	L0:
	push 1
	jmp L2
	L1:
	push 0
	L2:
	pop eax
	cmp eax, 0
	je ELSE4
	IF3:
	mov eax, 1
	add esp, 32
	pop ebp
	ret
	jmp END5
	ELSE4:
	xor eax, eax
	add esp, 32
	pop ebp
	ret
	jmp END5
	END5:
	push dword [ebp-16]
	pop eax
	add esp, 32
	pop ebp
	ret

str_init:
	; ptr str_init(int size)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	push dword [ebp-8]
	mov ebx, 1
	pop eax
	add eax, ebx
	push eax
	pop ecx
	call alloc
	push eax
	pop eax
	mov dword [ebp-12], eax
	mov edx, dword [ebp-12]
	mov ebx, dword [ebp-8]
	add edx, ebx
	add edx, 1
	
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret

str_del:
	; void str_del(ptr str)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov dword [ebp-8], ecx
	mov ecx, dword [ebp-8]
	call dealloc
	xor eax, eax
	add esp, 16
	pop ebp
	ret

to_str:
	; ptr to_str(int val)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	push 0
	pop eax
	mov dword [ebp-12], eax
	push dword [ebp-8]
	call to_string_hl
	add esp, 4
	mov dword [ebp-12], eax
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret

concat:
	; ptr concat(ptr one,ptr two)
	push ebp
	mov ebp, esp
	sub esp, 32
	mov dword [ebp-8], ecx
	mov dword [ebp-12], edx
	push 0
	pop eax
	mov dword [ebp-16], eax
	push dword [ebp-12]
	push dword [ebp-8]
	call concat_strings_hl
	add esp, 8
	mov dword [ebp-16], eax
	push dword [ebp-16]
	pop eax
	add esp, 32
	pop ebp
	ret

to_num:
	; int to_num(ptr str)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], dword 0
	push dword [ebp-8]
	call string_to_number_hl
	add esp, 4
	mov dword [ebp-12], eax
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret
extern file_write_hl
extern file_read_hl

f_write:
	; void f_write(ptr path,ptr value)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], edx
	push dword [ebp-12]
	push dword [ebp-8]
	call file_write_hl
	add esp, 8
	xor eax, eax
	add esp, 24
	pop ebp
	ret

f_read:
	; ptr f_read(ptr path)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	push 0
	pop eax
	mov dword [ebp-12], eax
	push dword [ebp-8]
	call file_read_hl
	add esp, 4
	mov dword [ebp-12], eax
	push dword [ebp-12]
	pop eax
	add esp, 24
	pop ebp
	ret

main:
	; int main()
	push ebp
	mov ebp, esp
	sub esp, 8
	push s_0
	pop ecx
	call f_read
	push eax
	pop ecx
	call prints
	xor eax, eax
	add esp, 8
	pop ebp
	ret

section .data
	s_0: db "test.txt",0
	numfmt: db "%d",0
	charfmt: db "%c",0
	strfmt: db "%s",0
	newline: db 10,0
