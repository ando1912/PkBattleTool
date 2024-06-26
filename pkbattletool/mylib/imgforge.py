import cv2
from logging import getLogger

from mylib import CameraCapture

class CameraFrameForge():
    def __init__(self,camera_capture:CameraCapture, option:str) -> None:
        self.logger = getLogger("Log").getChild("ImgCrop")
        self.logger.debug("Hello ImgCrop")

        self.width = int(camera_capture.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(camera_capture.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.optionlist =  {
            "message":{
                "top":int(self.height/14*10),
                "bottom":int(self.height/14*12),
                "left":int(self.width/8),
                "right":int(self.width/8*7),
                "bgr":[230,230,230],
                "thresh":200},
            "namebox":{
                "top":int(self.height/22*2),
                "bottom":int(self.height/22*3),
                "left":int(self.width/20*16),
                "right":int(self.width/20*19),
                "bgr":[230,230,230],
                "thresh":240},
            "pokemonbox":{
                "top":int(self.height*0.212),#0.212),
                "bottom":int(self.height*0.773),#0.772),
                "left":int(self.width*0.642),#0.642),
                "right":int(self.width*0.697+420),#0.697),
                "bgr":[230,230,230],
                "thresh":220}
        }

        self.option = self.optionlist[option]

    def crop_frame(self, frame):
        """
        画像の切り出し
        Return
            frame:切り出し後のフレーム
        """
        
        self.logger.debug("Execute crop_frame")
        top = self.option["top"]
        bottom = self.option["bottom"]
        left = self.option["left"]
        right = self.option["right"]

        self.logger.debug(f"top:{top} / bottom:{bottom} / left:{left} / right:{right}")

        return frame[top:bottom,left:right]

    def grayscale_frame(self,frame):
        """
        画像のグレースケール処理
        """
        self.logger.debug("Execute grayscale_frame")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def binaly_frame(self,frame):
        """
        画像の二値化処理
        """
        self.logger.debug("Execute binaly_frame")
        _, binaly_frame = cv2.threshold(frame, self.option["thresh"], 255, cv2.THRESH_BINARY)
        return binaly_frame
    