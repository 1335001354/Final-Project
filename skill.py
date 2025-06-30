# skill.py
from __future__ import annotations
from typing import List, Dict, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from hero import Unit
    from factory_effect import EffectFactory

class Skill:
    def __init__(self,
                 name: str,
                 effect_factory: EffectFactory,
                 damage_multiplier: float = 0.0,
                 effects_to_apply: List[Dict[str, Any]] | None = None,
                 cooldown: int = 0,
                 target_type: str = 'enemy',
                 target_count: int = 1):
        self.name = name
        self.effect_factory = effect_factory
        self.damage_multiplier = damage_multiplier
        self.effects_to_apply = effects_to_apply if effects_to_apply else []
        self.cooldown_max = cooldown
        self.current_cooldown = 0
        self.target_type = target_type # 'enemy' or 'self'
        self.target_count = target_count # 作用目标数量

    def is_ready(self) -> bool:
        """检查技能是否冷却完毕。"""
        return self.current_cooldown == 0

    def tick_cooldown(self):
        """每回合减少冷却时间。"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def _select_targets(self, user: Unit, opponent: Unit) -> List[Unit]:
        """选择技能作用的目标"""
        if self.target_type == 'self':
            return [user]
        elif self.target_type == 'enemy':
            # 对于敌方目标，目前只有单个对手，所以返回对手
            # 未来可以扩展为选择多个敌方单位
            return [opponent]
        return []

    def use(self, user: Unit, opponent: Unit) -> bool:
        """
        使用技能。
        Args:
            user (Unit): 技能使用者。
            opponent (Unit): 技能作用的敌方目标。
        """
        if not self.is_ready():
            print(f"[{user.name}] 尝试使用 [{self.name}]，但技能尚未冷却！")
            return False

        print(f"[{user.name}] 使用了技能：『{self.name}』!")
        
        # 选择目标
        targets = self._select_targets(user, opponent)
        
        # 1. 计算并施加伤害
        if self.damage_multiplier > 0:
            damage = int(user.attack * self.damage_multiplier)
            # 技能暴击判定
            is_crit = random.random() < user.crit_rate
            
            for target in targets:
                target.take_damage(damage, is_crit=is_crit)

        # 2. 施加效果
        for effect_data in self.effects_to_apply:
            for target in targets:
                # 从工厂创建效果实例
                effect_instance = self.effect_factory.create(**effect_data)
                if effect_instance:
                    effect_instance.source = user # 记录效果来源
                    target.add_effect(effect_instance)
        
        # 3. 进入冷却
        self.current_cooldown = self.cooldown_max + 1 # +1 是因为本回合末会tick一次
        return True