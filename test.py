from tkinter import *
from tkinter import messagebox, ttk
import serial
import serial.tools.list_ports
import datetime
import requests
import json
import pandas as pd
import traceback
from ERROR import *
from PIL import ImageTk, Image

save = False
scan_flag = meter_flag = ready_flag = False
DMC = Amin = Amax = Bmin = Bmax = None
count = 0
lstach =[]
lstbch = []
font_style = "Calibri"
font_size = 10
ports = serial.tools.list_ports.comports()
list_port = []
config_file = pd.read_csv("config.csv", index_col=0)

def disable_event():
    pass

def get_user(password):
    url = 'http://192.168.8.21:5000/api/v1/Laser/Get_user_laser/'+password
    Req = requests.get(url)
    user = json.loads(Req.text)['data'][0]['Name']
    scrt = json.loads(Req.text)['data'][0]['Security']
    return user, scrt

# Giao diện đăng nhập
def login():
    try:
        def set_security_level():
            global security_level
            global user_name
            try:
                user_data = get_user(ET_password.get())
                user_name = user_data[0]
                security_level = int(user_data[1])
                messagebox.showinfo("Đăng nhập", "Thành công")
                tk_login.destroy()
                tk_login.quit()
            except:
                security_level = 0
                messagebox.showerror("Đăng nhập", "Sai mật khẩu")
                tk_login.destroy()
                tk_login.quit()
        tk_login = Toplevel(selectcom)
        tk_login.title("Đăng nhập")
        tk_login.geometry("250x90+800+400")
        tk_login.grab_set()
        tk_login.protocol("WM_DELETE_WINDOW", disable_event)
        tk_login.configure(bg='#FFFFFF')
        LB_password = Label(tk_login, text="Mật khẩu", font=(
            font_style, font_size), bg='#ffffff', anchor=W)
        LB_password.place(x=15, y=10, width=70, height=30)
        ET_password = Entry(tk_login, font=(font_style, font_size), show="*")
        ET_password.place(x=85, y=10, width=150, height=30)
        Btn_login = Button(tk_login, text="Xác nhận",
                           command=set_security_level)
        Btn_login.place(x=85, y=50, width=80, height=30)
        tk_login.mainloop()
        return security_level
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        return 0

