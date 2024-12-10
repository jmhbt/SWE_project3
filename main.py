import threading
import unittest
from car import Car
from car_controller import CarController
from gui import CarSimulatorGUI

"""
[테스트 담당]

주요 변경사항: 

1.
일단 lock_vehicle(), unlock_vehicle() 에서 트렁크 열고/닫기를 빼고
SOS에 open trunk를 따로 추가했습니다. 
생각해보니 차량 전체 잠금 상태와 트렁크 개폐 여부는 별개로 관리해야 할 것 같아요.

2.
command == "LOCK" 일 때, 모든 문이 닫혀 있을 때 잠금 가능하도록 조건 추가하였습니다.

3. 
주행중일 때 트렁크를 열 수 없도록 수정하였습니다.

4.
관련하여 요구사항 2.2.2, 2.2.6, 3.2.1, 3.2.7에 해당 부분 수정하였습니다.

5. 2,3 번에 대한 테스트 케이스 추가하였습니다.

6. 
command == "LEFT_DOOR_OPEN", "RIGHT_DOOR_OPEN" 일 때
not car_controller.get_right_door_lock() -> car_controller.get_right_door_lock() == "UNLOCKED"로 수정하였습니다.
문 잠금 상태가 boolean이 아니라 문자열로 관리되고 있어서 수정하였습니다.

7.
car의 트렁크 상태가 문자열이 아니라 boolean으로 관리되고 있어서
command == "TRUNK_CLOSE" 일 때
조건 중 car_controller.get_trunk_status() == "OPEN" -> not car_controller.get_trunk_status()로 수정하였습니다.

8.
문이나 트렁크가 열려있는 채로 가속 페달을 밟을시(ACCELERATE) 속도는 올라가지만 경고 메시지를 출력하도록 함수를 하나 만들고 (warn_drive_while_open())
command == "ACCELERATE" 부분을 문이나 트렁크가 하나라도 열려 있으면 경고문을 출력하도록 수정했습니다.
그리고 이와 관련해서 테스트 케이스를 작성했습니다.

9.주행 도중에 엔진이 꺼지지 않는지를 확인하는 테스트 케이스를 작성했습니다.
"""
#추가로할거1113
# a.일정 주행속도 넘어가면 과속경고음 울리는 기능 추가해야함
# 요구사항 문서에도 추가해야함
# 구체적으로 속도 얼마 넘으면 울리게 할지, 경고음은 한번 울릴지 속도 넘긴 상태면 계속 울릴지 결정하기 - 일단 계속 울리는 것으로

# b.차량 속도가 30넘어서 엑셀 밟을 때마다 매번 잠금을 계속 하는데 한번만 해도 되는 문제 해결하기 - 완
# ~~생각해본 해결법들~~
# 1.차량 문들이 다 잠겨있는지 확인하는 함수 만들어서 이걸 엑셀레이터 조건문에 넣기 

# c.차량 주행중에 문열면 안열리게 코드 바꾸고 확인하는 테스트케이스(테스트함수)도 추가로 정의 - 잠금장치가 해제 안되는 것으로

# d.다 만들었으면 inspection 문서에 수정한거 추가한거 작성 !!!!!!!!!!!!!!!!!!!!!!!!!!!하하하하하





# #추가로만든거
# lock_door(car_controller):
# unlock_door(car_controller): 함수 만듦


# 경고 메시지를 출력하는 함수
def warn_speed_limit():
    global speedtest
    speedtest = True
    print("경고: 차량 속도가 120km/h를 초과했습니다.")  # 과속 경고 메시지 출력

