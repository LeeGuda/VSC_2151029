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
Str_conveyor_status.set('정지') # 초기값 설정

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
    data = entry1.get()
    try:
        number_apples = number_apples + int(data)
        Str_apples_remained.set(str(number_apples)) # '투입'은 메인스레드에서 실행되므로 안전
    except ValueError:
        print("숫자만 입력하세요.")

btn1 = Button(tk, text='투입', bg='black', fg='white', command=insert_apples).grid(row=1, column=2)

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
event_admin_finished = threading.Event() # ★★★ admin이 종료를 알리기 위한 새 이벤트 ★★★

# 쓰레드 컨베이어 장치
Load_Flag = False # IO_Variable
Conveyor_Switch = False # False: Off / True: On
event_drop = threading.Event()
number_apples = 0

# --- GUI 업데이트를 위한 전역 변수 (스레드 -> 메인) ---
g_conveyor_status = '정지'
g_load_status = 'Empty'
g_counter_status = '0'
g_display_message = '--- kg / --- 개'
g_print_label = '----------'
g_packer_status = '대기중'

def Conveyor():
    global number_apples, Conveyor_Switch, Load_Flag
    global g_conveyor_status, g_load_status # GUI 변수
    
    while not event_thread_stop.is_set() :
        if number_apples > 0 :
            Load_Flag = True
            g_load_status = 'Loaded' # Str_load_status.set() 대신 사용
        else :
            Load_Flag = False
            g_load_status = 'Empty' # Str_load_status.set() 대신 사용

        if Conveyor_Switch == True : # 컨베이어 가동
            g_conveyor_status = '가동' # Str_conveyor_status.set() 대신 사용
            time.sleep(0.3) # 벨트 투입 시간 모사
            if event_thread_stop.is_set(): break # sleep 후 체크
            
            if number_apples > 0 :
                number_apples -= 1
                
                time.sleep(1.5) # 벨트 전송시간 모사
                if event_thread_stop.is_set(): break # sleep 후 체크
                
                event_drop.set() # 계수스위치(Counter) 가동
        else :
            g_conveyor_status = '정지' # Str_conveyor_status.set() 대신 사용
            time.sleep(0.1)

    print('\nI/O_Conveyor Task END!!')

IOTask_Conveyor = threading.Thread(target=Conveyor)
IOTask_Conveyor.start()

# 쓰레드 계수용 스위치(포토커플러)
Photocoupler_Status = False 
event_scale = threading.Event()
def Counter():
    global Photocoupler_Status, g_counter_status # GUI 변수
    
    while not event_thread_stop.is_set() :
        # event_drop 대기 (0.1초 타임아웃)
        if not event_drop.wait(timeout=0.1): 
            continue # 타임아웃 시 event_thread_stop 다시 체크
        
        if event_thread_stop.is_set() : break # wait() 직후에도 체크
        event_drop.clear()
        
        # -- puls 발생 : Photocoupler_Status
        g_counter_status = '1' 
        Photocoupler_Status = True
        time.sleep(0.1) # pulse time 모사(100mSec)
        if event_thread_stop.is_set() : break # sleep 후 체크
        
        g_counter_status = '0' 
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
        # event_scale 대기 (0.1초 타임아웃)
        if not event_scale.wait(timeout=0.1): 
            continue # 타임아웃 시 event_thread_stop 다시 체크
        
        if event_thread_stop.is_set() : break # wait() 직후에도 체크
        event_scale.clear()

        Scale_Data = 80 + random.randint(1, 70) # 측정 모사 (80 ~ 150g 발생)
        
        time.sleep(0.5) # 저울 값 유지시간 모사
        if event_thread_stop.is_set() : break # sleep 후 체크
        
        Scale_Data = 0

    print('\nI/O_Scale Task END!!')

IOTask_Scale = threading.Thread(target=Scale)
IOTask_Scale.start()

# Shared Data Variable
Weight_Sum = 0
Count_Sum = 0