# Giao diện để mình set các thông số quan trọng để khi thực hiện đo dữ liệu đường kính từ các con hàng thì sẽ quyết định được con hàng đó là OK/NG/Special/Return
def Configure():

    # Lưu các giá trị người dùng Config ở phía dưới
    def saveconfig():
        # Các thông số này là gì
        global const_Athresh, const_Bthresh, const_Amin, const_Amax, const_Bmin, const_Bmax, A_title, B_title, config_file, const_Alow, const_Ahigh, title
        title = []
        Amin = []
        Amax = []
        Type = []
        Athresh = []
        Alow = []
        Ahigh = []
        for i in range(sokenh):    
            title.append(ET_Atit[i].get())
            Type.append(ET_Atype[i].get())
            Amin.append(float(ET_Amin[i].get()))
            Amax.append(float(ET_Amax[i].get()))
            Athresh.append(float(ET_Athresh[i].get()))
            Alow.append(float(ET_Alow[i].get()))
            Ahigh.append(float(ET_Ahigh[i].get()))
            config_file.loc[config_file.index[i], "Title"] = title[i]
            config_file.loc[config_file.index[i], "Min"] = Amin[i]
            config_file.loc[config_file.index[i], "Max"] = Amax[i]
            config_file.loc[config_file.index[i], "Threshold"] = Athresh[i]
            config_file.loc[config_file.index[i], "Type"] = Type[i]        
            config_file.loc[config_file.index[i], "Special Low"] = Alow[i]
            config_file.loc[config_file.index[i], "Special High"] = Ahigh[i]
        config_file.loc[config_file.index[0], "Channel"] = sokenh 
        config_file.to_csv("config.csv")
        tk_config.destroy()

    # Gán giá trị vừa chọn cho sokenh
    def handle_selection(event):
        global sokenh
        selected_item = combobox.get()
        sokenh = int(combobox.get().split()[0]) # sokenh sinh ra từ đây
        kichthuoc = 50+35*sokenh # kichthuoc sinh ra từ đây
        tk_config.geometry(f"1420x{kichthuoc}")
        frm1.place_configure(height=40 + 35*sokenh)
        print("So kenh = ", sokenh)
        print("Selected item:", selected_item)

    if 1:
        global sokenh, kichthuoc
        print(config_file.loc["Ach","Channel"])
        sokenh = int(config_file.loc["Ach","Channel"])
        tk_config = Toplevel(selectcom)
        kichthuoc = 50+35*sokenh
        tk_config.geometry(f"1420x{kichthuoc}")
        
        # Chỗ này để Set các số lượng Channel
        combobox = ttk.Combobox(tk_config,state="readonly",height=6, font=10)
        combobox['values'] = list(f"{i+1} Channel" for i in range(12)) # Từ 2 -> 12

        # Chỗ này để chọn số kênh -> kichthuoc
        combobox.current(sokenh-1)  # Chọn mặc định CH1
        combobox.bind("<<ComboboxSelected>>", handle_selection)
        combobox.place(x=1150, y=40, height=30, width=120)

        ET_Atit = []
        LB_Aindex = []
        ET_Athresh = []
        ET_Alow = []
        ET_Amin = []
        ET_Amax = []
        ET_Ahigh = []
        ET_Atype = []

        frm1 = Frame(tk_config)
        frm1.place(x=0,y=0,width=1140,height=40+35*sokenh)

        for i in range (12):
            LB_Aindex.append(Label(frm1, text=config_file.index[i], font=10, anchor=W))
            LB_Aindex[i].place(x=30, y=40 + 35*i, height=30, width=50)

            ET_Atit.append(Entry(frm1, font=8))
            ET_Atit[i].place(x=100, y=40 + 35*i, height=30, width=120)
            ET_Atit[i].insert(0, config_file.loc[config_file.index[i], "Title"])
            ET_Athresh.append(Entry(frm1, font=8))
            ET_Athresh[i].place(x=250, y=40 + 35*i, height=30, width=120)
            ET_Athresh[i].insert(0, config_file.loc[config_file.index[i], "Threshold"])

            ET_Alow.append(Entry(frm1, font=8))
            ET_Alow[i].place(x=400, y=40 + 35*i, height=30, width=120)
            ET_Alow[i].insert(0, config_file.loc[config_file.index[i], "Special Low"])

            ET_Amin.append(Entry(frm1, font=8))
            ET_Amin[i].place(x=550, y=40 + 35*i, height=30, width=120)
            ET_Amin[i].insert(0, config_file.loc[config_file.index[i], "Min"])   

            ET_Amax.append(Entry(frm1, font=8))
            ET_Amax[i].place(x=700, y=40 + 35*i, height=30, width=120)
            ET_Amax[i].insert(0, config_file.loc[config_file.index[i], "Max"])

            ET_Ahigh.append(Entry(frm1, font=8))
            ET_Ahigh[i].place(x=850, y=40 + 35*i, height=30, width=120)
            ET_Ahigh[i].insert(0, config_file.loc[config_file.index[i], "Special High"])

            # ID, OD là cqq gì?
            ET_Atype.append(ttk.Combobox(frm1,height=2,state="readonly"))
            ET_Atype[i]['values'] = ['ID', 'OD']
            ET_Atype[i].set(config_file.loc[config_file.index[i], "Type"])  
            ET_Atype[i].bind("<<ComboboxSelected>>", handle_selection)
            ET_Atype[i].place(x=1000, y=40 + 35*i, height=30, width=120)

        # Các thông số chính của mỗi Ach, Bch, Cch, Dch => Xch là cái gì???? 
        # Các thông số Title, Threshold, Special Low, Min, Max, Special High, Type là gì????
        LB_Atit = Label(tk_config, text="Title", font=10, anchor=W)
        LB_Atit.place(x=100, y=10, height=30, width=100)
        LB_Athresh = Label(tk_config, text="Threshold", font=10)
        LB_Athresh.place(x=250, y=10, height=30, width=120)
        LB_Alow = Label(tk_config, text="Special Low", font=10)
        LB_Alow.place(x=400, y=10, height=30, width=120)
        LB_Amin = Label(tk_config, text="Min", font=10)
        LB_Amin.place(x=550, y=10, height=30, width=120)
        LB_Amax = Label(tk_config, text="Max", font=10)
        LB_Amax.place(x=700, y=10, height=30, width=120)
        LB_Ahigh = Label(tk_config, text="Special High", font=10)
        LB_Ahigh.place(x=850, y=10, height=30, width=120)
        LB_Atype = Label(tk_config, text="Type", font=10)
        LB_Atype.place(x=1000, y=10, height=30, width=120)
        Btn_Save = Button(tk_config, text="Configure",command=saveconfig, font=10)
        Btn_Save.place(x=1300, y=40, height=30, width=100)

