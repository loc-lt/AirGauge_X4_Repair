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
import pyodbc
save = False
scan_flag = meter_flag = ready_flag = False
DMC = Amin = Amax = Bmin = Bmax = None

conn2 = pyodbc.connect(
        'Driver={SQL Server}; Server=192.168.8.125; Database=QC; UID=sa; PWD=1234; Trusted_Connection=No;')

cursor2 = conn2.cursor()
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

def product_config():
    product_file = pd.read_csv("product.csv",index_col=0)
    def save_product():
        for i in range(len(product_file.index)):
            print(ET_code[i].get())
            product_file.loc[product_file.index[i], 'code'] = ET_code[i].get()
            for j in range(12):
                product_file.loc[product_file.index[i], product_file.columns[j+1]] = Alluse[i][j].get()
        product_file.to_csv("product.csv")
        tk_product.destroy()
    tk_product = Toplevel(selectcom)
    height = len(product_file.index)*40+50
    tk_product.geometry(f"1060x{height}")
    LB_mahang = Label(tk_product,text="Product",bg = "#ffffff", font=8)
    LB_mahang.place(x=10,y=10,width=100,height=30)

    LB_code = Label(tk_product,text="Code",bg = "#ffffff", font=8)
    LB_code.place(x=120,y=10,width=100,height=30)
    BT_save = Button(tk_product,text="Save",bg = "#ffffff", font=8, command=save_product)
    BT_save.place(x=950,y=10,width=100,height=30)
    ET_mahang = []
    CB_Allused = []
    CB_used = []
    ET_code = []
    Alluse = []
    for i in range(ord('a'),ord('m')):
        LB_ch = Label(tk_product,text=chr(i).upper()+'ch',bg = "#ffffff", font=8)
        LB_ch.place(x=(i-ord('a'))*60+230,y=10,width=50,height=30)
    for i in range(len(product_file.index)):
        ET_mahang.append(Entry(tk_product,bg = "#ffffff", font=8))
        ET_mahang[i].place(x=10,y=50+40*i,width=100,height=30)
        ET_mahang[i].insert(0,product_file.index[i])
        ET_code.append(Entry(tk_product,bg = "#ffffff", font=8))
        ET_code[i].place(x=120,y=50+40*i,width=100,height=30)
        ET_code[i].insert(0,product_file.loc[product_file.index[i], "code"])
        inUsed = []
        for j in range(12):
            inUsed.append(IntVar())
        Alluse.append(inUsed)
        for j in range(12):
            Alluse[i][j].set(product_file.loc[product_file.index[i], product_file.columns[j+1]])
            CB_used.append(Checkbutton(tk_product,font=12,variable=Alluse[i][j],onvalue=1,offvalue=0))
            CB_used[j].place(x=(j)*60+230,y=50+40*i,width=50,height=30)
        CB_Allused.append(CB_used)
        CB_used = []

