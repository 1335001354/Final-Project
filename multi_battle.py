from __future__ import annotations
from typing import List, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from hero import Unit

class MultiBattle:
    def __init__(self, team1: List[Unit], team2: List[Unit], silent: bool = False):
        self.team1 = team1
        self.team2 = team2
        self.silent = silent
        
        if not self.silent:
            print("====== 多英雄战斗开始 ======")
            print(f"队伍1 ({len(team1)}人): {', '.join([u.name for u in team1])}")
            print(f"队伍2 ({len(team2)}人): {', '.join([u.name for u in team2])}")

    def get_alive_units(self, team: List[Unit]) -> List[Unit]:
        """获取队伍中存活的单位"""
        return [unit for unit in team if unit.current_hp > 0]

    def get_all_alive_units(self) -> List[Unit]:
        """获取所有存活的单位"""
        return self.get_alive_units(self.team1) + self.get_alive_units(self.team2)

    def get_opponents(self, unit: Unit) -> List[Unit]:
        """获取指定单位的对手队伍"""
        if unit in self.team1:
            return self.get_alive_units(self.team2)
        else:
            return self.get_alive_units(self.team1)

    def run(self):
        """执行多英雄战斗循环，直到一方全部倒下"""
        turn = 1
        
        while self.get_alive_units(self.team1) and self.get_alive_units(self.team2):
            if not self.silent:
                print(f"\n★★★★★ 回合 {turn} ★★★★★")
            
            # 获取所有存活单位，按速度排序
            all_alive = self.get_all_alive_units()
            all_alive.sort(key=lambda u: u.speed, reverse=True)
            
            # 每个存活单位依次行动
            for unit in all_alive:
                if unit.current_hp <= 0:
                    continue
                    
                if not self.silent:
                    print(f"\n轮到 [{unit.name}] 行动...")
                unit.process_turn_start(silent=self.silent)
                
                # 获取对手
                opponents = self.get_opponents(unit)
                if not opponents:
                    break
                
                # 执行行动
                self._unit_act(unit, opponents)
                unit.process_turn_end(silent=self.silent)
                
                # 检查是否有队伍被全灭
                if not self.get_alive_units(self.team1) or not self.get_alive_units(self.team2):
                    break
            
            turn += 1

        # 战斗结束，宣布胜利者
        team1_alive = self.get_alive_units(self.team1)
        team2_alive = self.get_alive_units(self.team2)
        
        # 返回结果而不是直接打印
        result = {
            'winner': None,
            'survivors': [],
            'turns': turn - 1,
            'team1_final': [(u.name, u.current_hp, u.hp) for u in self.team1],
            'team2_final': [(u.name, u.current_hp, u.hp) for u in self.team2]
        }
        
        if team1_alive and not team2_alive:
            result['winner'] = 'team1'
            result['survivors'] = [u.name for u in team1_alive]
        elif team2_alive and not team1_alive:
            result['winner'] = 'team2'
            result['survivors'] = [u.name for u in team2_alive]
        else:
            result['winner'] = 'draw'
        
        if not self.silent:
            print("\n====== 战斗结束 ======")
            if result['winner'] == 'team1':
                print(f"🏆 队伍1胜利！")
                print(f"存活成员: {', '.join(result['survivors'])}")
            elif result['winner'] == 'team2':
                print(f"🏆 队伍2胜利！")
                print(f"存活成员: {', '.join(result['survivors'])}")
            else:
                print("平局！")
            
            print("\n最终状态：")
            print("队伍1:")
            for unit in self.team1:
                print(f"  {unit}")
            print("队伍2:")
            for unit in self.team2:
                print(f"  {unit}")
        
        return result

    def _unit_act(self, unit: Unit, opponents: List[Unit]):
        """单位行动逻辑"""
        if unit.is_stunned:
            if not self.silent:
                print(f"[{unit.name}] 处于眩晕状态，无法行动！")
            return
            
        # 尝试使用技能
        for skill in unit.skills.values():
            if skill.is_ready():
                self._use_skill(unit, skill, opponents)
                return
        
        # 没有可用技能，执行普通攻击
        if not self.silent:
            print(f"[{unit.name}] 没有可用的技能，执行普通攻击。")
        target = random.choice(opponents)
        is_crit = random.random() < unit.crit_rate
        target.take_damage(unit.attack, is_crit=is_crit, silent=self.silent)

    def _use_skill(self, user: Unit, skill, opponents: List[Unit]):
        """使用技能"""
        if not skill.is_ready():
            if not self.silent:
                print(f"[{user.name}] 尝试使用 [{skill.name}]，但技能尚未冷却！")
            return False

        if not self.silent:
            print(f"[{user.name}] 使用了技能：『{skill.name}』!")
        
        # 选择目标
        if skill.target_type == 'self':
            targets = [user]
        else:  # enemy
            # 随机选择指定数量的对手
            target_count = min(skill.target_count, len(opponents))
            targets = random.sample(opponents, target_count)
        
        # 1. 计算并施加伤害
        if skill.damage_multiplier > 0:
            damage = int(user.attack * skill.damage_multiplier)
            is_crit = random.random() < user.crit_rate
            
            for target in targets:
                target.take_damage(damage, is_crit=is_crit, silent=self.silent)

        # 2. 施加效果
        for effect_data in skill.effects_to_apply:
            for target in targets:
                effect_instance = skill.effect_factory.create(**effect_data)
                if effect_instance:
                    effect_instance.source = user
                    target.add_effect(effect_instance, silent=self.silent)
        
        # 3. 进入冷却
        skill.current_cooldown = skill.cooldown_max + 1
        return True 