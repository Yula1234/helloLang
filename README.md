# Hello Lang

# autor - Yula, telegram @yula1000

A programming language.

* syntax like C
* Type checking like C++

hellolang currentlu compiles on NASM x86_64 windows executable


## Example code

```hl
#include lib.std

def main(argc : int, argv : ptr) -> int {
	$prints("Hello, World!\n")
}
```


## Compiling

for compile using gcc and nasm

```cmd
python main.py file.hl -o output.exe
```
