from pk_utility import *
from pk_enums import *
from Team import *
from SkillFamalies import *
from AllSkills import *
from Weather import *
from ManipulatePM import *
from PMList import *
from Console import *
from playsound import *
from PokemonPK.Global.playsound import *

class Rounds(object):

    def __init__(self,our_tm,enemy_tm):
        self.our_tm=our_tm
        self.enemy_tm=enemy_tm
        self.our_skill=None
        self.enemy_skill=None
        self.our_life_line=True
        self.enemy_life_line=True
        self.weather=Weather()
        self.first=True
        self.ml=music_list()
        


    def Run(self):
        '''
            回合制战斗
        '''
        Console.start_game(self.our_tm,self.enemy_tm)
        while True:
            #检查结束
            if self._CheckTeam():
                self._Exit()
                break
            # print('start')
            self._Start()
            
            # print('choose')
            if self._Choose()=='END':
                self._Exit()
                break
            # print('fight')
            self._Fight()

            self._End()
            # rest()
            
    def _Exit(self):
        self.ml.pause_music()
        music_manager.stop()
            
    
    def _Start(self):
        if self.first:
            self.first=False
            self.ml.append_music(pk_path+'Global/music/golden_fight_start.mp3')
            self.ml.append_music(pk_path+'Global/music/golden_fight_repeat.mp3',True)
            rest(1.5)
            Console.msg('开战了！')
            
            rest(1.5)
            self._Admission(self.our_tm) 
            rest(1.5)
            self._Admission(self.enemy_tm) 
        else:
            our_pm=self.our_tm.pm_list.Front()
            enemy_pm=self.enemy_tm.pm_list.Front()



            is_enemy_admission=False
            is_our_admission=False
            if not our_pm.IsAlive():
                is_our_admission=True
                
                

            if not enemy_pm.IsAlive():
                is_enemy_admission=True

            if is_our_admission or is_enemy_admission:
                if our_pm.IsAlive():
                    self._ReduceCondRound(our_pm)
                elif enemy_pm.IsAlive():
                    self._ReduceCondRound(enemy_pm)
                while(True):
                    if self.our_tm.pm_list.SwitchPM():  
                        is_our_admission=True                      
                        break
                    if not is_our_admission:
                        break

            if is_enemy_admission:
                for pm in self.enemy_tm.pm_list:
                    if pm.IsAlive() and TypeChart.TypeVSType(our_pm.type,pm.type)[0]<=2:
                        self.enemy_tm.pm_list.Choose(pm)
                        is_enemy_admission=True
                        break
                #如果没有合适的属性的宝可梦，则让第一只活着的宝可梦上场
                if not self.enemy_tm.pm_list.Front().IsAlive():
                    self.enemy_tm.pm_list.Choose(self.enemy_tm.pm_list.FirstAlive())
                    

            

            if is_our_admission:
                self._Admission(self.our_tm)
            if is_enemy_admission:
                self._Admission(self.enemy_tm)
            

    def _Choose(self):
        '''
            选择攻击、道具或者交换宝可梦
        '''
        self.our_skill=None
        self.enemy_skill=None
        our_pm = self.our_tm.pm_list.FirstAlive()
        enemy_pm=self.enemy_tm.pm_list.FirstAlive()

        #我方选择
        if our_pm.special_cond.Check(SpecialCondEnum.FORCED):
            self.our_skill=our_pm.last_round.src_skill
        else:
            while(True):
                Console.refresh(is_clean_total=True)
                Console.msg('[1] 战斗')
                Console.msg('[2] 背包')
                Console.msg('[3] 精灵')
                Console.msg('[4] 逃跑')
                choice=input('请选择你要进行的操作：')
                choice=a2i(choice,1,4)
                if choice<4 and choice>=0:
                    if choice == 0:
                        retval = SkillChoose(our_pm)
                        if retval!=None:
                            self.our_skill=retval
                            break
                    elif choice == 1:
                        if self.our_tm.package.Open(self.our_tm.pm_list):
                            break
                    elif choice == 2:
                        if our_pm.special_cond.Check(SpecialCondEnum.BOUND):
                            Console.msg(our_pm.GetName()+'被束缚，无法下场')
                            continue
                        if self.our_tm.pm_list.SwitchPM():
                            self._Admission(self.our_tm)
                            break
                    elif choice == 3:
                        if ToBeSure('逃跑'):
                            return 'END'
                else:
                    pass
        
        #敌方选择
        self._EnemyScriptChoose()
        Console.refresh(is_clean_total=True)
        return ''
        # print('Skills')
        # print(self.our_skill)
        # print(self.enemy_skill)

    def _Admission(self,team):
        '''
            宝可梦入场
        '''
        # rest()
        pokemon=team.pm_list.FirstAlive()
        if pokemon!=None:
            team.player.Speak('就决定是你了(゜-゜)つロ—    '+pokemon.GetName()+'!')
        return pokemon

    def _UseProps(self):
        '''
            道具使用阶段
        '''
        pass

    def _Fight(self):
        '''
            1.使用招式阶段
            2.判断宝可梦状态
            3.招式负面效果发动
        '''
        our_pm = self.our_tm.pm_list.FirstAlive()
        enemy_pm=self.enemy_tm.pm_list.FirstAlive()
        if self.our_skill==None:
            if self.enemy_skill==None:
                pass
            else:
                self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
        else:
            if self.enemy_skill==None:
                self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
            else:
                if self.enemy_skill.GetPriority()>self.our_skill.GetPriority():
                    self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
                    self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)

                elif self.enemy_skill.GetPriority()<self.our_skill.GetPriority():
                    self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                    self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)

                else:
                    our_speed = our_pm.Speed()
                    enemy_speed = enemy_pm.Speed()
                    if our_speed*our_pm.stage.Get(StageEnum.SPEED) > enemy_speed*enemy_pm.stage.Get(StageEnum.SPEED):
                        self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                        self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
                    elif enemy_pm.status_cond==StatusCondEnum.PARALYSIS:
                        self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                        self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
                    elif our_pm.status_cond==StatusCondEnum.PARALYSIS:
                        self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
                        self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                    elif our_speed*our_pm.stage.Get(StageEnum.SPEED) < enemy_speed*enemy_pm.stage.Get(StageEnum.SPEED):
                        self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
                        self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                    else:
                        if our_speed > enemy_speed:
                            self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                            self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
                        elif our_speed < enemy_speed:
                            self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
                            self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                        else:
                            self._CheckAndApplySkill(self.our_skill,our_pm,enemy_pm,self.weather,self.our_tm,self.enemy_tm)
                            self._CheckAndApplySkill(self.enemy_skill,enemy_pm,our_pm,self.weather,self.enemy_tm,self.our_tm)
        our_pm = self.our_tm.pm_list.Front()
        enemy_pm=self.enemy_tm.pm_list.Front()
        #招式负面效果发动
        if our_pm.IsAlive():
            self._NegativeEffect(our_pm,enemy_pm)
        if enemy_pm.IsAlive():
            self._NegativeEffect(enemy_pm,our_pm)

    def _NegativeEffect(self,pm,opposite_pm):

        if pm.status_cond.Check(StatusCondEnum.POISON):
            Console.msg(pm.GetName()+pm.status_cond.Discription())
            ApplyDamage(pm,pm.HP()*1/8)
        elif pm.status_cond.Check(StatusCondEnum.BADLYPOISON):
            Console.msg(pm.GetName()+pm.status_cond.Discription())
            time=pm.status_cond.LastTime()+1
            if time>15:
                time=15
            ApplyDamage(pm,pm.HP()*time/16)
        elif pm.status_cond.Check(StatusCondEnum.BURN):
            Console.msg(pm.GetName()+pm.status_cond.Discription())
            ApplyDamage(pm,pm.HP()*1/16)

        if pm.special_cond.Check(SpecialCondEnum.PARASITIC):
            Console.msg(pm.GetName()+SpecialCondEnum.Discription(SpecialCondEnum.PARASITIC))
            ApplyDamage(pm,pm.HP()*1/16)
            if opposite_pm.IsAlive():
                Console.msg(opposite_pm.GetName()+'吸收了力量，回复了'+RecoverHP(opposite_pm,pm.HP()*1/16)+'点HP')


        
    
    def _End(self):
        '''
            1.天气变化
            2.回合结束
        '''
        our_pm = self.our_tm.pm_list.Front()
        enemy_pm=self.enemy_tm.pm_list.Front()

        #状态数减1
        self._ReduceCondRound(our_pm)
        self._ReduceCondRound(enemy_pm)
        
        if self.weather!=None:
            last_weather=self.weather.Get()
            self.weather.Reduce()
            if self.weather!=last_weather:
                Console.msg(self.weather.Discription())
            else:
                if self.weather.IsNormal():
                    pass
                else:
                    Console.msg(self.weather.Discription())

        
    def _ReduceCondRound(self,pm):
        if pm.IsAlive():
            retval=pm.status_cond.Reduce()
            if retval!='':
                Console.msg(pm.GetName()+retval)

            is_forced_before=pm.special_cond.Check(SpecialCondEnum.FORCED)

            retval=pm.special_cond.Reduce()
            if retval!='':
                Console.msg(pm.GetName()+retval)

            is_forced_later=pm.special_cond.Check(SpecialCondEnum.FORCED)

            if is_forced_before and not is_forced_later and pm.last_round.src_skill !=None and pm.last_round.src_skill.GetName()=='大闹一番':
                Console.msg(pm.GetName()+'闹得头晕目眩')
                SkillBase.CauseSpecialCond(pm,1,SpecialCondEnum.CONFUSION)

                

    def _CheckTeam(self):
        '''
            检查战斗是否结束
        '''
        end=True
        for pm in self.enemy_tm.pm_list:
            if pm.hp>0:
                end=False
        if end==True:
            music_name=self.ml.top().get_music()
            music_name=music_name[music_name.rfind('/')+1:]
            if music_name == 'golden_fight_start.mp3':
                self.ml.play_next()    
            
            self.ml.append_music(pk_path+'Global/music/golden_fight_win.mp3')
            self.ml.play_next()
            Console.msg('***************',sleep_time=0.5)
            Console.msg('你赢得了胜利！',sleep_time=0.5)
            Console.msg('***************',sleep_time=0.5)
            return True
        end=True
        for pm in self.our_tm.pm_list:
            if pm.hp>0:
                end=False
        if end==True:
            Console.msg('你输了...')
            return True
        return end
    def _CheckAndApplySkill(self,skill,src,target,weather,src_tm,target_tm):
        status=src.status_cond
        damage=0
        apply_flag=True
        if not(src.IsAlive() and target.IsAlive()):
            return False

        if not StatusCondEnum.IsNormal(status):
            if status==StatusCondEnum.PARALYSIS:
                if np.random.rand()<0.25:
                    Console.msg(src.GetName()+src.status_cond.Discription())
                    apply_flag=False
            elif status==StatusCondEnum.SLEEP:
                Console.msg(src.GetName()+src.status_cond.Discription())
                apply_flag=False
            elif status==StatusCondEnum.FREEZE:
                Console.msg(src.GetName()+src.status_cond.Discription())
                apply_flag=False
        special_cond=src.special_cond
        if special_cond.Check(SpecialCondEnum.STIFF):
            Console.msg(src.GetName()+SpecialCondEnum.Discription(SpecialCondEnum.STIFF))
            apply_flag=False
        elif special_cond.Check(SpecialCondEnum.CONFUSION):
            Console.msg(src.GetName()+'混乱了')
            if np.random.rand()<0.5:
                Console.msg(src.GetName()+SpecialCondEnum.Discription(SpecialCondEnum.CONFUSION))
                damage=SelfHarm().Apply(src,src,weather,is_print=False)
                apply_flag=False
        
            
        if apply_flag:
            damage=skill.Apply(src,target,weather)
        if target.IsAlive():
            if target.last_round.src_skill!=None and damage>0 and  target.last_round.src_skill.GetName()=='愤怒':
                Console.msg(target.GetName()+'被激怒了')
                Console.msg(target.GetName()+target.stage.Up(StageEnum.ATTACK,1))
            target.last_round.target_skill=skill
            target.last_round.suffer_damage=damage
        if src.IsAlive():
            src.last_round.src_skill=skill
        if skill.GetName()=='吹飞' or skill.GetName()=='吼叫':
            Console.msg(target.GetName()+'被强制下场')
            target_tm.pm_list.Choose(target_tm.pm_list.LastAlive())
            self._Admission(target_tm)
        
        

    def _EnemyScriptChoose(self):
        our_pm = self.our_tm.pm_list.FirstAlive()
        enemy_pm=self.enemy_tm.pm_list.FirstAlive()
        effect,effect_str=TypeChart.TypeVSType(our_pm.type,enemy_pm.type)
        if np.random.rand()<0.33333:
            self.enemy_tm.player.MockingOnFighting()
        if enemy_pm.special_cond.Check(SpecialCondEnum.FORCED):
            self.enemy_skill=enemy_pm.last_round.src_skill
            return True
        else:
            #优先换精灵
            if effect>2 and np.random.rand()<0.6:
                if not enemy_pm.special_cond.Check(SpecialCondEnum.BOUND):
                    for i,pm in enumerate(self.enemy_tm.pm_list):
                        if pm.IsAlive() and TypeChart.TypeVSType(our_pm.type,pm.type)[0]<=2:
                            self.enemy_tm.player.Speak('下来吧'+self.enemy_tm.pm_list.FirstAlive().GetName())
                            self.enemy_tm.pm_list.Swap(0,i)
                            self._Admission(self.enemy_tm)
                            enemy_pm=pm
                            return True
                
            #其次是使用药物
            if enemy_pm.IsAlive() and enemy_pm.hp<enemy_pm.HP()*0.25 and np.random.rand()<1/3:
                medicine=FullRestore(1)
                self.enemy_tm.player.Speak('对'+enemy_pm.GetName()+'使用了'+medicine.GetName())
                medicine.Use(enemy_pm)
                return True

            #最后是选择招式    
            self.enemy_skill=self._EnemyScriptSkillChoose()
            return True
            
    def _EnemyScriptSkillChoose(self):
        our_pm = self.our_tm.pm_list.FirstAlive()
        enemy_pm=self.enemy_tm.pm_list.FirstAlive()
        choice=[0 for i in range(len(enemy_pm.skills))]
        struggle_flag=True
                        
        

        for i,skill in enumerate(enemy_pm.skills):
            if skill.pp>0:
                struggle_flag=False
                income=0
                if skill.IsHit(enemy_pm,our_pm,self.weather): 
                    if skill.GetPower()>0:
                        income=skill.DamageCal(enemy_pm,our_pm,self.weather,is_print=False)*skill.GetHit()/100
                    if isinstance(skill,ReboundSkill) or isinstance(skill,SelfLossSkill):
                        income=income-enemy_pm.hp*skill.percent
                    elif isinstance(skill,FixDamageSkill):
                        income=skill.damage*skill.GetHit()/100
                    elif isinstance(skill,StockpileSkill):
                        income=income/2
                    elif isinstance(skill,MustKillSkill):
                        income=our_pm.hp*(30+enemy_pm.level-our_pm.level)/100
                    elif isinstance(skill,MultiHitSkill):
                        income=income*3.168
                    elif isinstance(skill,AbsorbSkill):
                        income=income+income*skill.percent
                    else:
                        obj_of_action=skill.GetObjOfAction()
                        if obj_of_action & ObjOfAction.SRC:
                            if skill.GetPower()>0:
                                income = income-30*np.random.randint(50,100)/100
                            else:
                                income = income+30*np.random.randint(50,100)/100
                        if obj_of_action & ObjOfAction.SRC_ABL:
                            if enemy_pm.stage.Mean()<=0:
                                income = income+30*np.random.randint(50,100)/100*skill.effect
                            else:
                                income = income+15*np.random.randint(50,100)/100*skill.effect
                        if obj_of_action & ObjOfAction.TAR_ABL:
                            if our_pm.stage.Mean()>=0:
                                income = income+30*np.random.randint(50,100)/100
                            else:
                                income = income+15*np.random.randint(50,100)/100
                choice[i]=income*np.random.randint(80,100)/100
            else:
                choice[i]=-1

        if struggle_flag:
            return Struggle()
        else:
            return enemy_pm.skills[np.argmax(choice)]
        

