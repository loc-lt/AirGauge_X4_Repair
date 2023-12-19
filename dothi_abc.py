import matplotlib.pyplot as plt

with open("data20231213_133557.txt",'r') as filename:
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


plt.plot(x_axis, list_a)
plt.plot(x_axis, min_a)
plt.plot(x_axis, max_a)
plt.plot(x_axis, thresh_a)

# plt.plot(x_axis, list_b[0:len(list_a)])
# plt.plot(x_axis, min_b)
# plt.plot(x_axis, max_b)
# plt.plot(x_axis, thresh_b)

plt.title('title name')
plt.xlabel('x_axis name')
plt.ylabel('y_axis name')
plt.show()