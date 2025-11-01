from tkinter import *
import threading
import time
import random
import queue

# ======================= I/O장치 GUI 구성 =======================

tk = Tk()
tk.title('I/O장치')

# -----GUI_컨베이어-----
# StrVariable
Str_apples_remained = StringVar()
Str_apples_remained.set('----')

Str_conveyor_status = StringVar()

Str_load_status = StringVar()
Str_load_status.set('Empty')

# Label
Partition_line1 = Label(tk, text='===== 이송기 =====', fg='red').grid(row=0, column=0)

Conv_text1 = Label(tk, text='투입할 사과 수량').grid(row=1, column=0)
Conv_text2 = Label(tk, text='트레이에 남은 수량').grid(row=2, column=0)
Conv_text3 = Label(tk, text='컨베이어 동작 상태').grid(row=4, column=0)

Conv_text4 = Label(tk, textvariable=Str_apples_remained).grid(row=2, column=1)
Conv_text5 = Label(tk, textvariable=Str_conveyor_status).grid(row=4, column=1)
Conv_text6 = Label(tk, textvariable=Str_load_status).grid(row=2, column=2)

# Entry
entry1 = Entry(tk)
entry1.grid(row=1, column=1)

# Button
def insert_apples():
    global number_apples
    global Conveyor_Switch
    data = entry1.get()
    number_apples = number_apples + int(data)
    # if number_apples > 0 : Conveyor_Switch = True # 컨베이어 자동 가동
    Str_apples_remained.set(str(number_apples))

btn1 = Button(tk, text='투입', bg='black', fg='white', command=insert_apples).grid(row=1, column=2)

def ending():
    event_thread.stop()
    
btn2 = Button(tk, text='Stop', bg='gray', fg='white', command=ending).grid(row=14, column=2)

# -----GUI 계수용 스위치-----
# StrVariable
Str_counter_status = StringVar()
Str_counter_status.set('0')

# Label
Partition_line2 = Label(tk, text='======= 계수기 =======', fg='red').grid(row=5, column=0)
counter_name = Label(tk, text='포토커플러 상태').grid(row=6, column=0)
counter_status = Label(tk, textvariable=Str_counter_status).grid(row=6, column=1)

# -----GUI 전자저울-----
# StrVariable
Str_scale_var = StringVar()
Str_scale_var.set('--')

# Label
Partition_line3 = Label(tk, text='======= 자동저울 =======', fg='red').grid(row=7, column=0)
scale_name = Label(tk, text='측정값').grid(row=8, column=0)
scale_var = Label(tk, textvariable=Str_scale_var).grid(row=8, column=1)

# -----GUI_디스플레이 장치-----
# StrVariable
Str_display_var = StringVar()
Str_display_var.set('--- kg / --- 개')

# Label
Partition_line4 = Label(tk, text='===== 디스플레이 장치 =====', fg='red').grid(row=9, column=0)
display_name = Label(tk, text='Box중량 및 사과수량').grid(row=10, column=0)
display_text = Label(tk, textvariable=Str_display_var).grid(row=10, column=1)

# -----GUI_포장기-----
# StrVariable
Str_print_var = StringVar()
Str_print_var.set('----------')

Str_packer_var = StringVar()
Str_packer_var.set('대기중')

# Label
Partition_line5 = Label(tk, text='======= 포장 장치 =======', fg='red').grid(row=11, column=0)
print_name = Label(tk, text='라벨프린트').grid(row=12, column=0)
print_text = Label(tk, textvariable=Str_print_var).grid(row=12, column=1)
packer_name = Label(tk, text='포장기 상태').grid(row=13, column=0)
packer_text = Label(tk, textvariable=Str_packer_var).grid(row=13, column=1)

# ==================== 모의 I/O장치 스레드 정의 ====================
event_thread_stop = threading.Event() # thread stop을 위한 event

# 쓰레드 컨베이어 장치
Load_Flag = False # IO_Variable
Conveyor_Switch = False # False: Off / True: On
event_drop = threading.Event()
number_apples = 0

def Conveyor():
    global number_apples
    global Conveyor_Switch # ##### IO_Variable
    global Load_Flag # ##### IO_Variable
    while not event_thread_stop.is_set() :
        if number_apples > 0 :
            Load_Flag = True
            Str_load_status.set('Loaded')
        else :
            Load_Flag = False
            Str_load_status.set('Empty')

        if Conveyor_Switch == True : # 컨베이어 가동
            Str_conveyor_status.set('가동')
            time.sleep(0.3) # 벨트 투입 시간 모사
            if number_apples > 0 :
                number_apples -= 1
                Str_apples_remained.set(str(number_apples)) # 트레이에 나머지 사과
                time.sleep(1.5) # 벨트 전송시간 모사
                event_drop.set() # 계수스위치(Counter) 가동
        else :
            Str_conveyor_status.set('정지')
            time.sleep(0.1)

    print('\nI/O_Conveyor Task END!!')

IOTask_Conveyor = threading.Thread(target=Conveyor)
IOTask_Conveyor.start()

