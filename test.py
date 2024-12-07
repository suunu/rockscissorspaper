import cv2
import numpy as np
import mss
import pyautogui

# 주황색 HSV 범위
lower_orange = np.array([10, 30, 100], dtype=np.uint8)
upper_orange = np.array([25, 255, 255], dtype=np.uint8)

# 파란색 HSV 범위
lower_blue = np.array([100, 50, 0], dtype=np.uint8)
upper_blue = np.array([140, 255, 255], dtype=np.uint8)

click_enabled = False

def capture_screen(region):
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        frame = np.array(screenshot)
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

def find_and_draw_contours(mask, frame, color):
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # 노이즈 제거
            cv2.drawContours(frame, [contour], -1, color, 3)  
    return frame

# 가위, 바위, 보 판단 함수 본인에게 맞는 수치 찾으세여
def determine_rps(pixel_count):
    if pixel_count > 150000:
        return "Paper"
    elif pixel_count > 130000:
        return "Scissors"
    elif pixel_count > 100000:
        return "Rock"
    else:
        return "Nothing"

def determine_winner(orange_rps, blue_rps):
    if orange_rps == blue_rps:
        return "Draw"
    if (orange_rps == "Rock" and blue_rps == "Paper") or \
       (orange_rps == "Scissors" and blue_rps == "Rock") or \
       (orange_rps == "Paper" and blue_rps == "Scissors"):
        return "Blue Wins"
    return "Orange Wins"

region = {"top": 200, "left": 2100, "width": 400, "height": 800}

while True:
    frame = capture_screen(region)

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    orange_mask = cv2.inRange(hsv_frame, lower_orange, upper_orange)
    blue_mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    orange_pixel_count = cv2.countNonZero(orange_mask)
    blue_pixel_count = cv2.countNonZero(blue_mask)

    orange_rps = determine_rps(orange_pixel_count)
    blue_rps = determine_rps(blue_pixel_count)

    output_frame = np.zeros_like(frame) 
    output_frame = find_and_draw_contours(orange_mask, output_frame, (0, 165, 255))  
    output_frame = find_and_draw_contours(blue_mask, output_frame, (255, 0, 0))  

    winner = determine_winner(orange_rps, blue_rps)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(output_frame, f"Orange: {orange_rps}", (50, 50), font, 1.5, (0, 165, 255), 3)
    cv2.putText(output_frame, f"Blue: {blue_rps}", (50, output_frame.shape[0] - 50), font, 1.5, (255, 0, 0), 3)
    cv2.putText(output_frame, f"Winner: {winner}", (50, output_frame.shape[0] // 2), font, 2, (255, 255, 255), 4)
    cv2.putText(output_frame, f"Click: {'Enabled' if click_enabled else 'Disabled'}", (50, 100), font, 1, (0, 255, 0), 2)

    # 콘솔 
    print(f"Orange Hand: {orange_rps} (Pixels: {orange_pixel_count})")
    print(f"Blue Hand: {blue_rps} (Pixels: {blue_pixel_count})")
    print(f"Result: {winner}")
    print(f"Click Status: {'Enabled' if click_enabled else 'Disabled'}")
    print("-" * 50)

    # 파란 손이 이기면 클릭
    if click_enabled and winner == "Blue Wins":
        print("Blue Wins! Clicking the screen...")
        pyautogui.click(x=2300, y=500)  # 파란손 위치

    cv2.imshow("Combined Contours", output_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC 키
        break
    elif key == ord('c'): 
        click_enabled = not click_enabled
        print(f"Clicking {'Enabled' if click_enabled else 'Disabled'}")

cv2.destroyAllWindows()
