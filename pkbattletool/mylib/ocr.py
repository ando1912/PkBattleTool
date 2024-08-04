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

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class OcrRunner:
    """
    キャプチャ画像に対して画像処理を行う
    .frame=処理前画像
    .cropped_frame=切り出し後画像
    .binaly_frame=二値化処理後画像
    .text=OCR分析結果
    """
    def __init__(self, camera_capture:CameraCapture):
        self.logger = getLogger("Log").getChild(f"OcrRunner")
        self.logger.info(f"Called OcrRunner")
        self.tesserac_path = config.get("DEFAULT","tesseract_path")

        self.camera_capture = camera_capture

        self.frame_forge = CameraFrameForge(camera_capture)
        
        self.frame = None
        self.framelist = []
        self.grayscale_framelist = []

        self.width = int(self.camera_capture.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera_capture.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.list_ocr_option =  {
            # メッセージボックス
            "message":{
                "thresh":200
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

    def start_ocr_thread(self):
        self.logger.getChild("start_ocr_thread").info("Execute start_ocr_thread")
        self.is_ocr_running = True
        self.ocr_thread = threading.Thread(target=self.run_ocr_thread, name="Thread OCR")
        self.ocr_thread.daemon = True
        self.ocr_thread.start()

    def stop_ocr_thread(self):
        self.logger.getChild("stop_ocr_thread").info("Execute stop_ocr_thread")
        self.is_ocr_running = False
        self.framelist = []
        self.grayscale_framelist = []
    
    def get_frame(self) -> cv2.typing.MatLike:
        """
        カメラからフレームを取得
        return:
            frame
        """
        return  self.camera_capture.get_frame()
    
    def get_framelist(self) -> list:
        self.logger.getChild("get_framelist").info("Run get_frame")
        return self.framelist

    def get_grayscale_framelist(self) -> list:
        self.logger.getChild("get_grayscale_framelist").info("Run get_grayscale_frame")

        return self.grayscale_framelist
    
    # for文実施時に処理が重くなる(画面描画が止まる)
    def get_masked_frame(self, grayscale_framelist:list,  option:str):
        logger = self.logger.getChild("masked_frame")
        logger.info("Run masked_frame")
        binary_framelist = []
        
        for grayscale_frame in grayscale_framelist:
            crop_frame = self.frame_forge.crop_frame(grayscale_frame, option)
            # 二値化
            binary_frame = self.frame_forge.binaly_frame(crop_frame, option)
            
            binary_framelist.append(binary_frame)
        # フレームの差を求める
        frame = self.frame_forge.diff_frames(binary_framelist, option)
        return frame

    def run_ocr_thread(self):
        logger = self.logger.getChild("run_ocr_thread")
        
        logger.info("Execute run_ocr_thread")
        while self.is_ocr_running:
            # 画像の取得と加工
            frame = self.get_frame() # CameraCaptureからフレームの取得
            if frame is None:
                logger.debug("Frame is None")
                continue
            # グレースケール変換
            gratscale_frame = self.frame_forge.grayscale_frame(frame)
        
            logger.debug("Append framelist")
            self.framelist.append(frame)
            self.grayscale_framelist.append(gratscale_frame)
            
            if len(self.framelist) > 5: # 規定以上の枚数になったら古いフレームから削除
                self.framelist.pop(0)
                self.grayscale_framelist.pop(0)
            
            time.sleep(0.01)

    def normalize_text(self, text:str) -> str:
        """
        記号文字などを削除する
        """
        self.logger.getChild("normalize_text").debug("Execute normalize_text")
        return re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％ 　]').sub("",text)

    def get_ocr_text(self, frame, option=str) -> str:
        logger = self.logger.getChild("get_ocr_text")
        logger.info(f"Run get_ocr_text : {option}")
        if self.tesserac_path not in os.environ["PATH"].split(os.pathsep):
            os.environ["PATH"] += os.pathsep + self.tesserac_path
        
        tools = pyocr.get_available_tools()
        tool= tools[0]

        PIL_Image = Image.fromarray(frame)
        text = tool.image_to_string(
            PIL_Image,
            lang=self.list_ocr_option[option]["lang"],
            builder=pyocr.builders.TextBuilder(tesseract_layout=6))
        
        return text
