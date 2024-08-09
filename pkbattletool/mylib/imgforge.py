import os, sys
import cv2
from logging import getLogger
import numpy as np
from .webcam_capture import CameraCapture

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class CameraFrameForge():
    def __init__(self,camera_capture:CameraCapture) -> None:
        """ゲーム画像の切抜き

        Args:
            camera_capture (CameraCapture): カメラキャプチャ
        """
        self.logger = getLogger("Log").getChild("CameraFrameForge")
        self.logger.debug("Called CameraFrameForge")

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


    def crop_frame(self, frame:np.ndarray, option:str) -> np.ndarray:
        """画像の切抜き

        Args:
            frame (np.ndarray): 画像の切り出し
            option (str): 切抜きのオプション

        Returns:
            np.ndarray: 切抜き後の画像
        """
        logger = self.logger.getChild("crop_frame")
        logger.debug(f"Run crop_frame({option})")
        top = self.options[option]["top"]
        bottom = self.options[option]["bottom"]
        left = self.options[option]["left"]
        right = self.options[option]["right"]

        return frame[top:bottom,left:right]

    def cvt_bgr2gray(self, frame:np.ndarray) -> np.ndarray:
        """画像のグレースケール処理

        Args:
            frame (np.ndarray): 変換前画像

        Returns:
            np.ndarray: 変換後画像
        """
        
        logger = self.logger.getChild("cvt_bgr2gray")
        logger.debug("Run cvt_bgr2gray")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def cvt_gray2binaly(self, grayscale_frame: np.ndarray, option:str) -> np.ndarray:
        """画像の二値化処理

        Args:
            grayscale_frame (np.ndarray): 変換前のグレースケール画像
            option (str): オプション

        Returns:
            np.ndarray: 変換後画像
        """
        logger = self.logger.getChild("cvt_gray2binaly")
        logger.debug("Run cvt_gray2binaly")
        _, binaly_frame = cv2.threshold(grayscale_frame, self.options[option]["thresh"], 255, cv2.THRESH_BINARY)
        return binaly_frame
    
    def diff_frames(self, frame_list:list[np.ndarray], option:str) -> np.ndarray:
        """画像の共通部分抽出

        Args:
            frame_list (list[np.ndarray]): フレームリスト
            option (str): オプション

        Returns:
            np.ndarray: 処理後画像
        """
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
    
    def save_frame(self, frame:np.ndarray, filename:str) -> None:
        """
        Arg:
            frame (np.ndarray):保存したいフレーム
            file_name (str):ファイル名、要拡張子
        """
        try:
            cv2.imwrite("{}".format(filename),frame)
            self.logger.info(f"Save image to {filename}")
        except Exception as e:
            self.logger.error(f"Fault save image : {e}")