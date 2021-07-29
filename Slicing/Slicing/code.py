# t=int(input())
# for i in range(t):
#     a=[]
#     n=int(input())
#     a=list(map(int,input().split(" ")))
#     s=sum(a)
#     if n==s:
#         print("0")
#     elif s<n:
#         print("1")
#     elif s>n:
#         print(s-n)
    

# n=int(input())
# for i in range(n):
#     n,m,i,j=list(map(int,input().split(" ")))
#     one=1
#     if i==1:
#         print(str(n)+" "+str(one)+" "+str(n)+" "+str(m))
#     elif j==1:
#         print(str(one)+" "+str(m)+" "+str(n)+" "+str(m))
#     elif i==n:
#         print(str(one)+" "+str(one)+" "+str(one)+" "+str(m))
#     elif j==m:
#         print(str(one)+" "+str(one)+" "+str(n)+" "+str(one))
#     else:
#         print(str(n)+" "+str(one)+" "+str(one)+" "+str(m))


n,k=list(map(int,input().split(" ")))
a=input()
if n==k:
    print(a)
elif k<n:
    print(a[:k])
elif k>n:
    d=k%n
    if d==0:
        a=(a+'')*(k/n)
    if d
