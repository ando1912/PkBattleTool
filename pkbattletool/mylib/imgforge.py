import os, sys
import cv2
from logging import getLogger
import numpy as np
from .webcam_capture import CameraCapture

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class CameraFrameForge():
    """
    ゲーム画面の切り抜きに関するクラス
    option:message/namebox/pokemonbox
    """
    def __init__(self,camera_capture:CameraCapture) -> None:
        self.logger = getLogger("Log").getChild("CameraFrameForge")
        self.logger.debug("Hello CameraFrameForge")

        self.width = int(camera_capture.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(camera_capture.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.options = {
            "message":{
                "top":int(self.height/14*10),
                "bottom":int(self.height/14*12),
                "left":int(self.width/8),
                "right":int(self.width/8*7),
                "thresh":200},
            "level":{
                "top":int(self.height*0.045),
                "bottom":int(self.height*0.082),
                "left":int(self.width*0.802),
                "right":int(self.width*0.880),
                "thresh":100},
            "namebox":{
                "top":int(self.height*0.091),
                "bottom":int(self.height*0.130),
                "left":int(self.width*0.799),
                "right":int(self.width*0.951),
                "thresh":180},
            "pokemonbox":{
                "top":int(self.height*0.213),
                "bottom":int(self.height*0.774),
                "left":int(self.width*0.642),
                "right":int(self.width*0.697),
                "thresh":180},
            "rankbattle":{
                "top":int(self.height*0.017),
                "bottom":int(self.height*0.058),
                "left":int(self.width*0.075),
                "right":int(self.width*0.188),
                "thresh":200}
            }


    def crop_frame(self, frame, option:str):
        """
        画像の切り出し
        Return
            frame:切り出し後のフレーム
        """
        logger = self.logger.getChild("crop_frame")
        logger.debug("Run crop_frame")
        top = self.options[option]["top"]
        bottom = self.options[option]["bottom"]
        left = self.options[option]["left"]
        right = self.options[option]["right"]

        self.logger.debug(f"top:{top} / bottom:{bottom} / left:{left} / right:{right}")

        return frame[top:bottom,left:right]

    def cvt_bgr2gray(self, frame:np.ndarray):
        """
        画像のグレースケール処理
        """
        logger = self.logger.getChild("grayscale_frame")
        logger.debug("Run cvt_bgr2gray")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def cvt_gray2binaly(self, grayscale_frame: np.ndarray, option:str):
        """
        画像の二値化処理
        """
        logger = self.logger.getChild("binaly_frame")
        logger.debug("Run cvt_gray2binaly")
        _, binaly_frame = cv2.threshold(grayscale_frame, self.options[option]["thresh"], 255, cv2.THRESH_BINARY)
        return binaly_frame
    
    def diff_frames(self, frame_list:list[np.ndarray], option:str) -> np.ndarray:
        logger = self.logger.getChild("diff_frames")
        logger.debug("Run diff_frames")
        
        base_img = frame_list[0]
        for image in frame_list[1:]:
            # 画像の差分を計算
            diff = cv2.absdiff(base_img, image)
            # 共通部分のマスクを作成
            _, mask = cv2.threshold(diff, self.options[option]["thresh"], 255, cv2.THRESH_BINARY_INV)
            base_img = cv2.bitwise_and(base_img, base_img, mask=mask)
        return base_img
    
    def save_frame(self, frame:np.ndarray, filename:str):
        """
        Arg:
            frame:保存したいフレーム
            file_name:ファイル名、要拡張子
        """
        try:
            cv2.imwrite("{}".format(filename),frame)
            self.logger.info(f"Save image to {filename}")
        except Exception as e:
            self.logger.error(f"Fault save image : {e}")