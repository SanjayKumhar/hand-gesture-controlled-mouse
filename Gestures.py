from enum import IntEnum

# Gesture Encodings 
class HandGesture(IntEnum):
    # Binary Encoded
    """
    Enum for mapping all hand gesture to binary number.
    """
    FIST = 0
    PINKY_finger = 1
    RING_finger = 2
    MID_finger = 4
    LAST3_fingers = 7
    INDEX_finger = 8
    FIRST2_fingers = 12
    LAST4_fingers = 15
    THUMB = 16    
    PALM = 31
    
    # Extra Mappings
    V_GESTURE = 33
    TWO_FINGERS_CLOSED = 34
    PINCH_MAJOR_hand = 35 #for features using right hand geatures
    PINCH_MINOR_hand = 36 #for features using left hand gestures

# Multi-handedness Labels
class HandLabel(IntEnum):
    MINOR_hand = 0
    MAJOR_hand = 1
