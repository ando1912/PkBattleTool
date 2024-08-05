import os, sys
import cv2

from threading import Thread
import datetime
from logging import getLogger

from module import config

import numpy as np

class CameraCapture:
    """
    カメラキャプチャの管理
    """
    def __init__(self) -> None:
        self.logger = getLogger("Log").getChild("CameraCapture")

        self.video_source:int = int(config.get("DEFAULT","camera_id"))
        self.vid = cv2.VideoCapture(self.video_source)

        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.vid.set(cv2.CAP_PROP_FPS, int(config.get("DEFAULT","display_fps")))
        
        self.screenshot_folder_path = config.get("DEFAULT","screenshot_folder")

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.display_fps = self.vid.get(cv2.CAP_PROP_FPS)
        
        self.logger.info(f"CameraConfig : w{self.width:.2f} x h{self.height:.2f} / {self.display_fps:.2f}fps")

        self.is_capturing:bool = False
        self.capture_thread:Thread = None
        self.frame:cv2.typing.MatLike = None
    
    
    def start_capture(self) -> None:
        """
        カメラの撮影を開始する
        """
        self.logger.getChild("start_capture").info("Execute start_capture")
        self.is_capturing= True
        self.capture_thread = Thread(target=self.capture_video)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def stop_capture(self) -> None:
        """
        カメラの撮影を停止する
        """
        self.logger.getChild("stop_capture").info("Execute stop_capture")
        self.is_capturing = False
    
    def capture_video(self) -> None:
        """
        モードが有効の間、撮影したフレームを格納する
        """
        logger = self.logger.getChild("capture_video")
        logger.info("Execute capture_video")
        while self.is_capturing:
            logger.debug("VideoCapture.read")
            ret, frame = self.vid.read()
            if ret:
                logger.debug("save frame")
                self.frame = frame
            
    def get_frame(self) -> np.ndarray:
        """カメラの画像を取得する
        
        Returns:
            ndarray: 画像
        """
        
        
        return self.frame

    def save_frame(self) -> None:
        """
        スクリーンショットした画像を保存する
        """
        logger = self.logger.getChild("save_frame")
        logger.debug("Execute save_frame")
        # screenshot保存フォルダがなかった場合にフォルダを作成する
        try:
            if os.path.exists(f"{self.screenshot_folder_path}"):
                os.mkdir(f"{self.screenshot_folder_path}")
                logger.info(f"Success makedir {self.screenshot_folder_path}")
        except Exception as e:
            logger.error(f"Fault makedir {self.screenshot_folder_path}")
            logger.exception(e)
        file_name = f"screenshot_{datetime.datetime.now().strftime('%y%m%d%H%M%S')}"
        try:
            cv2.imwrite(f"{self.screenshot_folder_path}/{file_name}.png", self.frame)
            print("save as {}".format(file_name))
        except Exception as e:
            self.logger.error(f"Fault save image")
            self.logger.exception(e)

    def release_camera(self) -> None:
        """
        カメラを開放する
        """
        self.logger.info("Execute release")
        if self.vid.isOpened():
            self.vid.release()
        self.video.release()