# Hàm này để làm gì
def count_history(strtoday,strnextday,Result):
    url = 'http://192.168.8.21:5000/api/v1/Measure_Diameter/count_history_Measure_Diameter_GC'
    payl = {
            "Result": Result,
            "strnextday": strnextday,
            "strtoday": strtoday
            }
    Req = requests.post(url, json=payl, timeout=1)
    get =  json.loads( Req.text )
    return str(get)   

# Hàm này để lưu các giá trị đo độ nghiêng gia công????
def savedata(DMC, Amin, Amax, Bmin, Bmax, result, TimescanDMC):
    url = 'http://192.168.8.21:5000/api/v1/Measure_Diameter/Insert_Measure_Diameter_GC'
    payl = {
        "A_Max": str(Amax),
        "A_Min": str(Amin),
        "B_Max": str(Bmax),
        "B_Min": str(Bmin),
        "DMC": DMC,
        "Result": result,
        "Product_Name":mahang,
        "Time_Finish": str(datetime.datetime.now())[:-3],
        "Time_ScanDMC": TimescanDMC
    }
    if connect_server:
        try:
            Req = requests.post(url, json=payl)
            if Req.text.strip()=='"OK"':
                return True
            return False
        except:
            Systemp_log(payl).append_new_line()
    else:
        Systemp_log(payl).append_new_line()

