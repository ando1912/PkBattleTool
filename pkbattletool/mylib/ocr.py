"""
OCR実行処理をまとめたクラス

"""

import os, sys

import cv2
import numpy as np

import pyocr
from PIL import Image

import threading
import re
from logging import getLogger

import time

from .imgforge import CameraFrameForge
from .webcam_capture import CameraCapture
from module import config

class OcrRunner:
    def __init__(self, camera_capture:CameraCapture):
        """OCR処理のクラス

        Args:
            camera_capture (CameraCapture): カメラキャプチャー
        """
        self.logger = getLogger("Log").getChild(f"OcrRunner")
        self.logger.info(f"Called OcrRunner")

        self.tesserac_path = config.get("DEFAULT","tesseract_path")
        self.camera_capture = camera_capture

        self.frame_forge = CameraFrameForge(camera_capture)
        
        # tesserac_pathの設定
        if self.tesserac_path not in os.environ["PATH"].split(os.pathsep):
            os.environ["PATH"] += os.pathsep + self.tesserac_path
        
        self.tools = pyocr.get_available_tools()
        self.tool = self.tools[0]
        
        self.frame = None
        self.framelist = []
        self.grayscale_framelist = []


        self.width = int(self.camera_capture.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera_capture.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.list_ocr_option =  {
            # メッセージボックス
            "message":{
                "thresh":200,
                "lang":"jpn"
                },
            "level":{
                "thresh":100,
                "lang":"eng"
                },
            "namebox":{
                "thresh":180,
                "lang":"jpn+eng"
                },
            # FIXME:カジュアルバトルの場合もあり、その場合、幅が異なる
            "rankbattle":{
                "thresh":200,
                "lang":"jpn"
                }
            }

        self.text = None

        self.is_ocr_running = False

        self.ocr_thread = None

    def close(self) -> None:
        """
        終了時の処理
        """
        self.stop_ocr_thread()
        self.logger.info("Close OcrRunner")
        
    def start_ocr_thread(self) -> None:
        """
        スレッド開始処理
        """

        self.logger.getChild("start_ocr_thread").info("Run start_ocr_thread")

        self.is_ocr_running = True
        self.ocr_thread = threading.Thread(target=self.run_ocr_thread, name="Thread OCR")
        self.ocr_thread.daemon = True
        self.ocr_thread.start()

    def stop_ocr_thread(self) -> None:
        """
        スレッド停止処理
        """
        self.logger.getChild("stop_ocr_thread").info("Run stop_ocr_thread")
        self.is_ocr_running = False
        
        self.framelist = []
        self.grayscale_framelist = []
    

    def get_frame(self) -> np.ndarray:

        """
        カメラからフレームを取得
        return:
            frame[np.ndarray] : 最新のカメラフレーム
        """
        return  self.camera_capture.get_frame()
    
    def get_framelist(self) -> list[np.ndarray]:
        """フレームリストの取得

        Returns:
            list[np.ndarray]: カメラフレームが入ったリスト
        """
        self.logger.getChild("get_framelist").info("Run get_frame")
        return self.framelist

    def get_grayscale_framelist(self) -> list[np.ndarray]:
        """グレースケールフレームリストの取得

        Returns:
            list[np.ndarray]: グレースケール変換されたフレームが入ったリスト
        """
        self.logger.getChild("get_grayscale_framelist").info("Run get_grayscale_frame")

        return self.grayscale_framelist

    
    # for文実施時に処理が重くなる(画面描画が止まる)
    def get_masked_frame(self, grayscale_framelist:list[np.ndarray],  option:str) -> np.ndarray:
        """画像の共通部分を抽出したフレームの取得

        Args:
            grayscale_framelist (list[np.ndarray]): グレースケール変換されたフレームリスト
            option (str): 変換オプション

        Returns:
            frame (np.ndarray): マスク処理をした画像
        """
        logger = self.logger.getChild("masked_frame")
        logger.info("Run masked_frame")
        binary_framelist = []
        
        for grayscale_frame in grayscale_framelist:
            crop_frame = self.frame_forge.crop_frame(grayscale_frame, option)
            # 二値化
            binary_frame = self.frame_forge.cvt_gray2binaly(crop_frame, option)
            
            binary_framelist.append(binary_frame)
        # フレームの差を求める
        frame = self.frame_forge.diff_frames(binary_framelist, option)
        return frame

    def run_ocr_thread(self) -> None:
        """
        OCRスレッドの開始処理
        """
        logger = self.logger.getChild("run_ocr_thread")
        
        logger.info("Run run_ocr_thread")
        while self.is_ocr_running:
            # 画像の取得と加工
            frame = self.get_frame() # CameraCaptureからフレームの取得
            if frame is None:
                logger.debug("Frame is None")
                continue
            # グレースケール変換
            gratscale_frame = self.frame_forge.cvt_bgr2gray(frame)
        
            logger.debug("Append framelist")
            self.framelist.append(frame)
            self.grayscale_framelist.append(gratscale_frame)
            
            if len(self.framelist) > 10: # 規定以上の枚数になったら古いフレームから削除
                self.framelist.pop(0)
                self.grayscale_framelist.pop(0)
            
            time.sleep(0.01)

    def normalize_text(self, text:str) -> str:
        """
        OCRで取得したテキストから記号等を削除する
        参考:https://qiita.com/ganyariya/items/42fc0ed3dcebecb6b117
        
        Args:
            text (str): 処理前のテキスト

        Returns:
            str: 処理後のテキスト
        """

        self.logger.getChild("normalize_text").debug("Run normalize_text")
        return re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％ 　]').sub("",text)

    # FIXME: 実行時に動作が重くなる
    def get_ocr_text(self, frame:np.ndarray, option:str) -> str:
        """画像に対してOCRでテキストを取得する

        Args:
            frame (np.ndarray): テキストを取得したい画像
            option (str): 認識オプション

        Returns:
            str: 認識したテキスト
        """

        logger = self.logger.getChild("get_ocr_text")
        logger.info(f"Run get_ocr_text : {option}")

        PIL_Image = Image.fromarray(frame)
        text = self.tool.image_to_string(
            PIL_Image,
            lang=self.list_ocr_option[option]["lang"],
            builder=pyocr.builders.TextBuilder(tesseract_layout=6))
        
        text = self.normalize_text(text)
        
        return text
