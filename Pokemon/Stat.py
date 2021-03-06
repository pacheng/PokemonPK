from pk_utility import *
from pk_enums import *

'''
    种族值
'''
class Stat(object):
    hp=0
    attack=0
    defense=0
    special_attack=0
    special_defense=0
    speed=0
    def __init__(self,file_path):
        file_stats=open(file_path)
        data = pd.read_csv(file_stats)
        file_stats.close()
        data.index=data['Stat'].values
        self.hp = data.loc['HP']['Value']
        self.attack = data.loc['Attack']['Value']
        self.defense = data.loc['Defense']['Value']
        self.special_attack = data.loc['Sp.Atk']['Value']
        self.special_defense = data.loc['Sp.Def']['Value']
        self.speed = data.loc['Speed']['Value']

'''
    个体值
'''
class IndivValues(object):
    hp=0
    attack=0
    defense=0
    special=0
    speed=0
    def __init__(self,attack=9,defense=8,special=8,speed=8):
        if attack >15 or defense >15 or special >15 or speed >15:
            raise PokemonPKError('Invalid Individual Values Found!')
        self.attack = attack
        self.defense = defense
        self.special = special
        self.speed = speed
        if attack%2:
            self.hp = self.hp+8
        if defense%2:
            self.hp = self.hp+4
        if speed%2:
            self.hp = self.hp+2
        if special%2:
            self.hp = self.hp+1

'''
    异常状态
'''
class StatusCond(object):
    def __eq__(self,other):
        if isinstance(other,StatusCondEnum):
            return self._condition==other
        else:
            return self._condition==other._condition
    def __init__(self):
        self.Clear()
    def __str__(self):
        return StatusCondEnum.ToChinese(self._condition)
    
    def Discription(self):
        return StatusCondEnum.Discription(self._condition)

    def Reduce(self):
        retval=''
        if self._round>0:
            self._round=self._round-1
            self._last_time=self._last_time+1
            if self._round==0:
                retval = StatusCondEnum.BackToNormal(self._condition)
                self.Clear()    
                
        return retval
        
    def Set(self,status_cond_enum,round):
        if not self.IsNormal():
            return False
        self._condition=status_cond_enum
        self._round=round
        self._last_time=0
        return True

    def Get(self):
        return self._condition

    def Check(self,status_cond_enum):
        return status_cond_enum == self._condition

    def Clear(self):
        self._condition=StatusCondEnum.NORMAL
        self._round=0
        self._last_time=0

    def IsNormal(self):
        return StatusCondEnum.IsNormal(self._condition)

    def LastTime(self):
        return self._last_time
    

'''
    特殊状态
'''
class SpecialCond(object):
    def __init__(self):
        self.Clear()
    
    def Reduce(self):
        retval=''
        for i in range(len(self._special_cond)):
            if self._special_cond[i]>0:
                self._special_cond[i]=self._special_cond[i]-1
                if self._special_cond[i]==0:
                    retval = SpecialCondEnum.BackToNormal(i)
                    self.Clear()  
        return retval
    def Set(self,special_cond_enum,num):
        self._special_cond[special_cond_enum]=num

    def Get(self,special_cond_enum):
        return self._special_cond[special_cond_enum]

    def Check(self,special_cond_enum):
        return self._special_cond[special_cond_enum]!=0

    def Clear(self):
        self._special_cond=[0,0,0,0,0,0,0]
'''
    能力阶级
'''
class Stage(object):
    def __init__(self):
        self.Clear()

    def Up(self,stage_enum,value):
        up_value = value+self._stage[stage_enum]
        if up_value<=6:
            self._stage[stage_enum]=up_value
        elif self._stage[stage_enum]!=6:
            self._stage[stage_enum]=6
        else :
            value=0
        return self.ToChinese(stage_enum,value)

    def Down(self,stage_enum,value):
        down_value = self._stage[stage_enum]-value
        if down_value>=-6:
            self._stage[stage_enum]=down_value
            value= -value
        elif self._stage[stage_enum]!=-6:
            self._stage[stage_enum]=-6
            value= -value
        else :
            value= 0
        return self.ToChinese(stage_enum,value)

    def Get(self,stage_enum):
        if stage_enum>=len(self._stage):
            raise PokemonPKError()
        if self._stage[stage_enum]<0:
            return 2/(2-self._stage[stage_enum])
        elif self._stage[stage_enum]==0:
            return 1
        else:
            return (2+self._stage[stage_enum])/2
    def Mean(self):
        sum_val=0
        for x in self._stage:
            sum_val=sum_val+x
        return sum_val/len(self._stage)
        

    def Clear(self):
        self._stage=[0,0,0,0,0,0,0,0]

    @classmethod
    def ToChinese(cls,stage_enum,value):

        change_mode=''
        if value==1:
            change_mode= '提高了!'
        elif value==2:
            change_mode= '大幅提高了!'
        elif value<=6 and value>=3:
            change_mode= '巨幅提高了!'
        elif value==-1:
            change_mode= '降低了!'
        elif value==-2:
            change_mode= '大幅降低了!'
        elif value<=-3 and value>=-6:
            change_mode= '巨幅降低了!'
        elif value==0:
            change_mode= '似乎没有发生变化'
        return StageEnum.ToChinese(stage_enum)+change_mode
        
class LastRound(object):
    def __init__(self):
        self.target_skill=None
        self.src_skill=None
        self.suffer_damage=0
    

        
        



        
        
        
        
        
