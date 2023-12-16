# Hello Lang

# autor - Yula, telegram @yula1000

A programming language.

* syntax like C
* Type checking like C++

hellolang currentlu compiles on NASM x86_64 windows executable


## hello world example

```hl
#include lib.std

def main(argc : int, argv : ptr) -> int {
    $prints("Hello, World!\n")
    return 0
}
```

## fibonacci numbers example
```hl
#include lib.std
#include lib.math

def main(argc : int, argv : ptr) -> int {
    for(int i = 0; i < 31; i = i + 1) {
        $println($fib(i))
    }
    return 0
}
```


## Compiling

for compile using gcc and nasm

```cmd
python main.py file.hl -o output.exe
```
