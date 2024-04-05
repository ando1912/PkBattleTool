import cv2 as cv
from PIL import Image, ImageTk
import threading
import datetime
from logging import getLogger

from module import config

class CameraCapture:
    def __init__(self):
        self.logger = getLogger("Log").getChild("CameraCapture")

        self.video_source = int(config.get("DEFAULT","camera_id"))
        self.vid = cv.VideoCapture(self.video_source)

        self.screenshot_folder_path = config.get("DEFAULT","screenshot_folder")
        self.display_fps = config.get("DEFAULT","display_fps")

        self.vid.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        self.vid.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

        self.width = int(self.vid.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.logger.debug(f"CameraConfig:{self.width}x{self.height}/{self.display_fps}")
        # print("W:{} / H:{}".format(self.width,self.height))

        self.is_capturing = False
        self.capture_thread = None
        self.frame = None
    
    def __del__(self):
        self.stop_capture()
        if self.vid.isOpened():
            self.vid.release()


    def start_capture(self):
        self.logger.debug("Execute start_capture")
        self.is_capturing= True
        self.capture_thread = threading.Thread(target=self.capture_video)
        self.capture_thread.start()
    
    def stop_capture(self):
        self.logger.debug("Execute stop_capture")
        self.is_capturing = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join()
    
    def capture_video(self):
        self.logger.debug("Execute capture_video")
        # print("capture_videを実行")
        while self.is_capturing:
            # print("capture videを実行中")
            ret, frame = self.vid.read()
            if ret:
                # print("フレームに格納")
                self.frame = frame
                # cv.imshow("text",frame)
        
    def get_frame(self):
        # ループ内処理のためログ出力は割愛
        # self.logger.debug("Execute get_frame")
        return self.frame

    def save_frame(self):
        self.logger.debug("Execute save_frame")
        file_name = "{}/screenshot_{}".format(self.screenshot_folder_path,datetime.datetime.now().strftime("%y%m%d%H%M%S") )
        cv.imwrite("{}.jpg".format(file_name),self.frame)
        print("save as {}".format(file_name))

    def convert_frame_to_photo(self):
        self.logger.debug("Execute convert_frame_to_photo")
        frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        return ImageTk.PhotoImage(image=Image.fromarray(frame))

    def release(self):
        self.logger.debug("Execute release")
        if self.vid.isOpened():
            self.vid.release()
    
class CameraControl:
    def __init__(self, camera_capture):
        self.logger = getLogger("Log").getChild("CameraControl")
        self.camera_capture = camera_capture

    def start_capture(self):
        self.logger.debug("Execute start_capture")
        self.camera_capture.start_capture()

    def stop_capture(self):
        self.logger.debug("Execute stop_capture")
        self.camera_capture.stop_capture()

    def release_camera(self):
        self.logger.debug("Execute release_camera")
        self.camera_capture.release()
    
    def save_frame(self):
        self.logger.debug("Execute save_frame")
        # print("スクリーンショット開始")
        self.camera_capture.save_frame()