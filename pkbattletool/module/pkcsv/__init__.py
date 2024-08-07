import os, sys
import pandas as pd
import Levenshtein
from logging import getLogger

class PkCSV:
    def __init__(self):
        self.logger = getLogger("Log").getChild("PkCSV")
        self.logger.debug("Hello PkCSV")
        
        # csvデータファイル
        self.filename = f"resources/pokedb_SV.csv"
        
        self.pokemon_df = None

        # csvの読み込み
        self.RoadCSV()

    def RoadCSV(self):
        """
        CSVをロード
        欠損値はNone
        """
        self.pokemon_df = pd.read_csv(self.filename, index_col="Key", dtype={
            "Key":"object","Index":"int","Name":"str","Form":"str","Type1":"str","Type2":"str",
            "Ability1":"str","Ability2":"str","HAbility":"str","HP":"int","Atk":"int","Def":"int",
            "SpA":"int","SpD":"int","Spe":"int","Tot":"int","Hash":"str"},encoding = "shift-jis",keep_default_na=False).replace({"":None})
        self.logger.debug("Load pokedb_SV.csv")
        # print(self.pokemon_df.head(5))
    
    def WriteCSV(self, new_df):
        new_df.to_csv(self.filename, mode="w", encoding="shift-jis")
    
    def Name_search2csv(self, name:str) -> pd.DataFrame:
        """
        ポケモン名をcsvファイルと照合し、合致するデータフレームを返す
        名前が見つからなければ、類似度検索をする
        
        Arg:
            name[str] :  ポケモンの名前
        Return:
            dataframe|None
        """
        logger = self.logger.getChild("Name_search2csv")
        logger.info(f"Call Search to csv-data : {name}")
        
        if name is None:
            return pd.DataFrame()
        else:
            # 図鑑のデータフレーム内に名前が見つかれば、そのまま返す
            if name in self.pokemon_df["Name"].values:
                result_df = self.pokemon_df[self.pokemon_df["Name"]==name]
                logger.info(f"{name} was found")
                return result_df
            # 見つからなければ、類似検索をかける
            else:
                logger.info(f"{name} was not found")
                return self.analyze_name(name)
    
    def analyze_name(self,name:str) -> pd.DataFrame:
        """
        与えられたポケモン名をcsvと照合し、類似する名前のデータフレームを返す
        
        Arg:
            name[str]: 検索したいポケモン名
        Return:
            dataframe|None
        """
        logger = self.logger.getChild("analyze_name")
        logger.info("Call analyze_name")
        if name is not None and name != "":
            logger.debug(f"Analyze name is \"{name}\"")
            
            min_distance = 99
            max_ratio = 0
            min_distance_Key = None
            max_ratio_Key = None

            for index, row in self.pokemon_df.iterrows():
                # 編集距離の計算
                name_distance = Levenshtein.distance(name, row.Name)
                if min_distance > name_distance:
                    min_distance = name_distance
                    min_distance_Key = index
                # 類似度の計算
                name_ratio = Levenshtein.ratio(name, row.Name)
                if max_ratio < name_ratio:
                    max_ratio = name_ratio
                    max_ratio_Key = index

            # 編集距離と類似度分析でのインデックスが一致
            if min_distance_Key == max_ratio_Key:
                return self.pokemon_df.loc[[min_distance_Key]]
            else:
                return pd.DataFrame()


_util = PkCSV()

def get_df():
    return _util.pokemon_df

def get_series(key):
    return _util.pokemon_df.loc[key]

def write_csv(new_df):
    _util.WriteCSV(new_df)