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
    event_thread_stop()
    
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
F_F_q = queue.Queue(3) # Fill Full 메세지 Q (Analysis -> Step_Control)
N_C_q = queue.Queue(3) # New Count 메세지 Q (Count_Scan -> Analysis)
P_O_q = queue.Queue(3) # Pack On 메세지 Q (Step_Control -> Print_Packing)
P_E_q = queue.Queue(3) # Pack End 메세지 Q (Print_Packing -> Step_Control)
D_S_q = queue.Queue(3) # Drop_Sig 메세지 Q (Count_Scan -> Load_Data_Scan)
# D_R_q = queue.Queue(3) # Data_Req 메세지 Q (요구사항에 있었으나 W_D_q로 대체)
W_D_q = queue.Queue(3) # Weight Data Q (Load_Data_Scan -> Analysis)

# ---- 공유 데이터 접근을 위한 Lock
data_lock = threading.Lock()

# ---- Task : Step_Control (메인 제어 상태 머신)
def Step_Control():
    global Conveyor_Switch, Weight_Sum, Count_Sum
    state = 'IDLE' # 상태: 'IDLE', 'FILLING', 'PACKING'
    print('Step_Control Task START!!')
    
    while not event_thread_stop.is_set() :
        if state == 'IDLE':
            # 1. IDLE 상태: 초기화 및 충진 시작
            print('Control: State -> IDLE. Resetting and starting FILLING.')
            # 합계 초기화
            with data_lock:
                Weight_Sum = 0
                Count_Sum = 0
            
            # 다음 상태로 전이 및 컨베이어 가동
            state = 'FILLING'
            Conveyor_Switch = True 
            print('Control: State -> FILLING. Conveyor ON.')

        elif state == 'FILLING':
            # 2. FILLING 상태: 박스가 다 찼다는 신호(F_F_q) 대기
            try:
                msg = F_F_q.get(timeout=0.1) # 0.1초 타임아웃
                
                if msg == 'Box_Full':
                    print('Control: Box Full detected! State -> PACKING.')
                    Conveyor_Switch = False # 컨베이어 정지
                    
                    # 포장 태스크(Print_Packing)에 라벨 정보와 함께 포장 명령
                    with data_lock:
                        label = f'{Weight_Sum}g / {Count_Sum}개'
                    P_O_q.put(['Pack On', label])
                    
                    state = 'PACKING' # 포장 상태로 전이

            except queue.Empty:
                pass # 메시지 없으면 계속 FILLING 상태 유지 (및 종료 신호 확인)

        elif state == 'PACKING':
            # 3. PACKING 상태: 포장 완료 신호(P_E_q) 대기
            try:
                msg = P_E_q.get(timeout=0.1) # 0.1초 타임아웃
                
                if msg == 'Pack_End':
                    print('Control: Pack End detected! State -> IDLE.')
                    state = 'IDLE' # 초기화 및 다음 작업을 위해 IDLE 상태로 전이
                    
            except queue.Empty:
                pass # 메시지 없으면 계속 PACKING 상태 유지 (및 종료 신호 확인)

    Conveyor_Switch = False # 스레드 종료 시 컨베이어 확실히 정지
    print('\nStep_Control Task END!!')

# ---- Task : Analysis_Process (데이터 분석 및 합산)
def Analysis_Process():
    global Weight_Sum, Count_Sum
    print('Analysis_Process Task START!!')
    
    while not event_thread_stop.is_set():
        try:
            # 1. 카운트 신호(N_C_q) 대기
            N_C_q.get(timeout=0.1)
            
            # 2. 카운트 신호 수신 시, 무게 데이터(W_D_q) 대기
            try:
                weight = W_D_q.get(timeout=0.5) # 카운트 후 0.5초 내 무게 데이터가 와야 함
                
                # 3. 데이터 합산 (Lock 사용)
                with data_lock:
                    Weight_Sum += weight
                    Count_Sum += 1
                    print(f'Analysis: New Apple. Weight: {weight}, Total: {Weight_Sum}g, {Count_Sum}개')
                
                # 4. 최대 무게 검사
                if Weight_Sum >= MAX_WEIGHT:
                    print(f'Analysis: MAX_WEIGHT Reached! Sending Box_Full')
                    F_F_q.put('Box_Full') # Step_Control로 박스 다 찼음 신호
            
            except queue.Empty:
                # 카운트는 되었으나 무게 데이터가 시간 내 오지 않음 (에러)
                print('Analysis Error: Count received, but no weight data!')

        except queue.Empty:
            pass # 카운트 신호 없음, 루프 계속

    print('\nAnalysis_Process Task END!!')

# ---- Task : Count_Switch_Scan (포토커플러 상태 스캔)
def Count_Switch_Scan():
    old_status = False
    print('Count_Switch_Scan Task START!!')
    
    while not event_thread_stop.is_set():
        global Photocoupler_Status # 전역 I/O 변수
        current_status = Photocoupler_Status
        
        # Rising Edge 감지 (False -> True)
        if current_status == True and old_status == False:
            print('Scan: Photocoupler HIGH (Apple Detected)')
            N_C_q.put('New_Count') # Analysis_Process 태스크로 신호
            D_S_q.put('Get_Weight')  # Load_Data_Scan 태스크로 신호
        
        old_status = current_status
        time.sleep(0.01) # 10ms 스캔 주기

    print('\nCount_Switch_Scan Task END!!')

