from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Dict, Type

from dataclasses import dataclass, field
from abc import ABC, abstractmethod

"""
动作空间：
  削弱：
    数值削弱
    目标数量削弱
    概率削弱
    英雄属性削弱
  增强
    数值增强
    目标数量增强
    概率增强
    英雄属性增强
"""

"""
共性：
持续回合数
可否被驱散

减益类型：
持续伤害类型
    持续伤害倍率
    无视减防比例
控制类型
    概率
减速类型
    减速比例
削减怒气类型
    减少怒气数值


增益类型：
加速类型

"""

@dataclass
class StatusEffect(ABC):
    name: str
    duration: int
    magnitude: float = 0.0
    removeable: bool = True
    elapsed: int = field(default=0, init=False)

    @abstractmethod
    def on_apply(self, target: 'Attack'):
        ...

    @abstractmethod
    def on_tick(self, target: 'Attack'):
        ...

    @abstractmethod
    def on_expire(self, target: 'Attack'):
        ...

    @abstractmethod
    def on_attack(self, target: 'Attack'):
        ...

    def tick(self, target: 'Attack') -> bool:
        """每回合调用一次，返回 True 表示效果已结束"""
        if self.elapsed == 0:
            self.on_apply(target)

        self.on_tick(target)
        self.elapsed += 1

        if self.elapsed >= self.duration:
            self.on_expire(target)
            return True
        return False


@dataclass
class Attack:
    """
    一个简单的攻击类。

    Attributes
    ----------
    attacknum : int
        攻击基数（例如子弹数、招式基础威力等）
    attackratio : float
        攻击系数（例如暴击倍率、伤害放大倍率等）
    attackstatus : int
        攻击的异常状态（例如中毒、灼烧等）
    """
    attacknum: int = field(default=0)
    attackratio: float = field(default=1.0)
    attackdeffect: int = field(default=0)

    def effective_damage(self) -> float:
        """
        计算最终有效伤害。

        Returns
        -------
        float
            伤害结果 = attacknum * attackratio - attackdeffect
        """
        return self.attacknum * self.attackratio - self.attackdeffect

    def __repr__(self) -> str:
        return (f"Attack(attacknum={self.attacknum}, "
                f"attackratio={self.attackratio}, "
                f"attackdeffect={self.attackdeffect})")

