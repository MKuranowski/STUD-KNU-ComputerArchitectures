#!/bin/sh

prog="${SIMULATOR:-python3 riscv_sim.py}"
tests="write_to_zero immediates arithmetic mul overflow memory branches jump_and_link"
tests_count=$(echo "$tests" | wc -w | sed -e 's/^[[:space:]]*//')
n=1
ret_code=0

echo TAP Version 14
echo 1..$tests_count

for test in $tests; do
    diff_result=$(python3 assembler.py "tests/$test.s" | $prog | diff - "tests/$test.out")
    if [ $? -eq 0 ]; then
        echo ok $n - $test
    else
        echo not ok $n - $test
        echo '  ---'
        echo '  diff: |'
        echo "$diff_result" | sed -e 's/^/    /'
        echo '  ...'
        ret_code=1
    fi

    n=$(( n + 1 ))
done

return $ret_code
