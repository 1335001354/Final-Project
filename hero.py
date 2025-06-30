from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Any, Dict, Optional, TYPE_CHECKING, Union
from abc import ABC
import random

# 确保从您的其他文件中正确导入
from enums import TriggerPhase

if TYPE_CHECKING:
    from effect import GenericEffect
    from skill import Skill

# Attribute 类保持不变，放在文件顶部
@dataclass
class Attribute:
    """用于存储单个可扩展属性的所有数据。"""
    base: float
    ratio: float = 1.0
    final_type: Callable[[float], Any] = int
    calculation_logic: Callable[[float, float], float] = lambda base, ratio: base * ratio

    @property
    def value(self) -> Any:
        calculated_value = self.calculation_logic(self.base, self.ratio)
        return self.final_type(calculated_value)

class Unit(ABC):
    """一个支持动态扩展属性和效果的、经过最终修正的单元类。"""
    
    def __init__(self, skills: Optional[List[Skill]] = None, **kwargs):
        """通过关键字参数初始化属性，并通过列表初始化技能。"""
        # --- 1. 初始化所有容器 ---
        self._attributes: Dict[str, Attribute] = {}
        self.effects: List['GenericEffect'] = []
        self.skills: Dict[str, Skill] = {}
        self.is_stunned: bool = False
        
        # --- 2. 填充技能字典 ---
        if skills:
            for skill in skills:
                self.skills[skill.name] = skill # 修正了赋值错误
        
        # --- 3. 定义核心"可计算"属性 ---
        # 彻底移除了关于 'effects' 的错误定义
        self._define_core_attribute('hp', kwargs.get('hp', 0))
        self._define_core_attribute('attack', kwargs.get('attack', 0))
        self._define_core_attribute('armor', kwargs.get('armor', 0))
        self._define_core_attribute('speed', kwargs.get('speed', 0))
        self._define_core_attribute('crit_rate', kwargs.get('crit_rate', 0.0), float)
        
        # --- 4. 设置其他实例变量 ---
        self.name = kwargs.get('name', 'Unnamed Unit')
        self.max_hp = self.hp 
        self.current_hp = self.max_hp

    def _define_core_attribute(self, name: str, base_value: float, final_type: Callable = int):
        self._attributes[name] = Attribute(base=base_value, final_type=final_type)

    def add_effect(self, effect: Union['GenericEffect', None], silent: bool = False):
        if effect:
            self.effects.append(effect)
            effect.on_apply(self, silent=silent)

    def __getattr__(self, name: str) -> Any:
        if name in self._attributes:
            attr_obj = self._attributes[name]
            final_value = attr_obj.base * attr_obj.ratio
            ratio_modifier, flat_modifier = 1.0, 0.0
            
            for effect in self.effects:
                context = {'target': self, 'user': effect.source, 'attr_name': name}
                modifiers = effect._execute_hook(TriggerPhase.PASSIVE, context)
                if modifiers and isinstance(modifiers, dict):
                    ratio_modifier *= modifiers.get('ratio', 1.0)
                    flat_modifier += modifiers.get('flat', 0.0)
            
            final_value = (final_value + flat_modifier) * ratio_modifier
            return attr_obj.final_type(final_value)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def take_damage(self, amount: int, is_crit: bool = False, silent: bool = False):
        # 新的护甲计算逻辑：护甲越高，免伤比例越接近1
        armor_value = self.armor
        damage_reduction_ratio = armor_value / (armor_value + 100)
        final_damage = int(amount * (1 - damage_reduction_ratio))
        if is_crit:
            final_damage *= 2
            if not silent:
                print(f"[暴击！]{self.name} 受到暴击伤害！")
        self.current_hp -= final_damage
        if not silent:
            print(f"[{self.name}] 护甲减免了 {int(amount * damage_reduction_ratio)} 点伤害，受到了 {final_damage} 点伤害，当前生命值: {self.current_hp}/{self.hp}")

    def act(self, opponent: 'Unit'):
        if self.is_stunned:
            print(f"[{self.name}] 处于眩晕状态，无法行动！")
            return
        for skill in self.skills.values():
            if skill.is_ready():
                skill.use(self, opponent)
                return
        print(f"[{self.name}] 没有可用的技能，执行普通攻击。")
        # 普通攻击暴击判定
        is_crit = random.random() < self.crit_rate
        opponent.take_damage(self.attack, is_crit=is_crit)

    def tick_skill_cooldowns(self):
        for skill in self.skills.values():
            skill.tick_cooldown()
    
    def process_turn_start(self, silent: bool = False):
        if not silent:
            print(f"\n[{self.name}] 的回合开始，当前生命值: {self.current_hp}/{self.hp}")
        for effect in list(self.effects):
            effect.on_turn_start(self, silent=silent)

    def process_turn_end(self, silent: bool = False):
        if not silent:
            print(f"--- [{self.name}] 的回合结束 ---")
        expired_effects = []
        for effect in list(self.effects):
            if effect.tick():
                expired_effects.append(effect)
        
        for effect in expired_effects:
            self.effects.remove(effect)
            effect.on_remove(self, silent=silent)
        
        self.tick_skill_cooldowns()

    def __repr__(self) -> str:
        attrs_str = f"攻击={self.attack}, 护甲={self.armor}, 速度={self.speed}"
        effects_str = ", ".join(e.name for e in self.effects) if self.effects else "无"
        return f"<{self.name} (HP: {self.current_hp}/{self.hp}) | {attrs_str} | 状态: [{effects_str}]>"


class Hero(Unit):
    """一个具体的英雄类，继承自 Unit。"""
    
    # 【修正】构造函数现在能正确处理 name 和 skills，并传递给父类
    def __init__(self, name: str, skills: Optional[List[Skill]] = None, **kwargs):
        super().__init__(skills=skills, name=name, **kwargs)

    def __repr__(self) -> str:
        # 使用父类的 __repr__ 即可，它已经足够详细
        return super().__repr__()