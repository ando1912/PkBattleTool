import os, sys
import pandas as pd
from logging import getLogger

PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class PkTypeCompatibility:
    def __init__(self):
        filename = f"{PATH}/poketype.csv" 
        self.typedf = pd.read_csv(filename, index_col="atacktype")
        self.logger = getLogger("Log").getChild("PkTypeCompatibility")
        self.logger.debug("Hello PkTypeCompatibility")
    
    def type_compatibility(self, atacktype:str, diffencetype:str) -> float:
        """
        攻撃側のタイプ相性
        Arg:
        atacktype:攻撃側タイプ
        diffencetype:防御側タイプ
        Return：
        (float):攻撃倍率
        """
        self.logger.debug("Execuse type_compatibility")
        return self.typedf[diffencetype].loc[atacktype]

    def multipletype_compatibility(self, atacktype:str, diffencetype1:str, diffencetype2:str) -> float:
        """
        Arg:
        atacktype:攻撃側タイプ
        diffencetype1:防御側タイプ1
        diffencetype2:防御側タイプ2
        Return
        (float):攻撃倍率
        """
        self.logger.debug("Execuse tmultipletype_compatibility")
        comp1 = self.type_compatibility(atacktype, diffencetype1)
        comp2 = self.type_compatibility(atacktype, diffencetype2)
        return comp1*comp2

    def effectivetype(self,diffencetype1, diffencetype2=None):
        """
        防御側の相性を計算
        Arg:
        diffencetype1(str):タイプ1
        diffencetype2(str):タイプ2
        Return:
        dataframe:タイプ相性のデータフレーム
        例：dataframe[atacktype]->atacktypeの攻撃倍率

        """
        self.logger.debug("Execuse tmultipletype_compatibility")
        df1 = self.typedf[diffencetype1] # タイプ1の相性
        if diffencetype2 == None:
            return df1
        df2 = self.typedf[diffencetype2] # タイプ2の相性
        return df1*df2