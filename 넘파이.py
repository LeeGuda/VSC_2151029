import numpy as np

a = np.array([[1,2,3],[4,5,6],[7,8,9]])

# ndim : 축의 개수
# shape : 배열의 형상
# size : 배열 안에 있는 요소들의 총 개수
# dtype : 배열 요소의 자료형
# itemsize : 배열 요소 하나의 바이트 크기
# data : 실제 데이터가 저장되는 메모리 블럭의 주소

print(a.shape) # 배열의 형상
print(a.ndim) #축의 개수
print(a.dtype) # 배열 요소의 자료형
print(a.itemsize) # 배열 요소 하나의 바이트 크기
print(a.size) # 배열 안에 있는 요소들의 총 개수
print(a.data) # 실제 데이터가 저장되는 메모리 블럭의 주소

#zeros(), ones(), eye()
print(np.zeros((3,4)))
print(np.ones((3,4)))
print(np.eye(3))

#arange(), linspace()
print(np.arange(10)) # 0~9
print(np.arange(1,10,2)) # 1~9, 2씩 증가
print(np.linspace(0,1,5)) # 0~1 사이를 5등분
print(np.linspace(0,10,4)) # 0~10 사이를 4등분

