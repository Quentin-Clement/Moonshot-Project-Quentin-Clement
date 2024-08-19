def get_thresholds():

    _ANGLE_HIP_KNEE_VERT = {
        'NORMAL' : (0,  30),
        'TRANS'  : (35, 65),
        'PASS'   : (80, 95)
    }    

        
    thresholds = {
        'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,  
        'HIP_THRESH'   : [15, 50],
        'ANKLE_THRESH' : 30,
        'KNEE_THRESH'  : [50, 80, 95],  
        'OFFSET_THRESH'    : 50.0,
        'INACTIVE_THRESH'  : 15.0,  
        'CNT_FRAME_THRESH' : 50

    }

    return thresholds