# Kiểm tra có kết nối với cái gì???
def check_connect():
    global connect_server
    try:
        ET_time.config(text=datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
        today = datetime.datetime.now()
        nextday = today + datetime.timedelta(days=1)
        strtoday = today.strftime("%Y-%m-%d")
        strnextday = nextday.strftime("%Y-%m-%d")

        # Set giá trị cho 2 ô ET_NG và ET_OK
        ET_NG.configure(text=count_history(strtoday,strnextday,'NG'))
        ET_OK.configure(text=count_history(strtoday,strnextday,'OK'))

        ET_OK.config(highlightbackground="#294c6e")
        ET_NG.config(highlightbackground="#294c6e")
        connect_server = True
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        ET_OK.config(highlightbackground="#ff0000")
        ET_NG.config(highlightbackground="#ff0000")
        connect_server = False
    ET_OK.after(1000,check_connect)

# Đọc dữ liệu từ máy quét (đọc lấy DMC_Product)
def read_scanner():
    global DMC, Amin, Amax, Bmin, Bmax, TimescanDMC, scan_flag, mahang
    try:
        if not scan_ser.is_open:
            scan_ser.open()
            LB_ERROR.configure(background="#00ff00", text="Kết nối tay quét")
        bytesToRead = scan_ser.inWaiting()
        data = scan_ser.read(bytesToRead)
        if len(data) > 0:
            print(data)
            if len(data) == 29:
                kq = data.decode("utf-8")
                if kq[9:14]=='E9238':
                    mahang = 'A2012004'
                    DMC = kq
                    Amin = Amax = Bmin = Bmax = None
                    TimescanDMC = str(datetime.datetime.now())[:-3]
                    ET_DMC.config(text=DMC)
                    ET_A_min.config(text="",bg="#ffffff")
                    ET_B_min.config(text="",bg="#ffffff")
                    ET_A_max.config(text="",bg="#ffffff")
                    ET_B_max.config(text="",bg="#ffffff")
                    LB_ERROR.config(text="Chờ kết quả đo "+mahang,
                                    background="#ffff00")
                elif kq[9:14]=='E9154':
                    mahang = 'A2012003'
                    DMC = kq
                    Amin = Amax = Bmin = Bmax = None
                    TimescanDMC = str(datetime.datetime.now())[:-3]
                    ET_DMC.config(text=DMC)
                    ET_A_min.config(text="",bg="#ffffff")
                    ET_B_min.config(text="",bg="#ffffff")
                    ET_A_max.config(text="",bg="#ffffff")
                    ET_B_max.config(text="",bg="#ffffff")
                    LB_ERROR.config(text="Chờ kết quả đo "+mahang,
                                    background="#ffff00")
            else:
                LB_ERROR.config(text="Mã không đúng số lượng: " +
                                str(data[:-1]), background="#ff0000")
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        scan_ser.close()
        LB_ERROR.configure(background="#ff0000", text="Mất kết nối tay quét")
    LB_ERROR.after(1000, read_scanner)

# Đọc dữ liệu từ việc đo thông số từ 2 cổng đo A, B (Đúng ko)
def read_meter():
    # Hàm này là hàm chính nè, sau này mình sửa sửa hàm này là chính để thêm 
    global DMC, Amin, Bmin, Amax, Bmax, count, lstach, lstbch    
    try:
        if not meter_ser.is_open:
            meter_ser.open()
            LB_ERROR.configure(background="#00ff00", text="Kết nối thiết bị đo")
        if DMC != None:
            # Hàm này để làm gì 
            meter_ser.write("D".encode())
            bytesToRead = meter_ser.inWaiting()
            # Đọc liên tục các giá trị từ 2 lỗ khí (tương đương với 2 cổng đo A, B)
            data = meter_ser.read(bytesToRead)
            # Dữ liệu chắc là liên tục nhưng được ngăn cách bởi dấu ' nên split trước, nhưng tại sao lại chọn giá trị thứ 2 rồi slipt nữa?? 
            lstdata = str(data).split("'")[1].split()
            if len(lstdata)!=0:
                # Chưa hiểu đoạn này
                for i in range(len(lstdata)):
                    if lstdata[i]=="ACH":
                        Ach = float(lstdata[i+1][:-2])
                    if lstdata[i]=="BCH":
                        Bch = float(lstdata[i+1][:-2])
                # Với điều kiện này Ach và Bch đọc được phải nhỏ hơn ngưỡng const_Athresh và const_Bthresh
                if (Ach < const_Athresh or mahang == 'A2012004') and Bch < const_Bthresh:
                    # Nếu số lượng count (là gì?) thì chỉ cần + 1 là xong -> chưa hiểu
                    if count < 2:
                        count+=1
                    else:
                        # Nếu trong TH đã có 2 count thì phải kiểm tra lại
                        LB_ERROR.config(
                                    text="Đang kiểm tra", background="#00ff00")
                        # Thêm phần tử mới trong lstach và lstbch
                        lstach.append(Ach) 
                        lstbch.append(Bch)
                        if len(lstach)>2:
                            Amin = min(lstach[:-2])
                            Amax = max(lstach[:-2])
                            Bmin = min(lstbch[:-2])
                            Bmax = max(lstbch[:-2])
                            
                            ET_B_min.config(text=Bmin)                            
                            ET_B_max.config(text=Bmax)
                            if mahang == "A2012003":
                                ET_A_min.config(text=Amin)
                                ET_A_max.config(text=Amax)
                                if not (Amax > const_Amin and Amax < const_Amax):
                                    ET_A_max.config(bg="#ff0000")
                                    LB_ERROR.config(
                                        text="Dữ liệu NG", background="#ff0000") 
                                elif not (Amin > const_Amin and Amin < const_Amax):
                                    ET_A_min.config(bg="#ff0000")
                                    LB_ERROR.config(
                                        text="Dữ liệu NG", background="#ff0000") 
                            if not (Bmax > const_Bmin and Bmax < const_Bmax):
                                ET_B_max.config(bg="#ff0000")
                                LB_ERROR.config(
                                    text="Dữ liệu NG", background="#ff0000") 
                            if not (Bmin > const_Bmin and Bmin < const_Bmax):
                                ET_B_min.config(bg="#ff0000")
                                LB_ERROR.config(
                                    text="Dữ liệu NG", background="#ff0000") 
                elif count > 0:
                    count-=1
                    if count == 0 and len(lstach)>5:
                        if Bmax > const_Bmin and Bmax < const_Bmax and Bmin > const_Bmin and Bmin < const_Bmax:
                            if Amax > const_Amin and Amax < const_Amax and Amin > const_Amin and Amin < const_Amax or mahang == 'A2012004':
                                Result = "OK"
                            else:
                                Result = "NG"
                        else:
                            Result = "NG"                                    
                        try:
                            savedata(DMC, Amin, Amax, Bmin, Bmax, Result, TimescanDMC)
                            DMC = Amin = Amax = Bmin = Bmax = None
                            lstach = []
                            lstbch = []    
                            if Result == "OK":
                                LB_ERROR.config(
                                    text="Kết quả đo OK", background="#00ff00")
                            else:
                                LB_ERROR.config(
                                    text="Kết quả đo NG", background="#ff0000")
                            
                        except:
                            Systemp_log(traceback.format_exc()).append_new_line()
                            LB_ERROR.config(
                                text="Lưu giá trị thất bại", background="#ff0000")
                
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        meter_ser.close()
        LB_ERROR.configure(background="#ff0000",
                           text="Mất kết nối thiết bị đo")
    LB_ERROR.after(300, read_meter)

# Xác nhận các thông số A_title, B_title, const_Alow, const_Amin, const_Bmin, const_Amax, const_Bmax, const_Athresh, const_Bthresh, const_Ahigh
def confirm():
    global ready_flag, const_Athresh, const_Bthresh, const_Amin, const_Amax, const_Bmin, const_Bmax, A_title, B_title, config_file,const_Alow, const_Ahigh
    if not scan_flag:
        messagebox.showerror("Lỗi", "Chưa chọn thiết bị tay scan")
    elif not meter_flag:
        messagebox.showerror("Lỗi", "Chưa chọn thiết bị đo")
    else:
        A_title = config_file.loc["Ach", "Title"]
        B_title = config_file.loc["Bch", "Title"]
        const_Alow = config_file.loc["Ach", "Special Low"]
        const_Amin = config_file.loc["Ach", "Min"]
        const_Bmin = config_file.loc["Bch", "Min"]
        const_Amax = config_file.loc["Ach", "Max"]
        const_Bmax = config_file.loc["Bch", "Max"]
        const_Athresh = config_file.loc["Ach", "Threshold"]
        const_Bthresh = config_file.loc["Bch", "Threshold"]
        const_Ahigh = config_file.loc["Ach", "Special High"]  
        selectcom.destroy()
        ready_flag = True

# Kết nối với tay quét -> để quét mã con hàng
def selectscan(i): 
    global scan_ser, scan_flag
    port = CB_scan.get().split("(")[1].split(")")[0]
    try:
        scan_ser.close()
    except:
        pass
    try:
        scan_ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )
        scan_ser.isOpen()
        scan_flag = True
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        scan_flag = False
        messagebox.showerror(
            "Lỗi serial", "Không thể kết nối thiết bị tay quét")

