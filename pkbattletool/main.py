import tkinter as tk
import os,sys
from logging import getLogger, StreamHandler, DEBUG, Formatter, FileHandler

from mylib import OcrRunner, CameraCapture
from gui import MenuBar, PKInfo, CanvasGame, CaptureControl, CanvasPkBox

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

def gui_main():
    # TODO: ウィンドウを開く位置を前回の位置にしたい
    root = tk.Tk()
    width = 1400 #660
    height = 900
    # root.geometry("{}x{}".format(width,height))
    # root.minsize(width=width,height=height)
    # root.maxsize(width=width,height=height)
    root.title("ポケモン対戦支援ツール")

    menuber = MenuBar(root)
    camera_capture = CameraCapture()
    # namebox_ocr_runner = OcrRunner(camera_capture, ocr_option="namebox")
    # pokemonbox_ocr_runner = OcrRunner(camera_capture, ocr_option="pokemonbox")

    # フレームウェジットの作成
    frame_pkinfo = PKInfo(root, camera_capture, bd=1, relief=tk.SOLID)
    frame_canvasgame = CanvasGame(root, camera_capture, bd=2, relief=tk.SOLID)
    frame_capturecontrol = CaptureControl(root, camera_capture, bd=1, relief=tk.SOLID)
    frame_canvaspkbox = CanvasPkBox(root, camera_capture, bd=2, relief=tk.SOLID)

    # ウェジットの配置
    frame_pkinfo.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
    frame_canvasgame.grid(row=1, rowspan=2, column=0, columnspan=2, padx=5, pady=5)
    frame_capturecontrol.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)
    frame_canvaspkbox.grid(row=0, column=2, rowspan=3, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

    def click_close():
        frame_capturecontrol.camera_control.stop_capture()
        frame_capturecontrol.camera_control.release_camera()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", click_close)

    root.mainloop()

def main():
    # ログ設定
    logger = getLogger("Log")
    handler = StreamHandler()

    logger.setLevel(DEBUG)
    handler.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    fh = FileHandler(filename=f"{PATH}/log.txt")
    fh.setLevel(DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.debug("Hello main")

    gui_main()

if __name__ == "__main__":
    main()