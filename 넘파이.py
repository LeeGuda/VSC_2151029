import numpy as np

# a = np.array([1,2,3])
# print(a)

b = np.array([[1,2,3],[4,5,6],[7,8,9]])

# ndim : 축의 개수
# shape : 배열의 형상
# size : 배열 안에 있는 요소들의 총 개수
# dtype : 배열 요소의 자료형
# itemsize : 배열 요소 하나의 바이트 크기
# data : 실제 데이터가 저장되는 메모리 블럭의 주소

print(b.shape) # 배열의 형상
print(b.ndim) #축의 개수
print(b.dtype) # 배열 요소의 자료형
print(b.itemsize) # 배열 요소 하나의 바이트 크기
print(b.size) # 배열 안에 있는 요소들의 총 개수



# x = np.array([[1,2],[3,4]])
# y = np.array([[5,6],[7,8]])
# print(np.vstack((x,y)))  # 수직으로 쌓기
# print(np.hstack((x,y)))  # 수평으로 쌓기

