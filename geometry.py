import math

""" 
    we are utilising one and only 3D Euclidean Distance 
    to compute and detect movement
""" 

#####
""" 
    simple euclidean distance funciton 
    to calculate between 2 landmarks lm points
""" 
def euclidean_distance(lm1, lm2, frame_width: int = 1, frame_height: int = 1) -> float:
    dx = (lm2.x - lm1.x) * frame_width # to pixels
    dy = (lm2.y - lm1.y) * frame_height # to pixels
    dz =  (lm2.z - lm1.z) * frame_width # depth - spatial pixels

    return math.sqrt(dx**2 + dy**2 + dz**2)


""" 
    To allow more possibilities, 
    we measure "how folded" my finger is using
    finger tip to wrist &
    knuckle (MCP - base) to wrist distances 
    and their ratios

    Ratio close to 1 means palm out
    Ratio around 50-60% means bent fingers 
    BUT NOT FIST YET
"""

def calculate_finger_flex(tip_lm, mcp_lm, wrist_lm, w:int, h:int) -> float:
    tip_to_wrist = euclidean_distance(tip_lm, wrist_lm, w, h)
    mcp_to_wrist = euclidean_distance(mcp_lm, wrist_lm, w, h)

    if mcp_to_wrist == 0.0: # fist
        return 0.0
    
    return tip_to_wrist/mcp_to_wrist

"""
Subtracting the position values from wrist to 
make wrist as the base and make values
invariant to hand position on the screen
"""
def extract_feature(hand_landmarks) -> list[float]:
    wrist = hand_landmarks[0]
    features=[]

    for lm in hand_landmarks:
        features.extend([lm.x-wrist.x,lm.y-wrist.y, lm.z-wrist.z])
    return features
