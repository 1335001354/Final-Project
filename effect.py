from __future__ import annotations
from typing import Dict, Any, Optional, TYPE_CHECKING

from enums import TriggerPhase
from action_interpreter import ActionInterpreter

# 【修正三】创建一个解释器的单例，供所有效果实例共享和调用
action_interpreter = ActionInterpreter()

if TYPE_CHECKING:
    from hero import Unit

class GenericEffect:
    """
    一个通用的效果实例。它的行为由注入的逻辑钩子函数决定。
    """
    # 【修正二】使用更灵活的构造函数
    def __init__(self,
                 name: str,
                 logic_hooks: Dict[TriggerPhase, Any],
                 **kwargs):
        """
        Args:
            name (str): 效果的名称。
            logic_hooks (Dict): 从YAML加载的原始逻辑钩子字典。
            **kwargs: 效果的其他所有参数，如 duration, potency 等。
        """
        self.name = name
        self.logic_hooks = logic_hooks

        # 从 kwargs 中安全地解析标准参数，并设置默认值
        self.is_control_effect: bool = kwargs.get('is_control_effect', False)
        self.duration: int = kwargs.get('duration', 1)
        self.potency: float = kwargs.get('potency', 1.0)
        self.target_count: int = kwargs.get('target_count', 1)
        self.source: Optional['Unit'] = kwargs.get('source', None)
        
        # 将所有传入的kwargs也存储起来，以备自定义逻辑使用
        self.params = kwargs

    def tick(self) -> bool:
        if self.duration == float('inf'):
            return False
        
        self.duration -= 1
        # 【修正】当 duration 减为0时，效果就应该过期
        return self.duration <= 0

    def _execute_hook(self, phase: TriggerPhase, context: Dict[str, Any]) -> Any:
        """通用钩子执行器，现在调用解释器的实例。"""
        if phase.name in self.logic_hooks:
            actions = self.logic_hooks[phase.name]
            context['effect'] = self
            # 【修正三】调用解释器的实例方法，而不是类方法
            return action_interpreter.execute(actions, context)

    # --- 【修正一】所有 on_* 方法都修正了 _execute_hook 的调用参数 ---
    
    def on_apply(self, target: 'Unit', silent: bool = False):
        if not silent:
            print(f"[{target.name}] 获得了效果：[{self.name}]（效力：{self.potency}, 持续：{self.duration}回合）。")
        context = {'target': target, 'user': self.source, 'silent': silent}
        self._execute_hook(TriggerPhase.ON_APPLY, context)
        
    def on_remove(self, target: 'Unit', silent: bool = False):
        if not silent:
            print(f"[{target.name}] 的效果 [{self.name}] 消失了。")
        context = {'target': target, 'user': self.source, 'silent': silent}
        self._execute_hook(TriggerPhase.ON_REMOVE, context)

    def on_turn_start(self, target: 'Unit', silent: bool = False):
        context = {'target': target, 'user': self.source, 'silent': silent}
        self._execute_hook(TriggerPhase.ON_TURN_START, context)

    def on_turn_end(self, target: 'Unit'):
        context = {'target': target, 'user':self.source}
        self._execute_hook(TriggerPhase.ON_TURN_END, context)

    def on_take_damage(self, target: 'Unit', damage_info: dict):
        context = {'target': target, 'user': self.source, 'damage_info': damage_info}
        self._execute_hook(TriggerPhase.ON_TAKE_DAMAGE, context)

    def on_deal_damage(self, target: 'Unit', damage_info: dict):
        context = {'target': target, 'user': self.source, 'damage_info': damage_info}
        self._execute_hook(TriggerPhase.ON_DEAL_DAMAGE, context)
        
    def __repr__(self) -> str:
        return f"<{self.name} (效力:{self.potency}, {self.duration}回合)>"