# 쓰레드 포장기(Packer)
Pack_Message = queue.Queue(5)
Pack_Return_Message = queue.Queue(5)
def Packer():
    global g_print_label, g_packer_status # GUI 변수
    
    while not event_thread_stop.is_set() :
        try:
            message = Pack_Message.get(timeout=0.1) # 0.1초 타임아웃
            
            if message[0] == 'Pack On' :
                g_print_label = message[1] 
                g_packer_status = '포장중' 
                
                # time.sleep(7)을 쪼개서 종료 신호를 자주 확인
                for _ in range(70):
                    time.sleep(0.1)
                    if event_thread_stop.is_set(): break
                if event_thread_stop.is_set(): break
                
                g_packer_status = '포장완료' 
                time.sleep(1)
                if event_thread_stop.is_set(): break
                
                g_packer_status = '대기중' 
                g_print_label = "----------" 
                Pack_Return_Message.put('Pack_End')
            
            elif message[0] == 'Shutdown':
                break # 종료 신호 처리
                
        except queue.Empty:
            pass # 0.1초 타임아웃 시 루프 처음으로 돌아가 event_thread_stop 체크

    print('\nI/O_Packer Task END!!')

IOTask_Packer = threading.Thread(target=Packer)
IOTask_Packer.start()

# -------------------- 이하 탐과제 작성 영역 --------------------

MAX_WEIGHT = 1 * 1000 # 1KG

# ---- Tasks Queue 정의
F_F_q = queue.Queue(3) 
N_C_q = queue.Queue(3) 
P_O_q = queue.Queue(3) 
P_E_q = queue.Queue(3) 
D_S_q = queue.Queue(3) 
W_D_q = queue.Queue(3) 

data_lock = threading.Lock()

# ---- Task : Step_Control (메인 제어 상태 머신)
def Step_Control():
    global Conveyor_Switch, Weight_Sum, Count_Sum
    state = 'IDLE' 
    print('Step_Control Task START!!')
    
    while not event_thread_stop.is_set() :
        if state == 'IDLE':
            print('Control: State -> IDLE. Resetting and starting FILLING.')
            with data_lock:
                Weight_Sum = 0
                Count_Sum = 0
            
            state = 'FILLING'
            Conveyor_Switch = True 
            print('Control: State -> FILLING. Conveyor ON.')

        elif state == 'FILLING':
            try:
                msg = F_F_q.get(timeout=0.1) 
                
                if msg == 'Box_Full':
                    print('Control: Box Full detected! State -> PACKING.')
                    Conveyor_Switch = False 
                    
                    with data_lock:
                        label = f'{Weight_Sum}g / {Count_Sum}개'
                    P_O_q.put(['Pack On', label])
                    
                    state = 'PACKING' 

            except queue.Empty:
                pass 

        elif state == 'PACKING':
            try:
                msg = P_E_q.get(timeout=0.1) 
                
                if msg == 'Pack_End':
                    print('Control: Pack End detected! State -> IDLE.')
                    state = 'IDLE' 
                    
            except queue.Empty:
                pass 

    Conveyor_Switch = False 
    print('\nStep_Control Task END!!')

# ---- Task : Analysis_Process (데이터 분석 및 합산)
def Analysis_Process():
    global Weight_Sum, Count_Sum
    print('Analysis_Process Task START!!')
    
    while not event_thread_stop.is_set():
        try:
            N_C_q.get(timeout=0.1)
            
            try:
                weight = W_D_q.get(timeout=0.5) 
                
                with data_lock:
                    Weight_Sum += weight
                    Count_Sum += 1
                    print(f'Analysis: New Apple. Weight: {weight}, Total: {Weight_Sum}g, {Count_Sum}개')
                
                if Weight_Sum >= MAX_WEIGHT:
                    while not F_F_q.empty(): F_F_q.get() # 큐 비우기
                    F_F_q.put('Box_Full') 
            
            except queue.Empty:
                print('Analysis Error: Count received, but no weight data!')

        except queue.Empty:
            pass 

    print('\nAnalysis_Process Task END!!')

# ---- Task : Count_Switch_Scan (포토커플러 상태 스캔)
def Count_Switch_Scan():
    old_status = False
    print('Count_Switch_Scan Task START!!')
    
    while not event_thread_stop.is_set():
        global Photocoupler_Status
        current_status = Photocoupler_Status
        
        if current_status == True and old_status == False:
            print('Scan: Photocoupler HIGH (Apple Detected)')
            N_C_q.put('New_Count') 
            D_S_q.put('Get_Weight') 
        
        old_status = current_status
        time.sleep(0.01) 

    print('\nCount_Switch_Scan Task END!!')

