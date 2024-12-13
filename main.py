import threading
import unittest
from car import Car
from car_controller import CarController
from gui import CarSimulatorGUI

# 속도 관련 상수
SPEED_LIMIT = 120  #  과속 기준 속도 (km/h)
AUTO_LOCK_SPEED = 30  # 자동 잠금이 작동하는 속도 (km/h)

# 경고 메시지를 출력하는 함수
def exceed_speed_limit(car_controller):
    if car_controller.get_speed() > SPEED_LIMIT:
        print(f"경고: 차량 속도가 {SPEED_LIMIT}km/h를 초과했습니다.")  # 과속 경고 메시지 출력
        return True
    else:
        return False

# execute_command를 제어하는 콜백 함수
def execute_command_callback(command, car_controller):
    # dual command 처리 (공백이 있는 경우)
    if isinstance(command, str) and ' ' in command:
        command1, command2 = command.split()
        execute_dual_command_callback(command1, command2, car_controller)
        return
    # 주행 중 엔진을 끌 수 없다는 경고 메시지 함수
    def warn_engine_running():
        print("주행 중입니다. 엔진을 끌 수 없습니다.")  # 사용자에게 경고 메시지

    #문이 열려 있는 채로 가속 페달을 밟을 시
    def warn_drive_while_open():
        print("문이 열려 있는 채로 주행중입니다. 문을 닫으십시오.") #사용자에게 경고 메시지
        
    
    if command == "ENGINE_BTN": # 기존 시동 ON/OFF 버튼이었으나 이제 OFF 용도로만 사용
        #분기 1: 엔진ON 시도-엔진이 꺼져있는 상태에서 "ENGINE_BTN" 누름
        if not car_controller.get_engine_status():
            print("브레이크를 누른 상태에서 엔진버튼을 눌러야 합니다")
        #분기 2: 엔진OFF 시도-엔진이 켜져있는 상태에서 "ENGINE_BTN" 누름
        else:
            if car_controller.get_speed() == 0 and not car_controller.get_lock_status():
                car_controller.toggle_engine()  # 시동 OFF
            elif car_controller.get_speed() > 0:
                warn_engine_running()  # 사용자에게 경고 메시지
            
    elif command == "ACCELERATE":
        if car_controller.get_engine_status() and not car_controller.get_lock_status():

            if(car_controller.get_left_door_status() == "OPEN" or car_controller.get_right_door_status() == "OPEN"
                or not car_controller.get_trunk_status()):  # 문이 열려 있는 채로 가속 페달을 밟을시
                warn_drive_while_open()  # 경고 메시지 출력
            
            car_controller.accelerate()  # 속도 +10
            if car_controller.get_speed() >= SPEED_LIMIT:
                exceed_speed_limit(car_controller)

            if car_controller.get_speed() >= AUTO_LOCK_SPEED:  # 속도가 자동잠금속도 이상일 때
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
            car_controller.get_right_door_status() == "CLOSED" and
            car_controller.get_trunk_status()): 
            lock_vehicle(car_controller) # 차량 전체 잠금

    elif command == "UNLOCK":
        if car_controller.get_speed() == 0:
            unlock_vehicle(car_controller) # 차량 전체 잠금 해제
            
    # 왼쪽 문 잠금
    elif command == "LEFT_DOOR_LOCK":
        if (not car_controller.get_lock_status() and 
            car_controller.get_left_door_status() == "CLOSED"):
            car_controller.lock_left_door()  # 왼쪽 문 잠금  

    # 왼쪽 문 잠금 해제
    elif command == "LEFT_DOOR_UNLOCK":
        if (not car_controller.get_lock_status() and 
            car_controller.get_speed() < AUTO_LOCK_SPEED):  # 속도가 자동잠금속도 미만일 때만 잠금 해제 허용
            car_controller.unlock_left_door()  # 왼쪽 문 잠금 해제
        
    elif command == "LEFT_DOOR_OPEN":
        if (car_controller.get_left_door_lock() == "UNLOCKED" and 
            car_controller.get_left_door_status() == "CLOSED"):
            car_controller.open_left_door()  # 왼쪽 문 열기
            
    elif command == "LEFT_DOOR_CLOSE": 
        if car_controller.get_left_door_status() == "OPEN":
            car_controller.close_left_door()  # 왼쪽 문 닫기
        
        
    # 오른쪽 문 잠금
    elif command == "RIGHT_DOOR_LOCK":
        if (not car_controller.get_lock_status() and 
            car_controller.get_right_door_status() == "CLOSED"):
            car_controller.lock_right_door()  # 오른쪽 문 잠금

    # 오른쪽 문 잠금 해제
    elif command == "RIGHT_DOOR_UNLOCK":
        if (not car_controller.get_lock_status() and 
            car_controller.get_speed() < AUTO_LOCK_SPEED):  # 속도가 자동잠금속도 미만일 때만 잠금 해제 허용
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
        car_controller.unlock_left_door()
        car_controller.unlock_right_door()        #---차 전체잠금이 아니라 문만 잠금 해제 1113 김준혁--- #--unlock_left_door()가 두개고, unlock_right_door()가 없어 수정 최한주--
        car_controller.open_left_door()
        car_controller.open_right_door()
        car_controller.open_trunk()
        
