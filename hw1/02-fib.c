#include <stddef.h>
#include <stdio.h>

int fib(int n) {
    int a = 0;
    int b = 1;

    for (int i = 0; i < n; i++) {
        int sum = a + b;
        a = b;
        b = sum;
    }

    return a;
}

int main(void) {
    for (int i = 0; i < 20; ++i) printf("fib(%2d) = %3x\n", i, fib(i));
    return 0;
}
