import cv2
import numpy as np
import mss
import pyautogui

lower_orange = np.array([10, 30, 100], dtype=np.uint8)
upper_orange = np.array([25, 255, 255], dtype=np.uint8)
lower_blue = np.array([100, 50, 0], dtype=np.uint8)
upper_blue = np.array([140, 255, 255], dtype=np.uint8)

click_enabled = False

button_rect = (50, 50, 200, 100) 

def capture_screen(region):
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        frame = np.array(screenshot)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

# 가위, 바위, 보 판단 함수 본인에게 맞는 수치 입력하세여
def determine_rps(pixel_count):
    if pixel_count > 155000:
        return "Paper"
    elif pixel_count > 138000:
        return "Scissors"
    elif pixel_count > 100000:
        return "Rock"
    else:
        return "Nothing"

# 승리 판단 함수
def determine_winner(orange_rps, blue_rps):
    if orange_rps == blue_rps:
        return "Draw"
    if (orange_rps == "Rock" and blue_rps == "Paper") or \
       (orange_rps == "Scissors" and blue_rps == "Rock") or \
       (orange_rps == "Paper" and blue_rps == "Scissors"):
        return "Blue Wins"
    return "Orange Wins"

def is_inside_button(x, y, rect):
    rect_x, rect_y, rect_w, rect_h = rect
    return rect_x <= x <= rect_x + rect_w and rect_y <= y <= rect_y + rect_h

cv2.setUseOptimized(True)
cv2.setNumThreads(4)

region = {"top": 200, "left": 2100, "width": 400, "height": 800}

while True:
    frame = capture_screen(region)

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    orange_mask = cv2.inRange(hsv_frame, lower_orange, upper_orange)
    blue_mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    orange_pixel_count = np.count_nonzero(orange_mask)
    blue_pixel_count = np.count_nonzero(blue_mask)
    
    orange_rps = determine_rps(orange_pixel_count)
    blue_rps = determine_rps(blue_pixel_count)

    winner = determine_winner(orange_rps, blue_rps)

    # 파란 손이 이기면 클릭
    if click_enabled and winner == "Blue Wins":
        pyautogui.click(x=2300, y=900)  # 원하는 클릭 위치
        
    def mouse_callback(event, x, y, flags, param):
        global click_enabled
        if event == cv2.EVENT_LBUTTONDOWN:
            if is_inside_button(x, y, button_rect):
                click_enabled = not click_enabled
                print(f"Clicking {'Enabled' if click_enabled else 'Disabled'}")

    blank_frame = np.zeros((300, 300, 3), dtype=np.uint8)
    button_color = (0, 255, 0) if click_enabled else (0, 0, 255)
    cv2.rectangle(blank_frame, (button_rect[0], button_rect[1]),
                  (button_rect[0] + button_rect[2], button_rect[1] + button_rect[3]), button_color, -1)
    cv2.putText(blank_frame, "Click ON" if click_enabled else "Click OFF",
                (button_rect[0] + 10, button_rect[1] + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    cv2.imshow("Control", blank_frame)
    cv2.setMouseCallback("Control", mouse_callback)

    # 종료
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC 
        break

cv2.destroyAllWindows()
