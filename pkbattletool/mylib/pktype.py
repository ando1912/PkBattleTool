import os, sys
import pandas as pd
from logging import getLogger

class PkTypeCompatibility:
    def __init__(self):
        filename = f"resources/poketype.csv"
        self.typedf = pd.read_csv(filename, index_col="atacktype")
        self.logger = getLogger("Log").getChild("PkTypeCompatibility")
        self.logger.debug("Called PkTypeCompatibility")
    
    def type_compatibility(self, atacktype:str, diffencetype:str) -> float:
        """タイプ相性の参照

        Args:
            atacktype (str): 攻撃側のタイプ
            diffencetype (str): 防御側のタイプ

        Returns:
            float: 攻撃倍率
        """
        self.logger.getChild("type_compatibility").debug("Run type_compatibility")
        return self.typedf[diffencetype].loc[atacktype]

    def multipletype_compatibility(self, atacktype:str, diffencetype1:str, diffencetype2:str) -> float:
        """複合タイプのタイプ相性計算

        Args:
            atacktype (str): 攻撃側のタイプ
            diffencetype1 (str): 防御側のタイプ1
            diffencetype2 (str): 防御側のタイプ2

        Returns:
            float: 攻撃倍率
        """
        self.logger.getChild("multipletype_compatibility").debug("Run tmultipletype_compatibility")
        comp1 = self.type_compatibility(atacktype, diffencetype1)
        comp2 = self.type_compatibility(atacktype, diffencetype2)
        return comp1*comp2

    def effectivetype(self, diffencetype1:str, diffencetype2:str = None) -> pd.Series:
        """複合タイプの相性の参照

        Args:
            diffencetype1 (str): タイプ1
            diffencetype2 (str, optional): タイプ2. Defaults to None.

        Returns:
            pd.Series: タイプ相性
        """
        self.logger.getChild("effectivetype").debug("Execuse tmultipletype_compatibility")
        df1 = self.typedf[diffencetype1] # タイプ1の相性
        if diffencetype2 == None:
            return df1
        df2 = self.typedf[diffencetype2] # タイプ2の相性
        return df1*df2