import os
import cv2
import time
import datetime

# 
def get_camera_img(cam_id = 0, wait_sec = 3):

    cap = cv2.VideoCapture(cam_id,cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

    btime = time.time()
    cnt = 0
    
    dt_now = datetime.datetime.now()
    folder_dir = dt_now.strftime("%y%m%d")
    
    while True:
        
        elasped_time = time.time() - btime
        
        ret, frame = cap.read()
        cv2.imshow("camera", frame)

        #繰り返し分から抜けるためのif文
        key =cv2.waitKey(10)
        if key == 27:
            break
        
        if elasped_time > wait_sec:
            if not os.path.exists(f"img\{folder_dir}"):
                os.makedirs(f"img\{folder_dir}")
            now = datetime.datetime.now()
            cv2.imwrite(f"img\{folder_dir}\{now.strftime('%y%m%d%H%M%S')}{now.microsecond//1000}.jpg",frame)
            btime = time.time()
            


if __name__ == '__main__':
    
    get_camera_img(cam_id = 4, wait_sec = 1)