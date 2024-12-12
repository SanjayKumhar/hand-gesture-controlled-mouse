# Imports

from ctypes import cast, POINTER
import time
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui
import screen_brightness_control as brightness_control
from Gestures import HandGesture
pyautogui.FAILSAFE = False

# Executes commands according to detected gestures.
"""
Attributes:
prev_x_coord           : (int) previous mouse location of x coordinate
prev_y_coord           : (int) previous mouse location of y coordinate
v_gest_flag            : (bool) true if V gesture is detected
fist_flag              : (bool) true if FIST gesture is detected
pinch_major_hand_flag  : (bool) true if PINCH gesture is detected through MAJOR hand, 
                            on x-axis 'Controller.change_system_brightness', on y-axis 'Controller.change_system_volume'.
pinch_minor_hand_flag  : (bool) true if PINCH gesture is detected through MINOR hand, 
                            on x-axis 'Controller.scroll_horizontal', on y-axis 'Controller.scroll_vertical'.
pinch_start_x_coord    : (int) x coordinate of hand landmark when pinch gesture is started.
pinch_start_y_coord    : (int) y coordinate of hand landmark when pinch gesture is started.
pinch_x_direction_flag : (bool) true if pinch gesture movment is along x-axis, otherwise false
prev_pinch_displacement: (int) stores quantized magnitued of prev pinch gesture displacement, from starting position
pinch_displacement     : (int) stores quantized magnitued of pinch gesture displacement, from starting position
frame_count            : (int) stores no. of frames since 'pinch_displacement' is updated.
prev_hand              : (tuple) stores (x, y) coordinates of hand in previous frame.
pinch_threshold        : (float) step size for quantization of 'pinch_displacement'.
"""

