import matplotlib.pyplot as plt

with open("test2.txt",'r') as filename:
    txt = filename.read()
list_total = txt.split()
list_a = []
list_b = []
x_axis = []

for i in range(len(list_total)):
    if list_total[i]=="ACH":
        if float(list_total[i+1][:-2]) < 40.3:
            list_a.append(float(list_total[i+1][:-2]))
        
    elif list_total[i]=="BCH":
        if float(list_total[i+1][:-2]) < 40.3:
            list_b.append(float(list_total[i+1][:-2]))
for i in range(len(list_a)):
    x_axis.append(str(i))

print(max(list_a))
print(max(list_b))
min = [40]*len(list_a)
max = [40.025]*len(list_a)
thresh = [40.05]*len(list_a)

plt.plot(x_axis, list_b[0:len(list_a)]) # Dữ liệu kênh B
# plt.plot(x_axis, list_a) # Dữ liệu kênh A
plt.plot(x_axis, min) # Đường min, y = 40
plt.plot(x_axis, max) # Đường max, y = 40.05
plt.plot(x_axis, thresh) # Đường threshold, y = 40.25

plt.title('title name')
plt.xlabel('x_axis name')
plt.ylabel('y_axis name')
plt.show()