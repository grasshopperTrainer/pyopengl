
a = [1,2,3]
b = [4,5,6]

k = [9,8,7]
m = [6,5,4]

for i,ii in zip(zip(a,b), zip(k,m)):
    print(i,ii)