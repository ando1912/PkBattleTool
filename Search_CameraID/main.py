import os, sys
import cv2
import time

import datetime
import argparse
from logging import getLogger, StreamHandler, INFO, DEBUG, Formatter, FileHandler

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))



def check_camera_connection_display(limit=10, save_flag=False):
    """PCに接続されたカメラを順番に確認して表示する

    Args:
        limit (int, optional): カメラIDの上限. Defaults to 10.
        save_flag (bool, optional): 画像保存のオプション. Defaults to False.
    """
    logger.info("Process Start")
    true_camera_is = []

    for camera_number in range(0, limit):# ID10まで総当り
        cap = cv2.VideoCapture(camera_number,cv2.CAP_DSHOW)

        ret, frame = cap.read()

        if ret is True:
            start = time.time()
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

            while True:
                elasped_time = time.time() - start
                _, frame = cap.read()

                if elasped_time > 3.0:
                    if save_flag :
                        # save data file
                        if not os.path.exists(f"{PATH}/results"):
                            os.mkdir(f"{PATH}/results")
                        save_data_name = f'{PATH}/results/N_{camera_number}.png'
                        cv2.imwrite(save_data_name, frame)
                        logger.info(f"Complete Save as {save_data_name}")

                    break

                cv2.imshow(f'Camera Number: {camera_number} {int(width)}x{int(height)}',frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


            cap.release()
            cv2.destroyAllWindows()

            true_camera_is.append(camera_number)
            logger.info(f"Port Number {camera_number} Find!")
            # print("port number", camera_number, "Find!")

        else:
            logger.info(f"Port Number {camera_number} None")
            print("port number", camera_number,"None")

    logger.info(f"Number of connected camera: {true_camera_is}")
    logger.info("Process END")

if __name__ == '__main__':
    # ログ設定
    logger = getLogger("Log")
    handler = StreamHandler()


    LOGGER_LEVEL = DEBUG
    HANDLER_LEVEL = DEBUG
    
    logger.setLevel(LOGGER_LEVEL)
    handler.setLevel(HANDLER_LEVEL)
    formatter = Formatter('%(asctime)s | %(levelname)s | %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    
    if not os.path.exists(f"{PATH}/logs/"):
        os.mkdir(f"{PATH}/logs")
    log_path = f"{PATH}/logs/log_{datetime.datetime.now().strftime('%y%m%d%H%M%S')}.txt"
    
    fh = FileHandler(filename=log_path)
    fh.setLevel(LOGGER_LEVEL)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("START PkBattleTool")
    
    # 引数の設定
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", help="検索するカメラIDの上限", default=10)
    parser.add_argument("-s", "--save", help="画像の保存", action="store_true")
    args = parser.parse_args()
    
    check_camera_connection_display(limit=int(args.limit), save_flag=args.save)