# XONG
# Giao diện để mình set các thông số quan trọng trước khi thực hiện đo dữ liệu đường kính từ các con hàng 
# => quyết định được con hàng đó là OK/NG/Special/Return
def Configure():
    # Lưu các giá trị người dùng Config ở phía dưới
    def saveconfig():
        global sokenh,config_file
        for i in range(12):        
            print(inUsed[i].get())
            # Chính là giá trị của các ô vuông, nếu mình tick vào thì InUsed (trong TH sử dụng)
            config_file.loc[config_file.index[i], "InUsed"] = inUsed[i].get() 
            # Biến Title
            config_file.loc[config_file.index[i], "Title"] = ET_Atit[i].get()
            # Biến Min
            config_file.loc[config_file.index[i], "Min"] = float(ET_Amin[i].get())
            # Biến Max
            config_file.loc[config_file.index[i], "Max"] = float(ET_Amax[i].get())
            # Biến Threshold
            config_file.loc[config_file.index[i], "Threshold"] = float(ET_Athresh[i].get())
            # Biến Type
            config_file.loc[config_file.index[i], "Type"] = ET_Atype[i].get()    
            # Biến Special Low
            config_file.loc[config_file.index[i], "Special Low"] = float(ET_Alow[i].get())
            # Biến Special High
            config_file.loc[config_file.index[i], "Special High"] = float(ET_Ahigh[i].get())

        # Lưu lại config vừa thay đổi vào file config.csv
        config_file.to_csv("config.csv")
        tk_config.destroy()

    if 1:
        global kichthuoc
        tk_config = Toplevel(selectcom)
        kichthuoc = 50+35*12
        tk_config.geometry(f"1420x{kichthuoc}")

        ET_Atit = [] # Title
        LB_Aindex = [] # 
        ET_Athresh = [] # Threshold
        ET_Alow = [] # Special Low
        ET_Amin = [] # Min
        ET_Amax = [] # Max
        ET_Ahigh = [] # Special High
        ET_Atype = [] # ID/OD
        Check_ = [] # Check Inused?

        # Mặc định là 12 kênh (có thể mở rộng trong tương lai nên mới có 12 IntVar)
        var1 = IntVar()
        var2 = IntVar()
        var3 = IntVar()
        var4 = IntVar()
        var5 = IntVar()
        var6 = IntVar()
        var7 = IntVar()
        var8 = IntVar()
        var9 = IntVar()
        var10 = IntVar()
        var11 = IntVar()
        var12 = IntVar()

        # Biến Inused chứa 12 giá check xem kênh nào còn sử dụng
        inUsed = [var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12]

        # Tạo Frame chứa mấy ô để điền thông tin
        frm1 = Frame(tk_config)
        frm1.place(x=0,y=0,width=1140,height=40+35*12)

        # Tạo các ô để nhập dữ liệu config
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

            ET_Atype.append(ttk.Combobox(frm1,height=2,state="readonly"))
            ET_Atype[i]['values'] = ['ID', 'OD']
            
            inUsed[i].set(config_file.loc[config_file.index[i], "InUsed"])
            Check_.append(Checkbutton(tk_config,variable=inUsed[i],onvalue=1,offvalue=0))
            Check_[i].place(x = 1150,y = 40 + 35*i, width=30, height=30)

            ET_Atype[i].set(config_file.loc[config_file.index[i], "Type"])  
            ET_Atype[i].place(x=1000, y=40 + 35*i, height=30, width=120)

        # Các thông số chính của mỗi Ach, Bch, Cch, Dch
        # Các thông số Title, Threshold, Special Low, Min, Max, Special High, Type
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
        Btn_Save = Button(tk_config, text="Save",command=saveconfig, font=10)
        Btn_Save.place(x=1300, y=40, height=30, width=100)
        Btn_pConfigre = Button(tk_config, text="Useage", command=product_config, font=10)
        Btn_pConfigre.place(x=1300, y=80, height=40, width=100)

# Hàm này để đếm số lượng con hàng có kết quả Result từ ngày strtoday to strnextday 
def count_history(strtoday,strnextday,Result):
    url = 'http://192.168.8.21:5000/api/v1/Measure_Diameter/count_history_Measure_Diameter'
    payl = {
            "Result": Result,
            "strnextday": strnextday,
            "strtoday": strtoday
            }
    print(payl)
    Req = requests.post(url, json=payl, timeout=1)
    get =  json.loads( Req.text )
    return str(get)    

# Hàm này để lưu các giá trị khi đo đường kính của một con hàng
def savedata(DMC, Amin, Amax, Bmin, Bmax, result, TimescanDMC):
    cursor2.execute( "INSERT INTO [QC].[dbo].[Measure_Diameter](Product_Name,Time_ScanDMC,DMC,A_Min,A_Max,B_Min,B_Max,Time_Finish,Result) "
                "VALUES ('" + mahang + "','" + TimescanDMC + "','" + DMC + "', '" + str(Amin) + "', '" + str(Amax) + "', '" + str(Bmin) + "','" + str(Bmax) + "', '" + str(datetime.datetime.now())[:-3] + "', '" + result + "') ")
    conn2.commit()
    url = 'http://192.168.8.21:5000/api/v1/Measure_Diameter/Insert_Measure_Diameter'
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
    print(payl)
    if connect_server:
        try:
            Req = requests.post(url, json=payl)
            print(Req.text)
            if Req.text.strip()=='"OK"':
                return True
            return False
        except: 
            Systemp_log(str(payl)).append_new_line()
    else:
        Systemp_log(payl).append_new_line()

