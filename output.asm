section .text

global main

	
extern printf
extern scanf
extern malloc
extern free
extern ExitProcess@4


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
extern fib_hl

fib:
	; int fib(int n)
	push ebp
	mov ebp, esp
	sub esp, 24
	mov dword [ebp-8], ecx
	mov dword [ebp-12], dword 0
	push dword [ebp-8]
	call fib_hl
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
	mov dword [ebp-16], dword 0
	PREIF0:
	push dword [ebp-16]
	mov ebx, 42
	pop eax
	cmp eax, ebx
	jl L3
	jnl L4
	L3:
	push 1
	jmp L5
	L4:
	push 0
	L5:
	pop eax
	cmp eax, 0
	je END2
	jmp WHILE1
	WHILE1:
	push s_0
	pop ecx
	call prints
	push dword [ebp-16]
	pop ecx
	call print
	push s_1
	pop ecx
	call prints
	push dword [ebp-16]
	pop ecx
	call fib
	push eax
	pop ecx
	call println
	push dword [ebp-16]
	mov ebx, 1
	pop eax
	add eax, ebx
	push eax
	pop eax
	mov dword [ebp-16], eax
	jmp PREIF0
	END2:
	xor eax, eax
	add esp, 16
	pop ebp
	ret

section .data
	s_0: db "fibonacci at ",0
	s_1: db " is - ",0
	numfmt: db "%d",0
	charfmt: db "%c",0
	strfmt: db "%s",0
	newline: db 10,0
