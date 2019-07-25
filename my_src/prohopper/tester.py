a = [1,2,3,4,5]
k = filter(lambda x:x if x/2 == 1 else None, a)
print(list(k))