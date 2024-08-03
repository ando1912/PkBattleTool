import os, sys
import cv2
from PIL import Image, ImageTk
import threading
import datetime
from logging import getLogger


from module import config
PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
class CameraCapture:
    def __init__(self) -> None:
        self.logger = getLogger("Log").getChild("CameraCapture")

        self.video_source = int(config.get("DEFAULT","camera_id"))
        self.vid = cv2.VideoCapture(self.video_source)

        self.screenshot_folder_path = config.get("DEFAULT","screenshot_folder")
        self.display_fps = config.get("DEFAULT","display_fps")

        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.logger.debug(f"CameraConfig:{self.width}x{self.height}/{self.display_fps}")
        # print("W:{} / H:{}".format(self.width,self.height))

        self.is_capturing = False
        self.capture_thread = None
        self.frame:cv2.typing.MatLike = None
    
    def __del__(self) -> None:
        self.stop_capture()
        if self.vid.isOpened():
            self.vid.release()


    def start_capture(self) -> None:
        """
        カメラの撮影を開始する
        """
        self.logger.info("Execute start_capture")
        self.is_capturing= True
        self.capture_thread = threading.Thread(target=self.capture_video)
        self.capture_thread.start()
    
    def stop_capture(self) -> None:
        """
        カメラの撮影を停止する
        """
        self.logger.info("Execute stop_capture")
        self.is_capturing = False
    
    def capture_video(self) -> None:
        """
        モードが有効の間、撮影したフレームを格納する
        """
        self.logger.info("Execute capture_video")
        while self.is_capturing:
            ret, frame = self.vid.read()
            if ret:
                self.frame = frame
        
    def get_frame(self) -> cv2.typing.MatLike:
        """カメラの画像を取得する
        
        Returns:
            cv2.typing.MatLike: 画像の行列
        """
        return self.frame

    def save_frame(self) -> None:
        """
        スクリーンショットした画像を保存する
        """
        self.logger.debug("Execute save_frame")
        # screenshot保存フォルダがなかった場合にフォルダを作成する
        try:
            if os.path.exists(f"{PATH}/{self.screenshot_folder_path}"):
                os.mkdir(f"{PATH}/{self.screenshot_folder_path}")
                self.logger.info(f"Success makedir {self.screenshot_folder_path}")
        except:
            self.logger.error(f"Fault makedir {self.screenshot_folder_path}")
        file_name = f"screenshot_{datetime.datetime.now().strftime('%y%m%d%H%M%S')}"
        try:
            cv2.imwrite(f"{PATH}/{self.screenshot_folder_path}/{file_name}.png", self.frame)
            print("save as {}".format(file_name))
        except:
            self.logger.error("Fault save image")

    def release(self) -> None:
        """
        カメラを開放する
        """
        self.logger.info("Execute release")
        if self.vid.isOpened():
            self.vid.release()
    
class CameraControl:
    def __init__(self, camera_capture:CameraCapture):
        self.logger = getLogger("Log").getChild("CameraControl")
        self.camera_capture = camera_capture

    def start_capture(self) -> None:
        self.logger.debug("Execute start_capture")
        self.camera_capture.start_capture()

    def stop_capture(self) -> None:
        self.logger.debug("Execute stop_capture")
        self.camera_capture.stop_capture()

    def release_camera(self) -> None:
        self.logger.debug("Execute release_camera")
        self.camera_capture.release()
    
    def save_frame(self) -> None:
        self.logger.debug("Execute save_frame")
        # print("スクリーンショット開始")
        self.camera_capture.save_frame()