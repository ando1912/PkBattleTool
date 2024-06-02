import pandas as pd
import os

type_EN = ["Normal","Fire","Water","Electric","Grass","Ice","Fighting","Poison","Ground","Flying","Psychic",
               "Bug","Rock","Ghost","Dragon","Dark","Steel","Fairy"]

# ポケモンの情報を格納するクラス
class Pokemon():
    def __init__(self, id):
        self.id: int = id
        self.name: str = None
        self.type1: int = None
        self.type2: int = None

        self.move1: int = None
        self.move2: int = None
        self.move3: int = None
        self.move4: int = None

    def setinfo(self, id):
        self.id = id
    
    def get_type(self):
        return (self.type1, self.type2)

# ポケモンのチーム情報を格納するクラス
class PokemonTeam():
    def __init__(self):
        self.teamlist = []
    
    def addPokemon(self, id:int):
        self.teamlist.append(Pokemon(id))
    
    def outputteam(self):
        for pokemon in self.teamlist:
            print(f"id:{pokemon.id}")

def type_effectiveness(atacktype, defensetype):
    if atacktype is None:
        return 1
    elif defensetype is None:
        return 1

    typedf = pd.read_csv(f"{os.path.dirname(__file__)}/poketype.csv", index_col="atacktype")
    effect = typedf.iloc[atacktype].iloc[defensetype]
    print(f"{type_EN[atacktype]} -> {type_EN[defensetype]} : x {effect}")
    
    return effect

def types_effectiveness(atacktypes, defensetypes):
    print(atacktypes)
    results = []
    for atktype in atacktypes:
        damage = 1
        for deftype in  defensetypes:
            damage *= type_effectiveness(atktype, deftype)
        results.append(damage)
        print(f"{type_EN[atktype]} -> {type_EN[defensetypes[0]]} & {type_EN[defensetypes[1]]} : x {damage}")
    # results = [type_effectiveness(atktype, deftype) for atktype in atacktypes for deftype in defensetypes]
    
    
    
    return results

if __name__ == "__main__":

    team1 = PokemonTeam()
    team1.addPokemon(id=23)
    team1.addPokemon(id=34)
    
    team1.outputteam()
    
    # type_effectiveness(0,13)
    types_effectiveness([1,2],[3,5])