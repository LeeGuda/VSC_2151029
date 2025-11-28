import queue
import threading
import time
import RPi.GPIO as GPIO
import tm1637

PIN_R = 17
PIN_G = 18
PIN_B = 27
CLK_7_SEG = 3
DIO_7_SEG = 4
BTN_PIN = 22

tm = tm1637.TM1637(clk=CLK_7_SEG, dio=DIO_7_SEG)

digit = [0, 0, 0, 0, 1] 

BUTTON_Q = queue.Queue(3)
LED_Q = queue.Queue(3)
TIMEOUT_Q = queue.Queue(3)
CLOCK_Q = queue.Queue(3)
TIMER_Q = queue.Queue(3)
STOP_WATCH_Q = queue.Queue(3)
STOP_FLAG = threading.Event()
dsp_event = threading.Event()

def setup_gpio():
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(PIN_R, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_G, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PIN_B, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(BTN_PIN, GPIO.IN)

def set_color(r, g, b):

    GPIO.output(PIN_R, r)
    GPIO.output(PIN_G, g)
    GPIO.output(PIN_B, b)

SEG_PTN = {
0: 0b00111111, # 0
1: 0b00000110, # 1
2: 0b01011011, # 2
3: 0b01001111, # 3
4: 0b01100110, # 4
5: 0b01101101, # 5
6: 0b01111101, # 6
7: 0b00000111, # 7
8: 0b01111111, # 8
9: 0b01101111, # 9
10: 0b00000000  # blank
}

def display_task():
    while True: 
        dsp_event.wait()
        
        segments = []
        for i in range(4):
            num_val = digit[i]
            pattern = SEG_PTN.get(num_val, 0b00000000)
            segments.append(pattern)
        
        if len(digit) > 4 and digit[4] == 1:
            segments[1] |= 0x80 
        
        try:
            tm.write(segments)
        except Exception as e:
            pass
            
        dsp_event.clear()
        
        if STOP_FLAG.is_set():
            break
def colon_blink_task():
    
    while not STOP_FLAG.is_set():
        # 콜론 상태 토글
        digit[4] = 1 if digit[4] == 0 else 0 
        
        # display_task 깨우기
        dsp_event.set()
        
        # 0.5초 대기 (1초 주기의 점멸 효과)
        time.sleep(0.5)

def button_task():
    # 초기값 정의
    button_status_old = GPIO.input(BTN_PIN)
    rising_edge = 0
    falling_edge = 0
    key_timer_on = 0
    key_timer = 0
    key_hold_time = 0
    long_key = 0
    toggle_cnt = 0
    LONG_PRESS_THRESHOLD = 15  # 1.5초 이상이면 롱키

    while True:
        # 현재 버튼 상태 읽기
        button_status = GPIO.input(BTN_PIN)

        
        # 0(눌림), 1(안눌림)으로 판정
        if button_status_old == 1 and button_status == 0:
            # 버튼이 눌림 (Falling Edge)
            falling_edge = 1
            rising_edge = 0
        elif button_status_old == 0 and button_status == 1:
            # 버튼이 떼짐 (Rising Edge)
            rising_edge = 1
            falling_edge = 0
        else:
            rising_edge = 0
            falling_edge = 0

        # 스위치 상태 저장
        def button_task():
            # 초기값 정의
            button_status_old = GPIO.input(BTN_PIN)  # 이전 버튼 상태
            rising_edge = 0
            falling_edge = 0
            key_timer_on = 0
            key_timer = 0
            key_hold_time = 0
            long_key = 0
            toggle_cnt = 0
            LONG_PRESS_THRESHOLD = 15  # 1.5초 이상이면 롱키

            while True:
                # 버튼 상태 읽기
                button_status = GPIO.input(BTN_PIN)

                # #스위치엣지 판정
                if button_status_old == 0 and button_status == 1:
                    # Rising edge: 버튼이 눌림(0) → 안눌림(1)
                    rising_edge = 1
                    falling_edge = 0
                elif button_status_old == 1 and button_status == 0:
                    # Falling edge: 버튼이 안눌림(1) → 눌림(0)
                    falling_edge = 1
                    rising_edge = 0
                else:
                    rising_edge = 0
                    falling_edge = 0

                # #스위치상태 저장
                button_status_old = button_status

                # #키홀드 타이머 (버튼이 떼질 때까지 누른 시간)
                if rising_edge == 1:
                    key_hold_time += 1

                # #스위치 Off (버튼 눌림)
                if falling_edge == 1:
                    falling_edge = 0
                    key_timer_on = 1
                    key_timer = 0
                    key_hold_time = 0
                    toggle_cnt += 1
                    long_key = 1

                # #연속키 타이머 (버튼이 눌린 후 타이머 동작)
                if key_timer_on == 1:
                    key_timer += 1

                # #연속 Key 타임 아웃(1.5초)
                if key_timer_on == 1 and key_timer >= LONG_PRESS_THRESHOLD:
                    key_timer_on = 0
                    key_timer = 0

                    # #타이머Stop 및 결과출력
                    if long_key == 1:
                        BUTTON_Q.put(('LONG', 1))  # 롱키 메시지
                        long_key = 0
                    else:
                        if toggle_cnt == 1:
                            BUTTON_Q.put(('KEY', 1))  # 단일키 메시지
                        elif toggle_cnt >= 2:
                            BUTTON_Q.put(('Double_Key', 1))  # 더블키 메시지
                        toggle_cnt = 0

                # #stop_task On이면 종료
                if STOP_FLAG.is_set():
                    break

                # #센서확인 (100ms 대기)
                time.sleep(0.1)

def timer_task():
    is_visible = False
    is_running = False
    is_timeout = False
    remaining = 180 
    
    while not STOP_FLAG.is_set():
        if not TIMER_Q.empty():
            cmd = TIMER_Q.get()
            
            if cmd == 'ON': 
                is_visible = True
            elif cmd == 'OFF': 
                is_visible = False
            elif cmd == 'KEY': 
                if is_timeout: pass
                elif is_running: is_running = False 
                else: is_running = True 
            elif cmd == 'Double_Key':
                remaining = 180 
                is_timeout = False
                is_running = False
                TIMEOUT_Q.put('OFF')
                
        if is_running and remaining > 0:
            remaining -= 1 
            
            if remaining == 0:
                is_running = False 
                is_timeout = True
                TIMEOUT_Q.put('ON') 

        if is_visible:
            mins = remaining // 60
            secs = remaining % 60

            digit[0] = 10 
            digit[1] = mins 
            digit[2] = secs // 10
            digit[3] = secs % 10
            
            time.sleep(0.01) 
            
        time.sleep(1)
        
        if STOP_FLAG.is_set():
            break