# execute_command를 제어하는 콜백 함수
def execute_command_callback(command, car_controller):
    # 주행 중 엔진을 끌 수 없다는 경고 메시지 함수
    def warn_engine_running():
        print("주행 중입니다. 엔진을 끌 수 없습니다.")  # 사용자에게 경고 메시지

    #문이 열려 있는 채로 가속 페달을 밟을 시
    def warn_drive_while_open():
        print("문이 열려 있는 채로 주행중입니다. 문을 닫으십시오.") #사용자에게 경고 메시지
    
    if command == "ENGINE_BTN":
        if car_controller.get_speed() == 0 and not car_controller.get_lock_status():
            car_controller.toggle_engine()  # 시동 ON
        elif car_controller.get_speed() > 0:
            warn_engine_running()  # 사용자에게 경고 메시지


    elif command == "ACCELERATE":
    #문이 모두 닫혀있고, 트렁크도 닫혀있을 때 가속
        if car_controller.get_engine_status() and not car_controller.get_lock_status():

            if(car_controller.get_left_door_status() == "OPEN" or car_controller.get_right_door_status() == "OPEN"
                or not car_controller.get_trunk_status()):  # 문이 열려 있는 채로 가속 페달을 밟을시
                warn_drive_while_open()  # 경고 메시지 출력
            
            car_controller.accelerate()  # 속도 +10
            if car_controller.get_speed() > 120:
                warn_speed_limit()

            if car_controller.get_speed() >= 30:  # 속도가 30km/h 이상일 때
                # 차량의 문 잠금 상태를 확인하고 이미 잠겨있지 않은 문만 잠금
                if car_controller.get_left_door_lock() != "LOCKED":
                    car_controller.lock_left_door()
                if car_controller.get_right_door_lock() != "LOCKED":
                    car_controller.lock_right_door()

                
    elif command == "BRAKE":
        if car_controller.get_speed() > 0:
            car_controller.brake()  # 속도 -10


    elif command == "LOCK":
        # 속도가 0이고 모든 문이 닫혀 있을 때 차량 잠금 가능
        if (car_controller.get_speed() == 0 and
            car_controller.get_left_door_status() == "CLOSED" and
            car_controller.get_right_door_status() == "CLOSED"): 
            # print("왼쪽 문 열림 상태: ",car_controller.get_left_door_status())
            lock_vehicle(car_controller) # 차량 전체 잠금
    elif command == "UNLOCK":
        if car_controller.get_speed() == 0:
            unlock_vehicle(car_controller) # 차량 전체 잠금 해제
            
    elif command == "DOOR_LOCK":
        if car_controller.get_speed() > 30:
            lock_door(car_controller)
    elif command == "DOOR_UNLOCK":
        if car_controller.get_speed() < 30:  # 속도가 30km/h 미만일 때만 문 잠금 해제 허용
            unlock_door(car_controller)  # 문 잠금 해제


    # 왼쪽 문 
    elif command == "LEFT_DOOR_LOCK":
        if (not car_controller.get_lock_status() and 
            car_controller.get_left_door_status() == "CLOSED"):
            car_controller.lock_left_door()  # 왼쪽 문 잠금    
    elif command == "LEFT_DOOR_UNLOCK":
        car_controller.unlock_left_door()  # 왼쪽 문 잠금 해제
        
    elif command == "LEFT_DOOR_OPEN":
        if (car_controller.get_left_door_lock() == "UNLOCKED" and 
            car_controller.get_left_door_status() == "CLOSED"):
            car_controller.open_left_door()  # 왼쪽 문 열기
    elif command == "LEFT_DOOR_CLOSE": 
        if car_controller.get_left_door_status() == "OPEN":
            car_controller.close_left_door()  # 왼쪽 문 닫기
        
        
    # 오른쪽 문
    elif command == "RIGHT_DOOR_LOCK":
        if (not car_controller.get_lock_status() and 
            car_controller.get_right_door_status() == "CLOSED"):
            car_controller.lock_right_door()  # 오른쪽 문 잠금
    elif command == "RIGHT_DOOR_UNLOCK":
        car_controller.unlock_right_door()  # 오른쪽 문 잠금 해제
            
    elif command == "RIGHT_DOOR_OPEN":
        if (car_controller.get_right_door_lock() == "UNLOCKED" and 
            car_controller.get_right_door_status() == "CLOSED"):
            car_controller.open_right_door()  # 오른쪽 문 열기
    elif command == "RIGHT_DOOR_CLOSE":
        if car_controller.get_right_door_status() == "OPEN":
            car_controller.close_right_door()  # 오른쪽 문 닫기
        
        
    elif command == "TRUNK_OPEN":
        if (not car_controller.get_lock_status() and # 차량이 잠겨 있을 때는 트렁크를 열 수 없음
            car_controller.get_trunk_status() and # 트렁크가 닫혀 있을 때만 열 수 있음
            car_controller.get_speed() == 0): # 주행 중에는 트렁크를 열 수 없음
            car_controller.open_trunk()  # 트렁크 열기
    elif command == "TRUNK_CLOSE":
        if not car_controller.get_trunk_status(): # 트렁크가 열려 있을 때만 닫을 수 있음
            car_controller.close_trunk()  # 트렁크 닫기
            
        
    elif command == "SOS":
        while car_controller.get_speed() > 0:  # 속도가 0이 될 때까지 브레이크
            car_controller.brake() 
        unlock_door(car_controller) #---차 전체잠금이 아니라 문만 잠금 해제 1113 김준혁---
        car_controller.open_left_door()
        car_controller.open_right_door()  
        car_controller.open_trunk()

    # elif command == "SAFE":
    #     if car_controller.get_speed() > 0:  # 차량이 주행 중일 때
    #         warn_engine_running()  # 사용자에게 경고 메시지 --불필요한 커맨드, 삭제! 1113김준혁--

