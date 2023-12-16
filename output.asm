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

main:
	; int main(int argc,ptr argv)
	push ebp
	mov ebp, esp
	sub esp, 16
	mov edx, dword [ebp+8]
	mov dword [ebp-8], edx
	mov edx, dword [ebp+12]
	mov [ebp-12], edx
	mov ecx, 1
	call calloc
	push eax
	pop eax
	mov dword [ebp-16], eax
	push dword [ebp-16]
	pop ecx
	mov edx, 20
	call __write
	push dword [ebp-16]
	pop eax
	push dword [eax]
	pop ecx
	call print
	xor eax, eax
	add esp, 16
	pop ebp
	ret

section .data
	numfmt: db "%d",0
	charfmt: db "%c",0
	strfmt: db "%s",0
	newline: db 10,0