# Kết nối với đồng hồ đo (chưa hiểu lắm, là kết nối với thực chất là cái gì ta?? kết nối với cái máy đo kín khí luôn fk)
def selectmeter(i):
    global meter_ser, meter_flag
    port = CB_meter.get().split("(")[1].split(")")[0]

    try:
        meter_ser.close()
    except:
        pass
    try:
        meter_ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=False
        )
        meter_ser.isOpen()
        meter_flag = True
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        meter_flag = False
        messagebox.showerror("Lỗi serial", "Không thể kết nối thiết bị đo")

for port, desc, hwid in sorted(ports):
    list_port.append(desc)

# ----------------Giao diện chọn "USB Serial Device: Tên của tay quét để quét DMC của con hàng" và "USB Serial Port: Port / Tên của máy đo đường kính"-----------------
selectcom = Tk()
selectcom.geometry("500x150+50+50")
selectcom.resizable(False,False)
selectcom.iconbitmap("abc.ico")

# Chọn USB Serial Device: Tên của tay quét để quét DMC của con hàng
LB_scan = Label(selectcom, text="USB Serial Device:", font=10, anchor=W)
LB_scan.place(x=10, y=10, height=30, width=200)
CB_scan = ttk.Combobox(selectcom, state="readonly", values=list_port, font=8)
CB_scan.bind("<<ComboboxSelected>>", selectscan)
CB_scan.place(x=210, y=10, height=30, width=280)

# Chọn USB Serial Port: Port / Tên của máy đo đường kính
LB_meter = Label(selectcom, text="USB Serial Port:", font=10, anchor=W)
LB_meter.place(x=10, y=45, height=30, width=200)
CB_meter = ttk.Combobox(selectcom, state="readonly", values=list_port, font=8)
CB_meter.bind("<<ComboboxSelected>>", selectmeter)
CB_meter.place(x=210, y=45, height=30, width=280)

# Khi click vào nút Configure, giao diện mới hiện ra để chọn các thông số (Trừ Threshold)
Btn_Configre = Button(selectcom, text="Configure", command=Configure, font=10)
Btn_Configre.place(x=190, y=80, height=40, width=100)

Btn_COM = Button(selectcom, text="Connect", command=confirm, font=10)
Btn_COM.place(x=390, y=80, height=40, width=100)
selectcom.mainloop()
# --------------------------------------------------------

