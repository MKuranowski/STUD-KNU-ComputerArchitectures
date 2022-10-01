#include <stdio.h>

int main(void) {
    int i, j, temp;
    int A[20] = {7, 5, 12, 92, 8, 68, 0, 13, 158, 27, 99, 112, 140, 118, 117, 221, 8, 21, 19, 5};
    for (i = 0; i < 19; i++) {
        for (j = 0; j < 19 - i; j++) {
            if (A[j] > A[j + 1]) {
                temp = A[j];
                A[j] = A[j + 1];
                A[j + 1] = temp;
            }
        }
    }

    for (int i = 0; i < 20; ++i) printf("%d ", A[i]);
    putc('\n', stdout);

    return 0;
}
