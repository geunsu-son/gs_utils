import pyautogui
import time
from pywinauto import Desktop

def run_program(file_url):
    """
    윈도우 실행창(Win+R)으로 프로그램을 실행합니다.
    입력값: file_url (str) - 실행할 파일 경로
    반환값: 없음
    """
    pyautogui.keyDown('win')  # 'Win' 키를 누르고
    pyautogui.press('r')      # 'R' 키를 누름
    pyautogui.keyUp('win')    # 'Win' 키를 뗌

    pyautogui.write(file_url)  # 프로그램 경로 입력
    pyautogui.press('enter')  # 실행
    time.sleep(1)

def click_by_image_match(image_file, check_yn=0, check_image_file=None,confidence=0.8):
    """
    화면에서 이미지 매칭을 통해 버튼 클릭 또는 특정 화면 대기 후 클릭 수행
    입력값: image_file (str), check_yn (int), check_image_file (str), confidence (float)
    반환값: 없음
    """
    button_location = pyautogui.locateCenterOnScreen(image_file, confidence=confidence)

    if check_yn == 0:
        if button_location:
            pyautogui.click(button_location)
            time.sleep(1)
        else:
            pass

    # 특정 화면이 나올 때까지 대기
    elif check_yn == 1:
        while True:
            try:
                pyautogui.click(button_location)
                time.sleep(5)

                pyautogui.locateCenterOnScreen(check_image_file, confidence=0.7)
                time.sleep(1)
                break
            except:
                time.sleep(3)

def check_open_dialog(dialog_name, backend_type='win32'):
    """
    윈도우 창 목록에서 특정 다이얼로그가 열릴 때까지 대기합니다.
    입력값: dialog_name (str), backend_type (str)
    반환값: 없음
    """
    while True:
        windows = Desktop(backend=backend_type).windows()
        if len([window.window_text() for window in windows if dialog_name in window.window_text()]) > 0:
            time.sleep(1)
            break
        else:
            time.sleep(1)