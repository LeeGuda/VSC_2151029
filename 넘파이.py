import numpy as np

# a = np.array([1,2,3])
# print(a)

# b = np.array([[1,2,3],[4,5,6],[7,8,9]])
# print(b)

x = np.array([[1,2],[3,4]])
y = np.array([[5,6],[7,8]])
print(np.vstack((x,y)))  # 수직으로 쌓기
print(np.hstack((x,y)))  # 수평으로 쌓기

