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



# Tutorials

## functions

* staticaly typed
* so fast

```hl
def foo(arg1:int,arg2:int) -> int {
    return arg1 + arg2
}
```

schema:
    def NAME(ARGS) -> ReturnType {
        body
    }

## variables

* staticaly typed

```hl
int x = 0
x = 10
```
```c
schema:
    TYPE NAME = EXPR
    NAME = EXPR
```
## if

```hl
int x = 10
if(x < 12) {
    body
}
```
```c
schema:
    IF(CONDITION) {
        body
    }
```