# ---- Task : Load_Data_Scan (전자저울 데이터 스캔)
def Load_Data_Scan():
    print('Load_Data_Scan Task START!!')
    
    while not event_thread_stop.is_set():
        try:
            D_S_q.get(timeout=0.1)
            
            print('Scan: Waiting for Scale Data...')
            start_time = time.time()
            weight = 0
            while time.time() - start_time < 1.0: 
                global Scale_Data
                if Scale_Data > 0:
                    weight = Scale_Data
                    break
                time.sleep(0.01)
                if event_thread_stop.is_set(): break
            if event_thread_stop.is_set(): break
            
            if weight > 0:
                print(f'Scan: Scale Data Loaded: {weight}')
                W_D_q.put(weight)
            else:
                print('Scan Error: Timed out waiting for scale data')
                
        except queue.Empty:
            pass 

    print('\nLoad_Data_Scan Task END!!')

# ---- Task : Print_Packing (포장기 인터페이스)
def Print_Packing():
    print('Print_Packing Task START!!')
    
    while not event_thread_stop.is_set():
        try:
            pack_cmd = P_O_q.get(timeout=0.1) 
            
            print(f'Packing: Sending command to Packer I/O: {pack_cmd[1]}')
            Pack_Message.put(pack_cmd)
            
            try:
                ret_msg = Pack_Return_Message.get(timeout=10.0) 
                if ret_msg == 'Pack_End':
                    print('Packing: Received Pack_End from I/O')
                    P_E_q.put('Pack_End') 
                
            except queue.Empty:
                print('Packing Error: Timed out waiting for Pack_End response')
                
        except queue.Empty:
            pass 

    print('\nPrint_Packing Task END!!')


# ---- Task : Display_Out (GUI 전역변수 업데이트)
def Display_Out():
    global Weight_Sum, Count_Sum, g_display_message # GUI 변수
    print('Display_Out Task START!!')
    
    while not event_thread_stop.is_set() :
        with data_lock:
            g_display_message = str(Weight_Sum)+'g, ' +str(Count_Sum)+'개'
            
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
is_shutting_down = False

# ★★★ 메인 스레드에서 실행되는 GUI 업데이트 함수 (수정됨) ★★★
def update_gui():
    global is_shutting_down
    
    # 1. admin 스레드가 종료 신호를 보냈는지 확인
    if event_admin_finished.is_set():
        tk.destroy() # 메인 스레드에서 안전하게 GUI 종료
        return

    # 2. 종료가 시작되면(is_shutting_down == True) GUI 업데이트를 멈추고
    #    admin 스레드가 끝났는지 확인(폴링)만 계속함
    if is_shutting_down:
        tk.after(100, update_gui) # 0.1초 후 다시 확인
        return
        
    # 3. (정상 작동 시) 전역 변수를 읽어와서 GUI의 StringVar에 일괄 업데이트
    Str_apples_remained.set(str(number_apples))
    Str_conveyor_status.set(g_conveyor_status)
    Str_load_status.set(g_load_status)
    Str_counter_status.set(g_counter_status)
    Str_scale_var.set(str(Scale_Data))
    Str_display_var.set(g_display_message)
    Str_print_var.set(g_print_label)
    Str_packer_var.set(g_packer_status)
    
    # 4. 100ms (0.1초) 후에 이 함수를 다시 실행
    tk.after(100, update_gui)

def ending():
    global is_shutting_down
    if is_shutting_down: # 중복 실행 방지
        return
    is_shutting_down = True

    print('\nStop button pressed. Setting stop event...')
    event_thread_stop.set() # 모든 스레드에 종료 신호
    admin_Task.start() # 종료 처리 '백그라운드' 스레드 시작
    
btn2 = Button(tk, text='Stop', bg='gray', fg='white', command=ending).grid(row=14, column=2)

def admin():
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
    # 각 스레드가 wait() 또는 get()에서 빠져나오도록 신호를 보냄
    event_drop.set() 
    event_scale.set() 
    Pack_Message.put(['Shutdown', '']) 
    
    IOTask_Packer.join()
    IOTask_Counter.join()
    IOTask_Conveyor.join()
    IOTask_Scale.join()
    print('Admin Task: I/O tasks joined.')
    
    print('\nAdmin Task END!! All threads stopped. Signaling main thread to destroy GUI.')
    
    # ★★★ tk.destroy() 대신 이벤트 설정 (수정됨) ★★★
    event_admin_finished.set() 

admin_Task = threading.Thread(target=admin)

# 'X' 버튼(창 닫기)을 눌렀을 때 ending 함수를 호출하도록 설정
tk.protocol("WM_DELETE_WINDOW", ending)

# ★★★ GUI 폴링 루프 시작 ★★★
tk.after(100, update_gui)

# 메인 GUI 루프 시작
tk.mainloop()