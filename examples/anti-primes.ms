fun cntDivs(n) {
    if (n < 2) return 1
    cnt = i = 2
    while(i <= n//2) {
        if(n % i == 0) cnt+=1
        i+=1
    }
    return cnt
}

max_div = 0
cnt = 0
n = 1
"The first 15 anti-primes are:\n"
while(cnt < 15) {
    d = cntDivs(n)
    if(d > max_div) {
        n++"\n"
        max_div = d
        cnt+=1
    }
    n+=1
}