class Controller:
    # prev_x_coord = 0
    # prev_y_coord = 0
    # trial = True
    v_gest_flag = False
    fist_flag = False
    pinch_major_hand_flag = False
    pinch_minor_hand_flag = False
    pinch_start_x_coord = None
    pinch_start_y_coord = None
    pinch_x_direction_flag = None
    prev_pinch_displacement = 0
    pinch_displacement = 0
    frame_count = 0
    prev_hand = None
    pinch_threshold = 0.3
    
    def get_pinch_y_displacement(hand_result):
        """returns distance beween starting pinch y coord and current hand position y coord."""
        distance = round((Controller.pinch_start_y_coord - hand_result.landmark[8].y)*10,1)
        return distance

    def get_pinch_x_displacement(hand_result):
        """returns distance beween starting pinch x coord and current hand position x coord."""
        distance = round((hand_result.landmark[8].x - Controller.pinch_start_x_coord)*10,1)
        return distance
    
    # def change_system_brightness():
    #     """sets system brightness based on 'Controller.pinch_displacement'."""
    #     current_Brightness = brightness_control.get_brightness()/100.0
    #     # print(current_Brightness)
    #     # print(Controller.pinch_displacement)
    #     current_Brightness += Controller.pinch_displacement/5
    #     # print(current_Brightness)
    #     # print(Controller.pinch_displacement)
    #     if current_Brightness > 1.0:
    #         current_Brightness = 1.0
    #     elif current_Brightness < 0.0:
    #         current_Brightness = 0.0     
    #     # print(current_Brightness)
    #     # print("*********")  
    #     brightness_control.fade_brightness(int(100*current_Brightness) , start = brightness_control.get_brightness(),interval=1,increment=5)
    
    def change_system_brightness():
        current_brightness = brightness_control.get_brightness() / 100.0
        target_brightness = current_brightness + Controller.pinch_displacement / 10
        target_brightness = max(0.0, min(1.0, target_brightness))

        num_steps = int(abs(target_brightness - current_brightness) * 100)
        if num_steps == 0:
            return

        step_size = (target_brightness - current_brightness) / num_steps
        for i in range(num_steps):
            brightness_level = current_brightness + i * step_size
            brightness_control.set_brightness(int(brightness_level * 100))
            time.sleep(0.01)



    def change_system_volume():
        """sets system volume based on 'Controller.pinch_displacement'."""
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_Volume = volume.GetMasterVolumeLevelScalar()
        current_Volume += Controller.pinch_displacement/65.0
        if current_Volume > 1.0:
            current_Volume = 1.0
        elif current_Volume < 0.0:
            current_Volume = 0.0
        volume.SetMasterVolumeLevelScalar(current_Volume, None)
    
    def scroll_vertical():
        """scrolls on screen vertically."""
        pyautogui.scroll(120 if Controller.pinch_displacement>0.0 else -120)
        
    
    def scroll_horizontal():
        """scrolls on screen horizontally."""
        pyautogui.keyDown('shift')
        pyautogui.keyDown('ctrl')
        pyautogui.scroll(-120 if Controller.pinch_displacement>0.0 else 120)
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')

    # Locate Hand to get Cursor Position
    # Stabilize cursor by Dampening
    def get_cursor_position(hand_result):
        """
        returns coordinates of current hand position. Locates hand to get cursor position also stabilize cursor by 
        dampening jerky motion of hand. Returns tuple(float, float)
        """
        point = 9
        position = [hand_result.landmark[point].x ,hand_result.landmark[point].y]
        screen_x,screen_y = pyautogui.size()
        x_old,y_old = pyautogui.position()
        x = int(position[0]*screen_x)
        y = int(position[1]*screen_y)
        if Controller.prev_hand is None:
            Controller.prev_hand = x,y
        change_in_x = x - Controller.prev_hand[0]
        change_in_y = y - Controller.prev_hand[1]

        distance_square = change_in_x**2 + change_in_y**2
        ratio = 1
        Controller.prev_hand = [x,y]

        if distance_square <= 25:
            ratio = 0
        elif distance_square <= 900:
            ratio = 0.04 * (distance_square ** (1/2))  #0.07
        else:
            ratio = 3.1  #2.1
        x , y = x_old + change_in_x*ratio , y_old + change_in_y*ratio
        return (x,y) 

    

    def pinch_control_init(hand_result):
        """Initializes attributes for pinch gesture."""
        Controller.pinch_start_x_coord = hand_result.landmark[8].x
        Controller.pinch_start_y_coord = hand_result.landmark[8].y
        Controller.pinch_displacement = 0
        Controller.prev_pinch_displacement = 0
        Controller.frame_count = 0

    # Hold final position for 5 frames to change status
    def pinch_control(hand_result, control_horizontal_pinch, control_vertical_pinch):
        """
        calls 'control_horizontal_pinch'/'control_vertical_pinch' based on pinch flags,'frame_count' and sets 'pinch_displacement'.
        Parameters:
        hand_result              : (Object) Landmarks obtained from mediapipe.
        control_horizontal_pinch : callback function assosiated with horizontal pinch gesture.
        control_vertical_pinch   : callback function assosiated with vertical pinch gesture. 
        Returns None
        ----------
        """
        if Controller.frame_count == 5:
            Controller.frame_count = 0
            Controller.pinch_displacement = Controller.prev_pinch_displacement

            if Controller.pinch_x_direction_flag == True:
                control_horizontal_pinch() #x axis

            elif Controller.pinch_x_direction_flag == False:
                control_vertical_pinch() #y axis

        pinch_x_displacement =  Controller.get_pinch_x_displacement(hand_result)
        pinch_y_displacement =  Controller.get_pinch_y_displacement(hand_result)
            
        if abs(pinch_y_displacement) > abs(pinch_x_displacement) and abs(pinch_y_displacement) > Controller.pinch_threshold:
            Controller.pinch_x_direction_flag = False
            if abs(Controller.prev_pinch_displacement - pinch_y_displacement) < Controller.pinch_threshold:
                Controller.frame_count += 1
            else:
                Controller.prev_pinch_displacement = pinch_y_displacement
                Controller.frame_count = 0

        elif abs(pinch_x_displacement) > Controller.pinch_threshold:
            Controller.pinch_x_direction_flag = True
            if abs(Controller.prev_pinch_displacement - pinch_x_displacement) < Controller.pinch_threshold:
                Controller.frame_count += 1
            else:
                Controller.prev_pinch_displacement = pinch_x_displacement
                Controller.frame_count = 0

    def handle_gesture_controls(gesture, hand_result):  
        """Impliments all gesture functionality."""      
        cursor_x,cursor_y = None,None
        if gesture != HandGesture.PALM :
            cursor_x,cursor_y = Controller.get_cursor_position(hand_result)
        
        # flag reset
        if gesture != HandGesture.FIST and Controller.fist_flag:
            Controller.fist_flag = False
            pyautogui.mouseUp(button = "left",duration=0)

        if gesture != HandGesture.PINCH_MAJOR_hand and Controller.pinch_major_hand_flag:
            Controller.pinch_major_hand_flag = False

        if gesture != HandGesture.PINCH_MINOR_hand and Controller.pinch_minor_hand_flag:
            Controller.pinch_minor_hand_flag = False

        # implementation of features
        if gesture == HandGesture.V_GESTURE:
            Controller.v_gest_flag = True
            pyautogui.moveTo(cursor_x, cursor_y, duration = 0.001)

        elif gesture == HandGesture.FIST:
            if not Controller.fist_flag : 
                Controller.fist_flag = True
                pyautogui.mouseDown(button = "left",duration=0)
            pyautogui.moveTo(cursor_x, cursor_y, duration = 0.001)

        elif gesture == HandGesture.MID_finger and Controller.v_gest_flag:
            pyautogui.click(duration=0)
            Controller.v_gest_flag = False

        elif gesture == HandGesture.INDEX_finger and Controller.v_gest_flag:
            pyautogui.click(button='right',duration=0)
            Controller.v_gest_flag = False

        elif gesture == HandGesture.TWO_FINGERS_CLOSED and Controller.v_gest_flag:
            pyautogui.doubleClick()
            Controller.v_gest_flag = False

        elif gesture == HandGesture.PINCH_MINOR_hand:
            if Controller.pinch_minor_hand_flag == False:
                Controller.pinch_control_init(hand_result)
                Controller.pinch_minor_hand_flag = True
            Controller.pinch_control(hand_result,Controller.scroll_horizontal, Controller.scroll_vertical)
        
        elif gesture == HandGesture.PINCH_MAJOR_hand:
            if Controller.pinch_major_hand_flag == False:
                Controller.pinch_control_init(hand_result)
                Controller.pinch_major_hand_flag = True
            Controller.pinch_control(hand_result,Controller.change_system_brightness, Controller.change_system_volume)