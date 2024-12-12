# Imports

import pyautogui
import math
from Gestures import HandGesture,HandLabel
pyautogui.FAILSAFE = False

# Convert Mediapipe Landmarks to recognizable Gestures.
# Constructs all the necessary attributes for the HandRecognition object.
"""
Parameters:
curr_comput_gesture : (int) Represent gesture of Enum 'HandGesture',stores computed gesture for current frame.
ori_gesture         : (int) Represent gesture of Enum 'HandGesture', stores gesture being used.
prev_gesture        : (int) Represent gesture of Enum 'HandGesture', stores gesture computed for previous frame.
frame_count         : (int) total no. of frames since 'ori_gesture' is updated.
hand_results        : (Object) Landmarks obtained from mediapipe.
hand_label          : (int) Represents multi-handedness of Enum 'HandLabel'.

"""
class HandRecognition:
    def __init__(self, hand_label):
        self.curr_comput_gesture = 0
        self.ori_gesture = HandGesture.PALM
        self.prev_gesture = HandGesture.PALM
        self.frame_count = 0
        self.hand_results = None
        self.hand_label = hand_label
        
    
    def update_hand_results(self, hand_results):
        self.hand_results = hand_results # either left or right

    def get_signed_distance(self, point):
        """
        returns signed euclidean distance between 'point'.
        Parameters:
        point : list contaning two elements of type list/tuple which represents landmark point.
        Returns float
        """
        sign = 1
        # print(len(point))
        # print("***")
        '''(self.hand_results.landmark[point[0]].y < self.hand_results.landmark[point[1]].y) 
        indicates that finger is band forward
        '''
        if self.hand_results.landmark[point[0]].y < self.hand_results.landmark[point[1]].y:
            sign = -1
            # print(self.hand_results.landmark[point[0]].y,self.hand_results.landmark[point[1]].y)
            # print("*****")
        # print(point)
        # print(self.hand_results.landmark[point[0]].y,"1111111")
        # print(self.hand_results.landmark[point[0]].x)
        
        #  calculating distance
        distance = (self.hand_results.landmark[point[0]].x - self.hand_results.landmark[point[1]].x)**2
        distance += (self.hand_results.landmark[point[0]].y - self.hand_results.landmark[point[1]].y)**2
        distance = math.sqrt(distance)
        # print(dist)
        return distance*sign
    
    def get_distance(self, point):
        """
        returns euclidean distance between 'point'.
        Parameters
        point : list contaning two elements of type list/tuple which represents landmark point.
        Returns float
        """
        distance = (self.hand_results.landmark[point[0]].x - self.hand_results.landmark[point[1]].x)**2
        distance += (self.hand_results.landmark[point[0]].y - self.hand_results.landmark[point[1]].y)**2
        distance = math.sqrt(distance)
        return distance
    
    def get_distance_zAxis(self,point):
        """
        returns absolute difference on z-axis between 'point'.
        Parameters:
        point : list contaning two elements of type list/tuple which represents landmark point.
        Returns float
        """
        return abs(self.hand_results.landmark[point[0]].z - self.hand_results.landmark[point[1]].z)
    
    # Function to find Gesture Encoding using current finger_state.
    # Finger_state: 1 if finger is open, else 0
    def set_fingerState(self):
        
        # set 'curr_comput_gesture' by computing ratio of distance between finger tip, middle knuckle, base knuckle. 
        # Returns None

        if self.hand_results == None:
            return

        points = [[8,5,0],[12,9,0],[16,13,0],[20,17,0]]
        self.curr_comput_gesture = 0
        # self.curr_comput_gesture = self.curr_comput_gesture | 0 #thumb
        
        for idx,point in enumerate(points):
            dist1 = self.get_signed_distance(point[:2])
            dist2 = self.get_signed_distance(point[1:])
            # print(point[:2])
            # print(point[1:])
            # print(dist,dist2,"*********8")
            try:
                ratio = round(dist1/dist2,1)
                # print(ratio)
            except:
                ratio = round(dist1/0.01,1)
            
            # print(dist,dist2,self.curr_comput_gesture,"**")
            self.curr_comput_gesture = self.curr_comput_gesture << 1
            if ratio > 0.5 :
                self.curr_comput_gesture = self.curr_comput_gesture | 1
                # print(self.curr_comput_gesture,"******")
    

    # Handling Fluctations due to noise
    def get_gesture(self):
        """
        returns int representing gesture of Enum 'HandGesture' sets 'frame_count', 'ori_gesture', 'prev_gesture', 
        handles fluctations due to noise. Returns int
        """
        if self.hand_results == None:
            return HandGesture.PALM

        current_gesture = HandGesture.PALM
        if self.curr_comput_gesture in [HandGesture.LAST3_fingers,HandGesture.LAST4_fingers] and self.get_distance([8,4]) < 0.05:
            if self.hand_label == HandLabel.MINOR_hand :
                current_gesture = HandGesture.PINCH_MINOR_hand
            else:
                current_gesture = HandGesture.PINCH_MAJOR_hand

        elif HandGesture.FIRST2_fingers == self.curr_comput_gesture :
            point = [[8,12],[5,9]]
            dist1 = self.get_distance(point[0])
            dist2 = self.get_distance(point[1])
            ratio = dist1/dist2
            if ratio > 1.7:
                current_gesture = HandGesture.V_GESTURE
            else:
                if self.get_distance_zAxis([8,12]) < 0.1:
                    current_gesture =  HandGesture.TWO_FINGERS_CLOSED
                    # print(HandGesture.TWO_FINGERS_CLOSED)
                else:
                    current_gesture =  HandGesture.MID_finger
                    # print(current_gesture,"****")
            
        else:
            current_gesture =  self.curr_comput_gesture
        
        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.prev_gesture = current_gesture

        if self.frame_count > 4 :
            self.ori_gesture = current_gesture
        return self.ori_gesture