# 두개의 execute_command를 제어하는 콜백 함수
def execute_dual_command_callback(command1, command2, car_controller):
    if command1=="BRAKE" and command2=="ENGINE_BTN":
        if car_controller.get_speed() == 0 and not car_controller.get_lock_status():
            car_controller.toggle_engine()  # 시동 ON
    else:
        #이 외에 커맨드는 command1,command2 순으로 실행하되 
        #같은 커맨드를 동시에 두번은 못하니까 (엑셀은 하나 밖에 없으므로 동시에 두번 밟을순 없다)
        #동일한 커맨드가 중복될 경우 한번만 실행
        if command1==command2:
            execute_command_callback(command1, car_controller)
        else:
            execute_command_callback(command1, car_controller)
            execute_command_callback(command2, car_controller)
        
        
# 차량 전장장치 잠금 관련 함수
def lock_vehicle(car_controller):
    car_controller.lock_vehicle()  
    car_controller.lock_right_door()  
    car_controller.lock_left_door()  


def unlock_vehicle(car_controller):
    car_controller.unlock_vehicle()  
    car_controller.unlock_right_door() 
    car_controller.unlock_left_door()  


class TestCarController(unittest.TestCase):
    
    def setUp(self):
        self.car = Car()
        self.controller = CarController(self.car)
        execute_command_callback("UNLOCK", self.controller)

    #차량 전체 잠금 테스트
    def test_car_lock(self):
        # 잠금 테스트 
        execute_command_callback("LOCK", self.controller)
        self.assertTrue(self.car.lock, "차량 전체 잠금이 작동하지 않았습니다.")

    def test_car_unlock(self):
        # 잠금 해제 테스트
        self.assertFalse(self.car.lock, "차량 전체 잠금 해제가 작동하지 않았습니다.")
        
    #왼쪽 문잠금 테스트    
    def test_left_door_lock(self):
        execute_command_callback("LEFT_DOOR_LOCK", self.controller)
        self.assertEqual(self.car.left_door_lock, "LOCKED", "왼쪽 문이 잠기지 않았습니다.")
        
    #오른쪽 문잠금 테스트    
    def test_right_door_lock(self):
        execute_command_callback("RIGHT_DOOR_LOCK", self.controller)
        self.assertEqual(self.car.right_door_lock, "LOCKED", "오른쪽 문이 잠기지 않았습니다.")
        
    #왼쪽 문잠금해제 테스트
    def test_left_door_unlock(self):
        execute_command_callback("LEFT_DOOR_LOCK", self.controller)
        execute_command_callback("LEFT_DOOR_UNLOCK", self.controller)
        self.assertEqual(self.car.left_door_lock, "UNLOCKED", "왼쪽 문이 잠금 해제되지 않았습니다.")
        
    #오른쪽 문잠금해제 테스트
    def test_right_door_unlock(self):
        execute_command_callback("RIGHT_DOOR_LOCK", self.controller)
        execute_command_callback("RIGHT_DOOR_UNLOCK", self.controller)
        self.assertEqual(self.car.right_door_lock, "UNLOCKED", "오른쪽 문이 잠금 해제되지 않았습니다.")

    #왼쪽 문닫기 테스트
    def test_left_door_close(self):
        execute_command_callback("LEFT_DOOR_OPEN", self.controller)
        execute_command_callback("LEFT_DOOR_CLOSE", self.controller)
        self.assertEqual(self.car.left_door_status, "CLOSED", "왼쪽 문이 닫히지 않았습니다.")
        
    #오른쪽 문닫기 테스트
    def test_right_door_close(self):
        execute_command_callback("RIGHT_DOOR_OPEN", self.controller)
        execute_command_callback("RIGHT_DOOR_CLOSE", self.controller)
        self.assertEqual(self.car.right_door_status, "CLOSED", "오른쪽 문이 닫히지 않았습니다.")
        
    #왼쪽 문열기 테스트
    def test_left_door_open(self):
        execute_command_callback("LEFT_DOOR_OPEN", self.controller)
        self.assertEqual(self.car.left_door_status, "OPEN", "왼쪽 문이 열리지 않았습니다.")
        
    #오른쪽 문열기 테스트
    def test_right_door_open(self):
        execute_command_callback("RIGHT_DOOR_OPEN", self.controller)
        self.assertEqual(self.car.right_door_status, "OPEN", "오른쪽 문이 열리지 않았습니다.")
    
    #시동 테스트
    def test_engine_on(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        self.assertTrue(self.car.engine_on, "엔진이 켜지지 않았습니다.")    
    
    #가속 테스트
    def test_accelerate(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        self.assertEqual(self.controller.get_speed(), 10, "차량 속도가 10km/h가 되지 않았습니다.")
        
    #브레이크 테스트
    def test_brake(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("BRAKE", self.controller)
        self.assertEqual(self.controller.get_speed(), 0, "차량이 정지되지 않았습니다.")
        
    #트렁크 열기 테스트
    def test_trunk_open(self):
        execute_command_callback("TRUNK_OPEN", self.controller)
        self.assertFalse(self.car.trunk_status, "트렁크가 열리지 않았습니다.")
        
    #트렁크 닫기 테스트
    def test_trunk_close(self):
        execute_command_callback("TRUNK_OPEN", self.controller)
        execute_command_callback("TRUNK_CLOSE", self.controller)
        self.assertTrue(self.car.trunk_status, "트렁크가 닫히지 않았습니다.")

    def test_sos(self):
        # SOS 명령을 실행하고 상태 확인
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("SOS", self.controller) #여기서 속도가 0되고, 문이랑 트렁크 열린다
        self.assertEqual(self.controller.get_speed(), 0, "차량이 정지되지 않았습니다.")
        self.assertFalse(self.car.lock, "모든 문이 잠금 해제되지 않았습니다.")
        self.assertFalse(self.car.trunk_status, "트렁크가 열리지 않았습니다.")

    def test_accelerate_lock_trigger(self):
        # 엔진을 켜고 세 번 가속하여 속도가 자동 잠금 속도에 도달하도록 설정
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)

        # 속도가 자동 잠금 속도에 도달한 후 모든 문과 트렁크가 잠겼는지 확인
        self.assertEqual(self.controller.get_speed(), AUTO_LOCK_SPEED, f"차량 속도가 {AUTO_LOCK_SPEED}km/h가 되지 않았습니다.")
        self.assertEqual(self.car.left_door_lock, "LOCKED", f"속도가 {AUTO_LOCK_SPEED}km/h일 때 왼쪽 문이 잠기지 않았습니다.")
        self.assertEqual(self.car.right_door_lock, "LOCKED", f"속도가 {AUTO_LOCK_SPEED}km/h일 때 오른쪽 문이 잠기지 않았습니다.")
        self.assertTrue(self.car.trunk_status, f"속도가 {AUTO_LOCK_SPEED}km/h일 때 트렁크가 닫히지 않았습니다.")

    def test_lock_while_door_opened(self): 
        # 일부 문이 열린 상태에서 차량 전체 잠금 작동 여부 확인(작동하면 안됨)
        execute_command_callback("LEFT_DOOR_OPEN", self.controller)
        execute_command_callback("LOCK", self.controller)
        # 차량이 잠기지 않아야 함 (문이 열려 있으므로)
        self.assertFalse(self.car.lock, "문이 열린 상태에서 차량이 잠겼습니다.")

    def test_trunk_open_during_drive(self): # 현재 실패
        # 주행 중 트렁크 열기 시도
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("TRUNK_OPEN", self.controller)
        # 트렁크가 열리지 않아야 함
        self.assertEqual(self.car.trunk_status, True, "주행 중에 트렁크가 열렸습니다.")

    #문이 열린 상태에서 차가 출발하면 경고 메시지가 출력되는지 확인
    def test_drive_while_door_open(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("LEFT_DOOR_OPEN", self.controller)
        #문이 열린 채로 가속 시도
        execute_command_callback("ACCELERATE", self.controller)
        #가속은 되지만 경고 메시지가 나오는 것을 확인
        self.assertGreater(self.controller.get_speed(), 0, "자동차가 가속 되지 않았습니다.")

    #주행 중에는 엔진이 꺼지지 않는지 확인
    def test_engine_not_turnoff_while_driving(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        execute_command_callback("ACCELERATE", self.controller)
        #주행 중에 엔진 끄는걸 시도
        execute_command_callback("ENGINE_BTN", self.controller)
        self.assertTrue(self.car.engine_on, "주행 중에 엔진이 꺼졌습니다.")
        
    def test_speed_warning(self):        
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        # 속도가 0km/h 일때 과속 경고가 발생했는지 확인
        self.assertFalse(exceed_speed_limit(self.controller), "0km/h 인데도 과속 경고가 발생했습니다.")
        for _ in range(15):
            execute_command_callback("ACCELERATE", self.controller)
        # 속도가 과속기준속도 이상일때 과속 경고가 발생했는지 확인
        self.assertTrue(exceed_speed_limit(self.controller), f"속도 {SPEED_LIMIT}km/h 초과 시 과속 경고가 발생하지 않았습니다.")
        
    def test_locks_not_disengage_above_auto_lock_speed(self):
        # 엔진을 켜고 가속하여 차량을 주행 상태로 만듬
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)  # 첫 번째 가속
        execute_command_callback("ACCELERATE", self.controller)  # 두 번째 가속
        execute_command_callback("ACCELERATE", self.controller)  # 세 번째 가속, 속도는 자동잠금속도 이상

        # 차량 속도가 자동잠금속도 이상일 때 문 잠금 해제 시도
        execute_command_callback("LEFT_DOOR_UNLOCK", self.controller)
        execute_command_callback("RIGHT_DOOR_UNLOCK", self.controller)
        
        # 잠금 해제가 되지 않아야 함
        self.assertEqual(self.car.left_door_lock, "LOCKED", f"속도 {AUTO_LOCK_SPEED}km/h 이상에서 왼쪽 문이 잠금 해제되었습니다.")
        self.assertEqual(self.car.right_door_lock, "LOCKED", f"속도 {AUTO_LOCK_SPEED}km/h 이상에서 오른쪽 문이 잠금 해제되었습니다.")
        
    # 1203 TDD 개발 김준혁
    #1.BRAKE ENGINE_BTN
    def test_brake_and_engine_btn(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        self.assertTrue(self.car.engine_on, "test1 fail: 엔진이 켜지지 않았습니다.")
        
    #2.ENGINE_BTN BRAKE 
    def test_engine_btn_and_brake(self):
        execute_dual_command_callback("ENGINE_BTN","BRAKE",self.controller)
        self.assertFalse(self.car.engine_on, "test2 fail: 잘못된 접근에도 엔진이 켜졌습니다.")
        
    #3.ENGINE_BTN
    def test_engine_btn(self):
        execute_command_callback("ENGINE_BTN",self.controller)
        self.assertFalse(self.car.engine_on, "test3 fail: 잘못된 접근에도 엔진이 켜졌습니다.")
    
    #4.BRAKE
    #  ENGINE_BTN
    def test_brake_wait_engine_btn(self):
        execute_command_callback("BRAKE",self.controller)
        execute_command_callback("ENGINE_BTN",self.controller)
        self.assertFalse(self.car.engine_on, "test4 fail: 잘못된 접근에도 엔진이 켜졌습니다.")
        
    #5."ACCELERATE","ACCELERATE"
    def test_equal_dual_command(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_dual_command_callback("ACCELERATE","ACCELERATE",self.controller)
        execute_dual_command_callback("ACCELERATE","ACCELERATE",self.controller)
        execute_dual_command_callback("ACCELERATE","ACCELERATE",self.controller)
        execute_dual_command_callback("ACCELERATE","ACCELERATE",self.controller)
        self.assertEqual(self.controller.get_speed(), 40, "차량 속도가 40km/h가 되지 않았습니다.")
    
    #6."ACCELERATE","BRAKE"
    def test_another_dual_command(self):
        execute_dual_command_callback("BRAKE","ENGINE_BTN",self.controller)
        execute_command_callback("ACCELERATE", self.controller)  #가속
        execute_dual_command_callback("ACCELERATE","BRAKE",self.controller)#가속하고 브레이크
        execute_dual_command_callback("ACCELERATE","BRAKE",self.controller)#가속하고 브레이크
        execute_dual_command_callback("ACCELERATE","BRAKE",self.controller)#가속하고 브레이크
        print(self.controller.get_speed())
        self.assertEqual(self.controller.get_speed(), 10, "차량 속도가 10km/h가 되지 않았습니다.")
        
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