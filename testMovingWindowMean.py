import time

iters = 365*24*60*60

listLen = 300
idx1 = -listLen+1
tl = list(range(0, listLen))
multip = 3.2

st = time.time()
tls = sum(tl)*multip

for i in range(0, iters):
    tls0 = tl[0]*multip
    tl = tl[idx1:] + [i]
    tls = tls - tls0 + tl[-1]*multip

t1 = time.time() - st
print("Subtract and add method took %s seconds" % str(t1))

tl = list(range(0, listLen))

st = time.time()

for i in range(0, iters):
    tl = tl[idx1:] + [i]
    tls = sum(tl)*multip

t2 = time.time() - st
print("Total sum method took %s seconds" % str(t2))

print("Subtract-add method duration is %s percent of total sum method." % str(round(100*t1/t2)))