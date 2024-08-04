"""
参考引用：https://note.com/kaseki_mtg/n/n6df12de8981a
作者：暇士
"""
import os, sys

import cv2
from logging import getLogger
sys.path.append(".")
from module import pkcsv

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class PkHash:
    def __init__(self):
        self.logger = getLogger("Log").getChild("PkHash")
        self.logger.info("Called PkHash")

        self.crop_frame = None # ポケモン一覧画像

    # ポケモン画像解析
    def RecognitionPokemonImages(self, crop_frame:cv2.typing.MatLike) -> tuple[list, list, list, list]:
        """
        手持ちの画像を6枚に分割する
        Return:
            keylist[str]:図鑑番号
            dislist[int]:編集距離
            cutframelist[MatLike]:6分切り出し画像
            outline_iconlist[MatLike]:輪郭切り出し画像
        """
        logger = self.logger.getChild("RecognitionPokemonImages") # loggerの設定
        logger.debug("Execute RecognitionPokemonImages")
        height, width, _ = crop_frame.shape[:3]

        img_pokemon_height = int(height / 6)

        # リストの初期化
        keylist: list[str] = []
        dislist:list[int] = []
        cutframelist = []
        outline_iconllist = []
        for i in range(0, 6):
            y = int(height / 6 * i)
            cut_frame = crop_frame[y:y+img_pokemon_height, 0:width]
            cutframelist.append(cut_frame)
            
            outline_frame = self.GetImageByAllContours(cut_frame)
            # BUG: 輝度が高いとうまくいかない可能性がある
            outline_iconllist.append(outline_frame)
            key, distance = self.GetPokemonNameFromImage(outline_frame)
            keylist.append(key)
            logger.debug(f"Success keylist.append({key})")
            dislist.append(distance)
            logger.debug(f"Success dislist.append({distance})")
            logger.info(f"Complete CutFrame : {key}")
        logger.error("Fault to run cut_frame")
        return keylist, dislist, cutframelist, outline_iconllist

    def GetPokemonNameFromImage(self, frame: cv2.typing.MatLike) -> tuple[str,int]:
        """
        輪郭短形で切り出したポケモン画像と最もdHash値が近い画像を探す
        
        Arg:
            frame:cv2の画像フレーム
        Return:
            index[str]:最小キー
            distance[int]:Hash値の編集距離
        """
        logger = self.logger.getChild("GetPokemonNameFromImage")
        logger.debug("Execute GetPokemonNameFromImage")

        dhash: str = self.CalcPerceptualDhash(frame)
        dic: dict[str, int] = {}
        pokemon_df = pkcsv.get_df()
        for index, row in pokemon_df.dropna(subset=["Hash"]).iterrows():
            # 差分の計算
            distance = self.CalcHammingDistance(dhash, row["Hash"])
            dic[index] = distance
            if distance <= 8:
                logger.debug(f"Found key={index}/distance={distance}")
                return index, distance

        # 距離が最小の物を返す
        min_key = min(dic.items(), key=lambda x: x[1])[0]
        logger.debug(f"Nearly key={min_key}/distance={dic[min_key]}")
        return min_key, dic[min_key]

    def CalcHammingDistance(self, hash1: str, hash2: str) -> int:
        """
        dHash差分を計算
        
        Return:
            result[int]:2つのdHashの差分の数
        """
        # ループ内処理のためログ出力を省略
        # self.logger.debug("Execute CalcHammingDistance")
        # print(f"hash1={type(hash1)}/hash2={type(hash2)}")
        # print(hash2)
        result: int = 0
        for i in range(len(hash1)):
            if hash1[i] != hash2[i]:
                result += 1
        return result

    def CalcPerceptualDhash(self, frame: cv2.typing.MatLike) -> str:
        """
        画像のdHashを算出する
        """
        self.logger.debug("Execute CalcPercepturalDhash")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(src=gray, dsize=(9, 8), interpolation=cv2.INTER_AREA)

        dhash:str = ""
        for y in range(0, 8):
            for x in range(0, 8):
                dhash += "1" if resized[y, x] > resized[y, x+1] else "0"

        return dhash

    def GetImageByAllContours(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        # FIXME: フレーム上下の境界ラインが接触してしまい、トリミングに失敗する場合がある
        """
        画像内の全ての輪郭に外接する長方形を切り出す
        """
        logger = self.logger.getChild("GetImageByAllContours")
        logger.debug("Execute GetImageByAllContours")
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 閾値が低いと、輝度の高いポケモンのアイコンを認識しなくなる
        try:
            _, binary_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            cv2.waitKey(0)
            contours = self.FindContours(binary_img)
        except:
            _, binary_img = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY_INV)
            cv2.waitKey(0)
            contours = self.FindContours(binary_img)

        rect = {"x1": 999999, "x2": -1, "y1": 999999, "y2": -1}
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            rect = {"x1": min(rect["x1"], x),
                    "x2": max(rect["x2"], x + w),
                    "y1": min(rect["y1"], y),
                    "y2": max(rect["y2"], y + h),
                    }

        return frame[rect["y1"]:rect["y2"], rect["x1"]:rect["x2"]]

    def FindContours(self, binary_img:cv2.typing.MatLike):
        """
        輪郭抽出
        """
        self.logger.debug("Execute FindContours")
        # 輪郭の抽出
        # cv2.RETR_EXTERNAL = 最も外側の輪郭のみ抽出する
        # cv2.CHAIN_APPROX_SIMPLE = 必要最小限の点を検出する
        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

def debug_PkCSV() -> None:
    csv = pkcsv.PkCSV()
    key="1000"
    print(csv.pokemon_df[key:key][["Type1","Type2"]])
    #print(pkcsv.pokemon_df.head(5))

def debug_PkHash() -> None:
    pkhash = PkHash()
    keylist,dislist,_,_ = pkhash.RecognitionPokemonImages(cv2.imread(f"{PATH}/debug/screenshot_240105101126.png"))
    print(keylist,dislist)
    csv = pkcsv.PkCSV()
    df2 = csv.pokemon_df.loc[keylist]
    print(df2)

if __name__ == "__main__":
    PATH = os.path.abspath(os.path.join(PATH, os.pardir))
    debug_PkHash()