# Hàm kiểm tra sự connect với tay quét quét mã dmc và máy đo đường kính
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
        print(Allresult)
        connect_server = True
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        ET_OK.config(highlightbackground="#ff0000")
        ET_NG.config(highlightbackground="#ff0000")
        connect_server = False
    ET_OK.after(1000,check_connect)

# Kiểm tra xem mã con hàng có nằm trong các product mà ta config khi click Useage Button 
def check_mahang(ma):
    product_file = pd.read_csv("product.csv",index_col=0)
    for idx in product_file.index:
        if product_file.loc[idx,'code'] in ma:
            return idx

# Đọc dữ liệu từ máy quét (đọc lấy DMC_Product)
def read_scanner():
    global DMC, TimescanDMC, Allresult, mahang
    try:
        if not scan_ser.is_open:
            scan_ser.open()
            LB_ERROR.configure(background="#00ff00", text="Kết nối tay quét")
        bytesToRead = scan_ser.inWaiting()
        data = scan_ser.read(bytesToRead)
        if len(data) > 0:
            print(data)
            kq = data.decode("utf-8").strip()
            if not recheck:
                if len(kq) == 29:     
                    mahang = check_mahang(kq)                    
                    rsvariable()
                    DMC = kq
                    product_file = pd.read_csv("product.csv",index_col=0)
                    count = 0
                    for idx in range(12):
                        if str(product_file.columns[idx+1]) in Channel:
                            if int(product_file.loc[mahang,product_file.columns[idx+1]]) == 0:   
                                Allresult[count] = 'Not Check'
                            count+=1
                    TimescanDMC = str(datetime.datetime.now())[:-3]
                    ET_DMC.config(text=DMC)
                    for idx in range(sokenh):
                        ET_A_min[idx].config(text="",bg="#ffffff")
                        ET_A_max[idx].config(text="",bg="#ffffff")
                    LB_ERROR.config(text="Chờ kết quả đo "+mahang,
                                    background="#ffff00")
                else:
                    LB_ERROR.config(text="Mã không đúng số lượng: " +
                                    str(data[:-1]), background="#ff0000")
            else:
                if kq == DMC:
                    savedata2("OK","OK")                    
                    rsvariable()
                else:
                    savedata2("Return","NG")
                    if len(kq) == 29:     
                        mahang = check_mahang(kq)                        
                        rsvariable()
                        DMC = kq
                        product_file = pd.read_csv("product.csv",index_col=0)
                        count = 0
                        for idx in range(12):
                            print(product_file.columns[idx+1])
                            print(Channel)
                            if str(product_file.columns[idx+1]) in Channel:
                                print(product_file.loc[mahang,product_file.columns[idx+1]])
                                if int(product_file.loc[mahang,product_file.columns[idx+1]]) == 0:   
                                    Allresult[count] = 'Not Check'
                                count+=1
                        TimescanDMC = str(datetime.datetime.now())[:-3]
                        ET_DMC.config(text=DMC)
                        for idx in range(sokenh):
                            ET_A_min[idx].config(text="",bg="#ffffff")
                            ET_A_max[idx].config(text="",bg="#ffffff")
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

