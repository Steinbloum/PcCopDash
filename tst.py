import random
import itertools


ls = list(itertools.chain.from_iterable([[x]*y for x, y in zip(range(1,21), range(20,1,-1))]))
print(ls)
# print([len(x) for x in ls])
print(random.choice(ls))