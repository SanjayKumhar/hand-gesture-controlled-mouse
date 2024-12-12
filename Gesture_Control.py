# Imports

import cv2
import mediapipe as mp
import pyautogui
from google.protobuf.json_format import MessageToDict
from Gestures import HandGesture,HandLabel
from Controllers import Controller
from Hand_Recognition import HandRecognition

pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cv2.namedWindow('Gesture Controlled Virtual Mouse',cv2.WINDOW_NORMAL)
cv2.resizeWindow('Gesture Controlled Virtual Mouse',1200,600)

# Handles camera, obtain landmarks from mediapipe, entry point of Application.
"""
Attributes:
gc_mode       : (int) indicates weather gesture controller is running or not, 1 if running, otherwise 0.
capt_frame    : (Object) object obtained from cv2, for capturing video frame.
cam_height    : (int) highet in pixels of obtained frame from camera.
cam_width     : (int) width in pixels of obtained frame from camera.
hr_major_hand : (Object) of 'HandRecognition', object representing major hand.
hr_minor_hand : (Object) of 'HandRecognition', object representing minor hand.
domin_hand    : (bool) True if right hand is dominant hand, otherwise False. default True.

"""
class GestureController:
    gc_mode = 0
    capt_frame = None
    cam_height = None
    cam_width = None
    hr_major_hand = None # Right Hand by default
    hr_minor_hand = None # Left hand by default
    domin_hand = True # set it to true/false for right/left respectively 

    def __init__(self):
        """Initilaizes attributes."""
        # GestureController.domin_hand=input("Enter True/False for right/left hand respectively:")
        GestureController.gc_mode = 1
        GestureController.capt_frame = cv2.VideoCapture(0)
        GestureController.cam_height = GestureController.capt_frame.get(cv2.CAP_PROP_FRAME_HEIGHT)
        GestureController.cam_width = GestureController.capt_frame.get(cv2.CAP_PROP_FRAME_WIDTH)
    
    def classify_hands(results):
        """
        sets 'hr_major_hand', 'hr_minor_hand' based on classification(left, right) of hand obtained from mediapipe, 
        uses 'domin_hand' to decide major and minor hand.
        """
        left , right = None,None
        # if len(results.multi_handedness) > 1:
        #     print("More than one hands in frame")
            
        try:
            handedness_dict = MessageToDict(results.multi_handedness[0]) 
            # output of handedness_dict = {'classification': [{'index': 0, 'score': 0.98131067, 'label': 'Left'}]}
            # print (results.multi_handedness[1])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[0]
            else :
                left = results.multi_hand_landmarks[0]
        except:
            pass

        '''
        output of results.multi_hand_landmarks[0] =
        landmark {
            x: 0.727735698223114
            y: 0.6341353058815002
            z: -0.15457764267921448
        }
        output of results.multihandedness = 
        [classification {
            index: 1
            score: 0.8971208333969116
            label: "Right"
            }
        , classification {
            index: 0
            score: 0.9859097003936768
            label: "Left"
            }
        ]
        '''
        # print(right)
        # print (len(results.multi_handedness))
        # print(results.multi_handedness)
        # print(results.multi_handedness[1])
        # print (handedness_dict['classification'][0]['label'])

        # try:
        #     handedness_dict = MessageToDict(results.multi_handedness[1])
        #     if handedness_dict['classification'][0]['label'] == 'Left':
        #         left = results.multi_hand_landmarks[1]
        #     else :
        #         right = results.multi_hand_landmarks[1]
        # except:
        #     pass
        
        # print (len(results.multi_handedness))
        # print(results.multi_handedness)
        # print(right)
        
        if GestureController.domin_hand == True:
            GestureController.hr_major_hand = right # land-marks of right hand
            GestureController.hr_minor_hand = left  # land-marks of left hand
        else :
            GestureController.hr_major_hand = left
            GestureController.hr_minor_hand = right

    def start(self):
        """
        Entry point of whole programm, caputres video frame and passes, obtains
        landmark from mediapipe and passes it to 'majorHand_object' and 'minorHand_object' for
        controlling.
        """
        #objects of HandRecognition()
        majorHand_object = HandRecognition(HandLabel.MAJOR_hand)
        minorHand_object = HandRecognition(HandLabel.MINOR_hand)
        # print(majorHand_object)

        with mp_hands.Hands(max_num_hands = 2,min_detection_confidence=0.6, min_tracking_confidence=0.6) as hands:
            while GestureController.capt_frame.isOpened() and GestureController.gc_mode:
                success, image = GestureController.capt_frame.read()

                if not success:
                    print("Camera frame is empty.")
                    continue
                
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:                   
                    GestureController.classify_hands(results)
                    majorHand_object.update_hand_results(GestureController.hr_major_hand)
                    minorHand_object.update_hand_results(GestureController.hr_minor_hand)

                    majorHand_object.set_fingerState()
                    minorHand_object.set_fingerState()
                    gesture_name = minorHand_object.get_gesture()

                    if gesture_name == HandGesture.PINCH_MINOR_hand:
                        Controller.handle_gesture_controls(gesture_name, minorHand_object.hand_results)
                    else:
                        gesture_name = majorHand_object.get_gesture()
                        Controller.handle_gesture_controls(gesture_name, majorHand_object.hand_results)
                    
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                else:
                    Controller.prev_hand = None
                cv2.imshow('Gesture Controlled Virtual Mouse', image)
                if cv2.waitKey(5) & 0xFF == 13:
                    break
        GestureController.capt_frame.release()
        cv2.destroyAllWindows()

gesture_controller_object = GestureController()
gesture_controller_object.start()