# 차량 전장장치 잠금 관련 함수
def lock_vehicle(car_controller):
    car_controller.lock_vehicle()  
    car_controller.lock_right_door()  
    car_controller.lock_left_door()  


def unlock_vehicle(car_controller):
    car_controller.unlock_vehicle()  
    car_controller.unlock_right_door() 
    car_controller.unlock_left_door()  

# 차량 문 잠금 관련 함수             --- 차량 문만 잠금하는 함수 없어서 따로 만듦, 1113 김준혁 ---
def lock_door(car_controller):
    car_controller.lock_right_door()  
    car_controller.lock_left_door()  

def unlock_door(car_controller):
    car_controller.unlock_right_door() 
    car_controller.unlock_left_door() 
    
# 차량 모든 문 잠겼는지 확인하는 함수


class TestCarController(unittest.TestCase):
    
    def setUp(self):
        self.car = Car()
        self.controller = CarController(self.car)

    def test_SOS(self):
        # SOS 명령을 실행하고 상태 확인
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("ENGINE_BTN", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("SOS", self.controller) #여기서 속도가 0되고, 문이랑 트렁크 열린다
        self.assertEqual(self.controller.get_speed(), 0, "차량이 정지되지 않았습니다.")
        self.assertFalse(self.car.lock, "모든 문이 잠금 해제되지 않았습니다.")
        self.assertFalse(self.car.trunk_status, "트렁크가 열리지 않았습니다.")

    def test_accelerate_lock_trigger(self):
        # 엔진을 켜고 세 번 가속하여 속도가 30이 되도록 설정
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("ENGINE_BTN", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)

        # 속도가 30에 도달한 후 모든 문과 트렁크가 잠겼는지 확인
        self.assertEqual(self.controller.get_speed(), 30, "차량 속도가 30km/h가 되지 않았습니다.")
        self.assertEqual(self.car.left_door_lock, "LOCKED", "속도가 30km/h일 때 왼쪽 문이 잠기지 않았습니다.")
        self.assertEqual(self.car.right_door_lock, "LOCKED", "속도가 30km/h일 때 오른쪽 문이 잠기지 않았습니다.")
        self.assertTrue(self.car.trunk_status, "속도가 30km/h일 때 트렁크가 닫히지 않았습니다.")

    def test_lock_while_door_opened(self): 
        # 일부 문이 열린 상태에서 차량 전체 잠금 작동 여부 확인(작동하면 안됨)
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("LEFT_DOOR_OPEN", self.controller)
        execute_command_callback("LOCK", self.controller)
        # 차량이 잠기지 않아야 함 (문이 열려 있으므로)
        self.assertFalse(self.car.lock, "문이 열린 상태에서 차량이 잠겼습니다.")

    def test_trunk_open_during_drive(self): # 현재 실패
        # 주행 중 트렁크 열기 시도
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("ENGINE_BTN", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("TRUNK_OPEN", self.controller)
        # 트렁크가 열리지 않아야 함
        self.assertEqual(self.car.trunk_status, True, "주행 중에 트렁크가 열렸습니다.")

    #문이 열린 상태에서 차가 출발하면 경고 메시지가 출력되는지 확인
    def test_drive_while_door_open(self):
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("ENGINE_BTN", self.controller)
        execute_command_callback("LEFT_DOOR_OPEN", self.controller)
        #문이 열린 채로 가속 시도
        execute_command_callback("ACCELERATE", self.controller)
        #가속은 되지만 경고 메시지가 나오는 것을 확인
        self.assertGreater(self.controller.get_speed(), 0, "자동차가 가속 되지 않았습니다.")

    #주행 중에는 엔진이 꺼지지 않는지 확인
    def test_engine_not_turnoff_while_driving(self):
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("ENGINE_BTN", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        #주행 중에 엔진 끄는걸 시도
        execute_command_callback("ENGINE_BTN", self.controller)
        self.assertTrue(self.car.engine_on, "주행 중에 엔진이 꺼졌습니다.")
        
    def test_speed_warning(self):
        global speedtest
        speedtest = False  # 초기화
        
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("ENGINE_BTN", self.controller)
        for _ in range(15):
            execute_command_callback("ACCELERATE", self.controller)

        # 현재 속도 출력 (디버그)
        print(f"현재 속도: {self.controller.get_speed()} km/h")
        # 속도가 120km/h 이상이고 과속 경고가 발생했는지 확인
        self.assertGreater(self.controller.get_speed(), 120, "속도가 120km/h를 넘지 않았습니다.")
        self.assertTrue(speedtest, "120km/h 초과 시 과속 경고가 발생하지 않았습니다.")
        
    def test_locks_not_disengage_above_30kmh(self):
        # 엔진을 켜고 가속하여 차량을 주행 상태로 만듬
        execute_command_callback("UNLOCK", self.controller)
        execute_command_callback("ENGINE_BTN", self.controller)
        execute_command_callback("ACCELERATE", self.controller)  # 첫 번째 가속
        execute_command_callback("ACCELERATE", self.controller)  # 두 번째 가속
        execute_command_callback("ACCELERATE", self.controller)  # 세 번째 가속, 속도는 30km/h 이상

        # 차량 속도가 30km/h 이상일 때 문 잠금 해제 시도
        execute_command_callback("LEFT_DOOR_UNLOCK", self.controller)
        execute_command_callback("RIGHT_DOOR_UNLOCK", self.controller)
        
        # 잠금 해제가 되지 않아야 함
        self.assertEqual(self.car.left_door_lock, "LOCKED", "속도 30km/h 이상에서 왼쪽 문이 잠금 해제되었습니다.")
        self.assertEqual(self.car.right_door_lock, "LOCKED", "속도 30km/h 이상에서 오른쪽 문이 잠금 해제되었습니다.")
        
    

def file_input_thread(gui):
    while True:
        file_path = input("Please enter the command file path (or 'exit' to quit): ")
        
        if file_path.lower() == 'exit':
            print("Exiting program.")
            break

        # 파일 경로를 받은 후 GUI의 mainloop에서 실행할 수 있도록 큐에 넣음
        gui.window.after(0, lambda: gui.process_commands(file_path))

# 파일 경로를 입력받는 함수
# -> 가급적 수정하지 마세요.
if __name__ == "__main__":
    car = Car() 
    car_controller = CarController(car)
    unittest.main(exit=False)
    # GUI는 메인 스레드에서 실행
    gui = CarSimulatorGUI(car_controller, lambda command: execute_command_callback(command, car_controller))

    # 파일 입력 스레드는 별도로 실행하여, GUI와 병행 처리
    input_thread = threading.Thread(target=file_input_thread, args=(gui,))
    input_thread.daemon = True  # 메인 스레드가 종료되면 서브 스레드도 종료되도록 설정
    input_thread.start()

    # GUI 시작 (메인 스레드에서 실행)
    gui.start()