# Giao diện chính của chương trình đo đường kính bằng kín khí
port_count = 5
wk = Tk()
height = max(295+45*sokenh,475)
wk.geometry("800x"+str(height))
wk.iconbitmap("abc.ico")
frame_title = Frame(wk, highlightbackground="#294c6e",
                    highlightthickness=2, background="#f2f2f2")
frame_title.place(x=0, y=0, height=75, width=800)

# Tiêu đề
name = Label(wk,text="AIR GAUGE",font=("Bold",22),fg='navy')
name.place(x=350,y=20)
ET_time = Label(text=datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"),
                background="#f2f2f2", anchor=W, fg="#000000", font=("Helvetica", 12))
ET_time.place(x=660, y=5, height=20)
logo = ImageTk.PhotoImage(Image.open('logo.png'))
LB_logo = Label(frame_title, image=logo).place(
    x=0, y=0, height=75, width=188)
frame_main = Frame(wk)
frame_main.place(x=0, y=75, height=355 + 45*sokenh, width=800)
frame_result = Frame(frame_main, highlightbackground="#294c6e",
                     highlightthickness=1)
frame_result.place(x=10, y=85, width=525, height=50 + 45*sokenh)
frame_total = Frame(frame_main, highlightbackground="#294c6e",
                    highlightthickness=1)
frame_total.place(x=545, y=85, width=245, height=230)

# DATA DMC quét được
LB_DMC = Label(frame_main, text="DATA DMC:",highlightbackground="#294c6e", highlightthickness=2,
               background="#6fa7da", font=("Helvetica", 13, "bold"), fg="#ffffff")
LB_DMC.place(x=10, y=15, height=50, width=120)
ET_DMC = Label(frame_main, highlightbackground="#294c6e",
               highlightthickness=2, background="#ffffff", font=("Helvetica", 25, "bold"))
ET_DMC.place(x=145, y=15, height=50, width=645)

# Min Max cho số kênh A, B, C, D, .... được Configure
LB_min = Label(frame_result, text="Min", font=("Helvetica", 14, "bold"), fg="#FF9900")
LB_min.place(x=130, y=0, height=40, width=180)
LB_max = Label(frame_result, text="Max",font=("Helvetica", 14, "bold"), fg="#FF9900")
LB_max.place(x=330, y=0, height=40, width=180)

LB_A = []
ET_A_min = []
ET_A_max = []
ET_B_min = []
ET_B_max = []

for i in range (sokenh):
    LB_A.append(Label(frame_result, text=title[i], font=("Helvetica", 14, "bold"), fg="#000000"))
    LB_A[i].place(x=5, y=40 + 45*i, height=35, width=120)

    ET_A_min.append(Label(frame_result,text="", highlightbackground="#294c6e", highlightthickness=3, background="#ffffff", font=("Helvetica", 20, "bold")))
    ET_A_min[i].place(x=130, y=40 + 45*i, height=35, width=180)

    ET_A_max.append(Label(frame_result, highlightbackground="#294c6e", highlightthickness=3, background="#ffffff", font=("Helvetica", 20, "bold")))
    ET_A_max[i].place(x=330, y=40 + 45*i, height=35, width=180)

LB_ERROR = Label(frame_main, text="", highlightbackground="#294c6e",highlightthickness=1, font=("Helvetica", 14, "bold"))
LB_ERROR.place(x=10, y=max(150 + 45*sokenh,330), height=60, width=780)
LB_Total = Label(frame_total, text="TOTAL", highlightbackground="#294c6e",highlightthickness=1, font=("Helvetica", 14, "bold"), fg="#000044")
LB_Total.place(x=-1, y=-1, height=230, width=75)
LB_OK = Label(frame_total, text="OK",font=("Helvetica", 14, "bold"), fg="#005500")
LB_OK.place(x=75, y=40, height=50, width=40)
LB_NG = Label(frame_total, text="NG",font=("Helvetica", 14, "bold"), fg="#990000")
LB_NG.place(x=75, y=140, height=50, width=40)
ET_OK = Label(frame_total, highlightbackground="#294c6e",highlightthickness=3,fg="#005500", background="#ffffff", font=(10))
ET_OK.place(x=120, y=40, height=50, width=110)
ET_NG = Label(frame_total, highlightbackground="#294c6e",highlightthickness=3, background="#ffffff",fg="#990000", font=(10))
ET_NG.place(x=120, y=140, height=50, width=110)
read_meter()
read_scanner()
check_connect()
wk.mainloop()