# 쓰레드 계수용 스위치(포토커플러)
Photocoupler_Status = 0
event_scale = threading.Event()
def Counter():
    global Photocoupler_Status # ##### IO_Variable
    number_apples_OLD = 0
    while not event_thread_stop.is_set() :
        while not event_drop.is_set() :
            time.sleep(0.1)
            if event_thread_stop.is_set() : break
        
        event_drop.clear()
        
        # -- puls 발생 : Photocoupler_Status
        Str_counter_status.set('1')
        Photocoupler_Status = True
        time.sleep(0.1) # pulse time 모사(100mSec)
        Str_counter_status.set('0')
        Photocoupler_Status = False
        event_scale.set() # 저울측정개시

    print('\nI/O_Counter Task END!!')

IOTask_Counter = threading.Thread(target=Counter)
IOTask_Counter.start()

# 쓰레드 전자저울
Scale_Data = 0
def Scale():
    global Scale_Data # ### IO_Variable
    while not event_thread_stop.is_set() :
        while not event_scale.is_set() :
            time.sleep(0.1)
            if event_thread_stop.is_set() : break
        
        event_scale.clear()

        Scale_Data = 80 + random.randint(1, 70) # 측정 모사 (80 ~ 150g 발생)
        Str_scale_var.set(str(Scale_Data))
        time.sleep(0.5) # 저울 값 유지시간 모사
        Scale_Data = 0
        Str_scale_var.set(str(Scale_Data))

    print('\nI/O_Scale Task END!!')

IOTask_Scale = threading.Thread(target=Scale)
IOTask_Scale.start()

# Shared Data Variable
Weight_Sum = 0
Count_Sum = 0

# 쓰레드 Display 장치
Display_Message = queue.Queue(5)
def Display():
    while not event_thread_stop.is_set() :
        Str_display_var.set(Display_Message.get()) # Blocking 처리
        time.sleep(0.1) # Display interval time 모사
    print('\nI/O_Display Task END!!')

IOTask_Display = threading.Thread(target=Display)
IOTask_Display.start()

# 쓰레드 포장기(Packer)
Pack_Message = queue.Queue(5)
Pack_Return_Message = queue.Queue(5)
def Packer():
    while not event_thread_stop.is_set() :
        if not Pack_Message.empty() :
            message = Pack_Message.get()
            if message[0] == 'Pack On' :
                Str_print_var.set(message[1]) # 라벨 프린팅
                Str_packer_var.set('포장중')
                time.sleep(7) # 포장시간 모사
                Str_packer_var.set('포장완료')
                time.sleep(1)
                Str_packer_var.set('대기중')
                Str_print_var.set("") # 라벨 프린팅 clear
                Pack_Return_Message.put('Pack_End')
        
        pass

    time.sleep(0.1)
    print('\nI/O_Packer Task END!!')

IOTask_Packer = threading.Thread(target=Packer)
IOTask_Packer.start()

# -------------------- 이하 탐과제 작성 영역 --------------------

# *********** System Interface Variables ***********
# 공유데이터 : Weight_Sum, Count_Sum
# 입출력 I/O : Conveyor_Switch, Load_Flag, Photocoupler_Status
# A/I port : Scale_Data
# UART port : Pack_Message.put(), Pack_Return_Message.put(), Display_Message.put()
# ************* Control Task Area **************
MAX_WEIGHT = 1 * 1000 # 1KG

# ---- Tasks Queue 정의
F_F_q = queue.Queue(3) # Fill Full 메세지 Q
N_C_q = queue.Queue(3) # New Count 메세지 Q
P_O_q = queue.Queue(3) # Pack On 메세지 Q
P_E_q = queue.Queue(3) # Pack End 메세지 Q
D_S_q = queue.Queue(3) # Drop_Sig 메세지 Q
D_R_q = queue.Queue(3) # Data_Req 메세지 Q
W_D_q = queue.Queue(3) # Weight Data Q

# ---- Task : Step_Control
# ---- Task : Analysis_Process
# ---- Task : Count_Switch_Scan
# ---- Task : Load_Data_Scan
# ---- Task : Print_Packing

# ---- Task : Display_Out
def Display_Out():
    global Weight_Sum # ### Share Variable
    global Count_Sum # ### Share Variable
    while not event_thread_stop.is_set() :
        Display_Message.put(str(Weight_Sum)+'g, ' +str(Count_Sum)+'개')
        time.sleep(0.2) # Refresh time
    print('\nDisplay_Out Task END!!')

Task_Display_Out = threading.Thread(target=Display_Out)
Task_Display_Out.start()

# ***** 프로그램관리 Task & 메인루틴 *****
def admin():
    
    event_thread_stop.is_set()
    
    # -----UI treads 종료 join-----
    
    IOTask_Packer.join()
    IOTask_Counter.join()
    IOTask_Conveyor.join()
    IOTask_Display.join()
    IOTask_Scale.join()
    
    # --------------------------------
    
    print('\nadmin Task END!!')
    tk.destroy()

admin_Task = threading.Thread(target=admin)
admin_Task.start()

tk.mainloop()