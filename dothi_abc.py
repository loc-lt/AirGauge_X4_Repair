import matplotlib.pyplot as plt

with open("data20231221_144049.txt",'r') as filename:
    txt = filename.read()
list_total = txt.split()
list_a = []
list_b = []
x_axis = []

for i in range(len(list_total)):
    if list_total[i]=="ACH":
        if float(list_total[i+1][:-2]) < 16:
            list_a.append(float(list_total[i+1][:-2]))
    elif list_total[i]=="BCH":
        if float(list_total[i+1][:-2]) < 16:
            list_b.append(float(list_total[i+1][:-2]))

for i in range(len(list_a)):
    x_axis.append(str(i))

print(max(list_a))
print(max(list_b))
min_a = [15.989]*len(list_a)
max_a = [15.999]*len(list_a)
thresh_a = [15.980]*len(list_a)
min_b = [11.11]*len(list_b)
max_b = [11.15]*len(list_b)
thresh_b = [11.16]*len(list_b)

# Comment qua lại 2 cụm code dưới để theo dõi dữ liệu kênh A và kênh B

# # Kênh A để đọc dữ liệu từ Ring (sẽ phải đo 3 lần), mỗi lần cách nhau chưa rõ ràng, cũng ko có cách nào rõ biệt nhận
# plt.plot(x_axis, list_a)
# plt.plot(x_axis, min_a)
# plt.plot(x_axis, max_a)
# plt.plot(x_axis, thresh_a)

# Kênh B để đọc dữ liệu từ Ping (đo 2 lần, mỗi lần đọc cách nhau 1 lần rút con hàng BW Mini ra khỏi Ping)
# Tức là mình sẽ nhận biết 2 lần đọc khi đường kính nó quay lại  trên / dưới Threshold  
plt.plot(x_axis, list_b[0:len(list_a)])
plt.plot(x_axis, min_b)
plt.plot(x_axis, max_b)
plt.plot(x_axis, thresh_b)

plt.title('title name')
plt.xlabel('x_axis name')
plt.ylabel('y_axis name')
plt.show()