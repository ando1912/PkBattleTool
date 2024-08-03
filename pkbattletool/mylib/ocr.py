import cv2
import os, sys
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
    # BUG:スレッドを終了しないままウィンドウを閉じるとプロセスが終わらない
    def __init__(self, camera_capture:CameraCapture):
        self.logger = getLogger("Log").getChild(f"OcrRunner")
        self.logger.info(f"Called OcrRunner")
        self.tesserac_path = config.get("DEFAULT","tesseract_path")

        self.camera_capture = camera_capture

        self.frame_forge = CameraFrameForge(camera_capture)
        
        self.frame = None
        self.frame_list = []
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

        self.ocr_name_thread = None

    def start_ocr_thread(self):
        self.logger.getChild("start_ocr_thread").info("Execute start_ocr_thread")
        self.is_ocr_running = True
        self.ocr_name_thread = threading.Thread(target=lambda:self.run_ocr_thread())
        self.ocr_name_thread.start()

    def stop_ocr_thread(self):
        self.logger.getChild("stop_ocr_thread").info("Execute stop_ocr_thread")
        self.is_ocr_running = False
        self.frame_list = []
        self.grayscale_framelist = []

    def run_ocr_thread(self):
        logger = self.logger.getChild("run_ocr_thread")
        
        logger.info("Execute run_ocr_thread")
        while self.is_ocr_running:
            # 画像の取得と加工
            ret, frame = self.get_frame() # CameraCaptureからフレームの取得
            if not ret:
                break
            # crop_frame = self.frame_forge.crop_frame(frame) # フレームの切り抜き
            # グレースケール変換
            gratscale_frame = self.frame_forge.grayscale_frame(frame)
        
            self.frame_list.append(frame)
            self.grayscale_framelist.append(gratscale_frame)
            
            
            
            if len(self.frame_list) > 5: # 規定以上の枚数になったら古いフレームから削除
                self.frame_list.pop(0)
                self.grayscale_framelist.pop(0)
                # for i, img in enumerate(self.frame_list):
                #     cv2.imwrite(f"{i}.png", img)
                
            
            # text = self.run_ocr(self.frame)
            # self.text = self.normalize_text(text)
            # logger.debug(f"OCR result : {self.text}")
            time.sleep(0.05)

    def normalize_text(self, text:str) -> str:
        """
        記号文字などを削除する
        """
        self.logger.getChild("normalize_text").debug("Execute normalize_text")
        return re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％ 　]').sub("",text)

    def get_frame(self):
        """
        カメラからフレームを取得
        return:
            frame
        """
        return  self.camera_capture.get_frame()

    def masked_frame(self, option:str, grayscale_framelist=None):
        logger = self.logger.getChild("masked_frame")
        logger.info("Run masked_frame")
        if grayscale_framelist is None:
            grayscale_framelist = self.grayscale_frame_list
        binary_frame_list = []
        
        for grayscale_frame in grayscale_framelist:
            crop_frame = self.frame_forge.crop_frame(grayscale_frame, option)
            # 二値化
            binary_frame = self.frame_forge.binaly_frame(crop_frame, option)
            
            binary_frame_list.append(binary_frame)
        # フレームの差を求める
        return self.frame_forge.diff_frames(binary_frame_list, option)

    def run_ocr(self, frame, option=str) -> str:
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

class OcrControl:
    """
    OcrRunnerを組み合わせて処理を行う
    """
    def __init__(self, ocr_runner:OcrRunner):
        self.logger = getLogger("Log").getChild(f"OcrControl")
        self.ocr_runner = ocr_runner
        self.activemode = False

    def start_ocr_thread(self):
        self.ocr_runner.start_ocr_thread()
        self.activemode = True
        self.logger.getChild("start_ocr_thread").info("Start ocr thread")

    def stop_ocr_thread(self):
        self.ocr_runner.stop_ocr_thread()
        self.activemode = False
        self.logger.getChild("stop_ocr_thread").info("Stop ocr thread")

    def get_frame_list(self):
        self.logger.getChild("get_frame_list").info("Run get_frame")
        if len(self.ocr_runner.frame_list) == 0:
            return [self.ocr_runner.get_frame()]
        else:
            return self.ocr_runner.frame_list
        
    def get_grayscale_framelist(self):
        self.logger.getChild("get_grayscale_frame_list").info("Run get_grayscale_frame")
        if len(self.ocr_runner.grayscale_framelist)==0:
            return [cv2.cvtColor(self.get_frame(), cv2.COLOR_BGR2GRAY)]
        else:
            return self.ocr_runner.grayscale_framelist

    def get_frame(self):
        self.logger.getChild("get_frame").info("Run get_frame")
        if self.ocr_runner.frame is None:
            return self.ocr_runner.get_frame()
        else:
            return self.ocr_runner.frame
    
    def get_mask_frame(self, frame_list, option:str):
        self.logger.getChild("get_mask_frame").info(f"Get masked frame : {option}")
        frame = self.ocr_runner.masked_frame(option, frame_list)
        return frame

    def get_ocrtext(self, frame, option:str, ):
        self.logger.getChild("get_ocrtext").info(f"Get ocrtext : {option}")
        text = self.ocr_runner.run_ocr(frame=frame, option=option)
        return text