# XONG
# Show thông tin cho biết kết quả của con hàng sau khi đo là gì? OK/NG/Special/Return
# Lưu dữ liệu gồm Machine, Product_Name, Time_ScanDMC, TimeFinish, DMC, Result, PingRing vô bảng AirGauge
def savedata2(result,pinring):   
    try: 
        if result == "OK":
            LB_ERROR.config(
                text="Kết quả đo OK", background="#00ff00")
        elif result == 'Special':
            LB_ERROR.config(
                text="Kết quả đo Special", background="#ffff00") 
        elif result == "Return":
            LB_ERROR.config(
                text="Trả Sửa", background="#00ff00")
        else:
            LB_ERROR.config(
                text="Kết quả đo NG", background="#ff0000") 
        conn = pyodbc.connect(
                'Driver={SQL Server}; Server=192.168.8.21; Database=QC; UID=sa; PWD=1234; Trusted_Connection=No;')
        cursor = conn.cursor()
        may = ''
        value = f"'{machine}','{mahang}','{str(datetime.datetime.now())[:-3]}','{str(datetime.datetime.now())[:-3]}','{DMC}'"
        for i in range(sokenh):
            may += f',[{i+1}_Title],[{i+1}_Type],[{i+1}_Min],[{i+1}_Max]'
            value += f",'{title[i]}','{Type[i]}','{vMin[i]}','{vMax[i]}'"
        value+= f",'{result}','{pinring}'"
        cmd = "  insert into airgauge ([Machine],[Product_Name],[Time_ScanDMC],[TimeFinish],[DMC]"+may+",[Result],[PinRing]) values ("+value+")"
        print(cmd)
        cursor.execute(cmd)
        cursor.commit()
        savedata(DMC,vMin[0],vMax[0],vMin[1],vMax[1],result,TimescanDMC)
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        LB_ERROR.config(
            text="Lưu giá trị thất bại", background="#ff0000")