# ---- Task : Load_Data_Scan (전자저울 데이터 스캔)
def Load_Data_Scan():
    print('Load_Data_Scan Task START!!')
    
    while not event_thread_stop.is_set():
        try:
            # 1. 스캔 시작 신호(D_S_q) 대기 (from Count_Switch_Scan)
            D_S_q.get(timeout=0.1)
            
            # 2. 저울 데이터(Scale_Data)가 0이 아닐 때(측정값 발생)까지 대기
            print('Scan: Waiting for Scale Data...')
            start_time = time.time()
            weight = 0
            while time.time() - start_time < 1.0: # 1초 타임아웃
                global Scale_Data
                if Scale_Data > 0:
                    weight = Scale_Data
                    break
                time.sleep(0.01)
            
            # 3. 측정된 무게 데이터를 Analysis_Process로 전송
            if weight > 0:
                print(f'Scan: Scale Data Loaded: {weight}')
                W_D_q.put(weight)
            else:
                # 1초 내에 저울 값이 안 들어옴 (에러)
                print('Scan Error: Timed out waiting for scale data')
                
        except queue.Empty:
            pass # 스캔 신호 없음, 루프 계속

    print('\nLoad_Data_Scan Task END!!')

# ---- Task : Print_Packing (포장기 인터페이스)
def Print_Packing():
    print('Print_Packing Task START!!')
    
    while not event_thread_stop.is_set():
        try:
            # 1. 포장 시작 메시지(P_O_q) 대기 (from Step_Control)
            pack_cmd = P_O_q.get(timeout=0.1) # ex: ['Pack On', 'label']
            
            # 2. I/O 장치(Packer)로 메시지 전송
            print(f'Packing: Sending command to Packer I/O: {pack_cmd[1]}')
            Pack_Message.put(pack_cmd)
            
            # 3. I/O 장치(Packer)로부터 완료 메시지(Pack_Return_Message) 대기
            try:
                ret_msg = Pack_Return_Message.get(timeout=10.0) # 포장시간(7초) + 여유
                if ret_msg == 'Pack_End':
                    print('Packing: Received Pack_End from I/O')
                    P_E_q.put('Pack_End') # Step_Control로 완료 신호
                
            except queue.Empty:
                print('Packing Error: Timed out waiting for Pack_End response')
                
        except queue.Empty:
            pass # 포장 명령 없음, 루프 계속

    print('\nPrint_Packing Task END!!')


# ---- Task : Display_Out (기존 코드)
def Display_Out():
    global Weight_Sum # ### Share Variable
    global Count_Sum # ### Share Variable
    print('Display_Out Task START!!')
    
    while not event_thread_stop.is_set() :
        # Lock을 사용하여 데이터 읽기
        with data_lock:
            msg = str(Weight_Sum)+'g, ' +str(Count_Sum)+'개'
            
        try:
            Display_Message.put(msg, timeout=0.1) # 큐가 꽉 찼을 경우 대비
        except queue.Full:
            pass
            
        time.sleep(0.2) # Refresh time
        
    print('\nDisplay_Out Task END!!')

# ---- 제어 태스크들 시작 ----
Task_Step_Control = threading.Thread(target=Step_Control)
Task_Step_Control.start()

Task_Analysis_Process = threading.Thread(target=Analysis_Process)
Task_Analysis_Process.start()

Task_Count_Switch_Scan = threading.Thread(target=Count_Switch_Scan)
Task_Count_Switch_Scan.start()

Task_Load_Data_Scan = threading.Thread(target=Load_Data_Scan)
Task_Load_Data_Scan.start()

Task_Print_Packing = threading.Thread(target=Print_Packing)
Task_Print_Packing.start()

Task_Display_Out = threading.Thread(target=Display_Out)
Task_Display_Out.start()

# ***** 프로그램관리 Task & 메인루틴 *****
# 'Stop' 버튼(ending 함수)이 호출되면 event_thread_stop을 세팅하고
# admin_Task를 시작하여 모든 스레드를 join하고 GUI를 종료합니다.
def ending():
    print('\nStop button pressed. Setting stop event...')
    event_thread_stop.set() # 모든 스레드에 종료 신호
    admin_Task.start() # 종료 처리 스레드 시작
    
btn2 = Button(tk, text='Stop', bg='gray', fg='white', command=ending).grid(row=14, column=2)

def admin():
    # 이 태스크는 ending() 함수에 의해 시작됩니다.
    print('Admin Task: Waiting for all threads to join...')
    
    # -----Control Treads 종료 join-----
    Task_Step_Control.join()
    Task_Analysis_Process.join()
    Task_Count_Switch_Scan.join()
    Task_Load_Data_Scan.join()
    Task_Print_Packing.join()
    Task_Display_Out.join()
    print('Admin Task: Control tasks joined.')
    
    # -----I/O Treads 종료 join-----
    # I/O 스레드들이 큐.get()에서 블록킹 해제되도록
    # 각 큐에 더미 데이터를 넣어줄 수 있으나,
    # 여기서는 event_thread_stop 체크 로직에 의존합니다.
    # (Counter, Scale 스레드는 event.set()이 필요할 수 있음)
    event_drop.set()
    event_scale.set()
    Display_Message.put('Shutdown')
    Pack_Message.put(['Shutdown', ''])
    
    IOTask_Packer.join()
    IOTask_Counter.join()
    IOTask_Conveyor.join()
    IOTask_Display.join()
    IOTask_Scale.join()
    print('Admin Task: I/O tasks joined.')
    
    print('\nAdmin Task END!! All threads stopped. Destroying GUI.')
    tk.destroy()

admin_Task = threading.Thread(target=admin)
# admin_Task.start() # <-- 여기서 시작하지 않고 ending()에서 시작

tk.mainloop()