# Đọc dữ liệu từ việc đo thông số từ 2 cổng đo A, B (Một lần đọc)
def read_meter():
    # Hàm này là hàm chính nè, sau này mình sửa sửa hàm này là chính để thêm kênh 
    global DMC, Allresult, vMin, vMax, recheck, count
    try:
        if not meter_ser.is_open:
            meter_ser.open()
            LB_ERROR.configure(background="#00ff00", text="Kết nối thiết bị đo")
        if DMC != None:
            # Truyền ký hiệu D để ra hiệu là chuẩn bị đọc dữ liệu
            meter_ser.write("D".encode())
            bytesToRead = meter_ser.inWaiting()
            # Đọc các giá trị từ 2 lỗ khí (tương đương với 2 cổng đo A, B)
            data = meter_ser.read(bytesToRead)
            # Dữ liệu chắc là liên tục nhưng được ngăn cách bởi dấu ' nên split trước, nhưng tại sao lại chọn giá trị thứ 2 rồi slipt nữa?? 
            lstdata = str(data).split("'")[1].split() # Dữ liệu tinh gọn của dữ liệu đọc được từ máy đo kín khí
            if len(lstdata)!=0: # Nếu đọc dữ liệu thành công
                for idx in range(sokenh): # Chạy qua từng kênh
                    for i in range(len(lstdata)): # Khi độ dài lstdata đã > 0 thì duyệt qua từng phần tử
                        # Với điều kiện này là kênh từ trong dữ liệu đọc được = Kênh mà mình đã lưu và giá trị của AllReslut của kênh này khác Not Check 
                        # (Chính là giá trị 0 trong file product.csv, ví dụ trong file 1 mã đầu được check bởi cả 2 kênh ACH, BCH còn 2 mã bên dưới chỉ 
                        # được check bởi 1 trong 2 kênh ACH hoặc BCH)
                        if lstdata[i]==Channel[idx].upper() and Allresult[idx] != 'Not Check':
                            # Vậy gán Dvalue (giá trị đường kính của kênh lstdata[i])
                            Dvalue[idx] = float(lstdata[i+1][:-2])
                            # Nếu giá trị đường kính nhỏ hơn Threshold của kênh đó 
                            if Dvalue[idx] < Allthresh[idx]:
                                # Nếu mà count[idx] < 3 thì chỉ cần + 1 là xong mà chưa đưa vào 
                                if count[idx] < 3: # Set giá trị này để loại bỏ 3 giá trị đầu tiên khi bắt đầu nhận giá trị đường kính < Threshold
                                    count[idx]+=1
                                else:
                                # Khi đã bỏ đủ 3 giá nhiễu ban đầu
                                    # Ngược lại, nếu count[idx] = 3
                                    # Nếu trong TH count [idx] = 3 thì phải kiểm tra lại
                                    LB_ERROR.config(
                                            text="Đang kiểm tra", background="#00ff00")
                                    
                                    # Thêm giá trị đường kính mới vào lstvalue
                                    lstvalue[idx].append(Dvalue[idx])
                                    print(lstvalue)

                                    # Nếu mà số phần tử của lstvalue[idx] lớn hơn 2 (tức là  từ 3 trở lên)
                                    if len(lstvalue[idx])>2:
                                        vMin[idx] = min(lstvalue[idx])
                                        vMax[idx] = max(lstvalue[idx])
                                        print(vMax,vMin)

                                        # Nếu đã từ 3 phần tử trở lên thì sẽ show min max của các giá trị đo lên
                                        ET_A_min[idx].config(text=vMin[idx])                            
                                        ET_A_max[idx].config(text=vMax[idx])

                                        # Nếu giá trị max > special high -> cút luôn
                                        if vMax[idx] > Allhigh[idx]:
                                            ET_A_max[idx].config(bg="#ff0000")
                                            LB_ERROR.config(
                                                text="Dữ liệu NG", background="#ff0000") 
                                        # Còn nếu giá trị max > giá trị max yêu cầu
                                        elif vMax[idx] > Allmax[idx]:
                                            ET_A_max[idx].config(bg="#ffff00")
                                        # Còn nếu giá trị min < special low -> cút luôn
                                        if vMin[idx] < Alllow[idx]:
                                            ET_A_min[idx].config(bg="#ff0000")
                                            LB_ERROR.config(
                                                text="Dữ liệu NG", background="#ff0000") 
                                        # Nếu giá trị min < giá trị min yêu cầu
                                        elif vMin[idx] < Allmin[idx]:
                                            ET_A_min[idx].config(bg="#ffff00")

                            # Nếu giá trị đường kính lớn hơn Threshold của kênh đó 
                            # Nếu mà count[idx] > 0
                            elif count[idx] > 0:
                                # Thì oke thôi, bắt đầu trừ - 1
                                count[idx]-=1

                                # Trừ cho tới khi nào count[idx] = 0 và số lượng phần tử trong danh sách phàn tử > 5
                                if count[idx] == 0 and len(lstvalue[idx])>5:

                                    # Nếu giá trị min < special low
                                    # Xét các điều kiện như trong hình vẽ trên zalo
                                    if vMin[idx] < Alllow[idx]:
                                        if Type[idx] == "ID" and waitsave[idx] and Allresult[idx] != 'NG':
                                            recheck = True
                                            Allresult[idx] = ''
                                            waitsave[idx] = False
                                        else:
                                            Allresult[idx] = 'NG'
                                    if vMax[idx] > Allhigh[idx]:
                                        if Type[idx] == "OD" and waitsave[idx] and Allresult[idx] != 'NG':
                                            recheck = True
                                            Allresult[idx] = ''
                                            waitsave[idx] = False
                                        else:
                                            Allresult[idx] = 'NG'
                                    elif vMin[idx] < Allmin[idx] or vMax[idx] > Allmax[idx]:
                                        Allresult[idx] = 'Special'
                                    else:
                                        Allresult[idx] = 'OK'
                                    if None in Allresult:
                                        pass
                                    else:
                                        if not recheck or 'NG' in Allresult:
                                            if 'NG' in Allresult:
                                                result = 'NG'
                                            elif 'Special' in Allresult:
                                                result = 'Special'
                                            else:
                                                result = 'OK'   
                                            savedata2(result,"")
                                            rsvariable()
                                        else:
                                            LB_ERROR.config(
                                                text="Kiểm tra lại Pin/Ring", background="#ff0000") 
                                            
    # Suy cho cùng, count[idx] sẽ không bao giờ vượt quá 3, khi nó đạt tới 3 thì bắt đầu 
    except:
        Systemp_log(traceback.format_exc()).append_new_line()
        meter_ser.close()
        LB_ERROR.configure(background="#ff0000",
                           text="Mất kết nối thiết bị đo")
    LB_ERROR.after(300, read_meter)

# XONG
# Xác nhận các thông số A_title, B_title, const_Alow, const_Amin, const_Bmin, const_Amax, const_Bmax, const_Athresh, const_Bthresh, const_Ahigh
# Hàm này để connect vô giao diện chính để thao tác đọc và xử lý dữ liệu từ máy đo đường kính bằng kín khí
# Mục đích chính là với những kênh đang được sử dụng thì sẽ lưu dữ liệu vào các mảng sau
    # + Channel: danh sách chứa các kênh đang được sử dụng
    # + Allmin: danh sách chứa toàn bộ giá trị min của từng kênh
    # + Allmax: danh sách chứa toàn bọ giá trị max của từng kênh
    # + Type: danh sách chứa toàn bộ loại đường kính cần đo của từng kênh
    # + title: danh sách chứa toàn bộ tên hiển thị của từng kênh 
    # + Allthresh: danh sách chứa toàn bộ giá trị threshold của từng kênh
    # + Alllow: danh sách chứa toàn bộ giá trị Special Low của từng kênh
    # + Allhigh: danh sách chứa toàn bộ giá trị Special High của từng kênh 
def confirm():
    # Comfirm số kênh, 
    global sokenh, Channel, Allmin, Allmax, Allhigh, Alllow, Allthresh, Type, ready_flag, title
    if not scan_flag:
        messagebox.showerror("Lỗi", "Chưa chọn thiết bị tay scan")
    elif not meter_flag:
        messagebox.showerror("Lỗi", "Chưa chọn thiết bị do")
    else:
        Channel = [] 
        Allmin = []
        Allmax = []
        Type = []
        title = []
        Allthresh = []
        Alllow = []
        Allhigh = []
        for i in range(12):
            if int(config_file.loc[config_file.index[i], "InUsed"])==1:
                Channel.append(config_file.index[i])
                title.append(config_file.loc[config_file.index[i], "Title"])
                Type.append(config_file.loc[config_file.index[i], "Type"])
                Allmin.append(config_file.loc[config_file.index[i], "Min"])
                Allmax.append(config_file.loc[config_file.index[i], "Max"])
                Allthresh.append(config_file.loc[config_file.index[i], "Threshold"])
                Alllow.append(config_file.loc[config_file.index[i], "Special Low"])
                Allhigh.append(config_file.loc[config_file.index[i], "Special High"])

        # Lấy số kênh dựa vào số lượng phần từ của Channel (số lượng kênh đang sử dụng)
        sokenh = len(Channel)
        selectcom.destroy()
        ready_flag = True

# XONG, KHÔNG CẦN QUAN TÂM
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

# Kết nối với đồng hồ đo kín khí (kênh A, B, C)
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

# Tạo list_port là danh sách các port hiện đang kết nối với PC
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

if not ready_flag:
    exit()

# Hàm này dùng để làm gì -> Để reset lại các biến 
def rsvariable():
    # Khởi tạo waitesave, Dvalue, count, lstvalue, vMax, vMin, recheck, coutr
    global waitsave, Dvalue, count, lstvalue, vMin, vMax, Allresult, recheck, count, DMC
    DMC = None
    waitsave = [True]*sokenh
    Dvalue = [None]*sokenh # Đây chính là đường kính đo được mỗi lần đọc
    count = [0]*sokenh
    lstvalue = []
    vMax = []
    vMin = []
    for i in range(sokenh):
        lstvalue.append([])
        vMin.append([])
        vMax.append([])
    Allresult = [None]*sokenh
    recheck = False
    count = [0]*sokenh

rsvariable() # viết tắt của reset variable

# Giao diện chính của chương trình đo đường kính bằng kín khí
machine = "TEST"
wk = Tk()
height = max(295+45*sokenh,475)
wk.geometry("800x"+str(height)+"+1770+220")
wk.resizable(False,False)
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

check_connect()
read_scanner()
read_meter()
wk.mainloop()
