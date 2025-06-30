# action_interpreter.py

from __future__ import annotations
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from hero import Unit
    from effect import GenericEffect

class ActionInterpreter:
    """
    负责解释并执行在YAML中定义的 action 列表。
    """
    def execute(self, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> Any:
        """
        执行一系列动作。
        Args:
            actions (List[Dict]): 从效果定义中获取的动作列表。
            context (Dict): 执行动作所需的上下文，包含 effect, target, user 等。
        """
        return_values = {}
        for action in actions:
            action_type = action.get('type')
            if action_type:
                handler_method = getattr(self, f"_handle_{action_type.lower()}", None)

                if handler_method:
                    # 对于被动效果，我们需要收集返回值
                    result = handler_method(action, context)
                    if result:
                        return_values.update(result)
                else:
                    print(f"警告：未知的动作类型 '{action_type}'")
        
        if return_values:
            return return_values

    def _resolve_value(self, value_def: Any, context: Dict[str, Any]) -> Any:
        """解析一个值，可以是直接量，也可以是来自上下文的引用。"""
        if isinstance(value_def, dict):
            source_name = value_def.get('source')
            
            # 处理基于施加者攻击力的伤害计算
            if source_name == 'source_attack':
                source_unit = context.get('user')  # 效果的施加者
                if source_unit:
                    base_attack = source_unit.attack
                    multiplier = value_def.get('multiplier', 1.0)
                    if isinstance(multiplier, str):
                        effect = context.get('effect')
                        if effect and hasattr(effect, 'params'):
                            multiplier = effect.params.get(multiplier, 1.0)
                        else:
                            multiplier = 1.0
                    return int(base_attack * multiplier)
                return 0
            
            # 处理其他来源
            if source_name:
                source_obj = context.get(source_name) # e.g., context['effect']
                if source_obj:
                    value_key = value_def.get('value')
                    if value_key:
                        return getattr(source_obj, value_key, 0)
        # 简单的表达式求值 (警告: eval有风险，真实项目需使用更安全的解析器)
        elif isinstance(value_def, str):
            try:
                # 创建一个安全的局部命名空间来执行eval
                local_namespace = {'effect': context.get('effect')}
                return eval(value_def, {}, local_namespace)
            except Exception as e:
                print(f"表达式求值错误: {value_def}, 错误: {e}")
                return 0
        return value_def # 直接返回值

    def _resolve_target(self, target_def: str, context: Dict[str, Any]) -> Unit | None:
        """解析目标单位。"""
        if target_def == 'owner':
            return context.get('target') # 效果的持有者
        elif target_def == 'source':
            return context.get('user') # 效果的施加者
        return None

    # --- 具体的 Action Handler ---

    def _handle_deal_damage(self, params: Dict, context: Dict):
        target_def = params.get('target')
        if target_def:
            target = self._resolve_target(target_def, context)
            amount = self._resolve_value(params.get('amount'), context)
            if target and amount > 0:
                # 持续伤害不触发暴击
                target.take_damage(int(amount), is_crit=False)

    def _handle_heal(self, params: Dict, context: Dict):
        target_def = params.get('target')
        if target_def:
            target = self._resolve_target(target_def, context)
            amount = self._resolve_value(params.get('amount'), context)
            if target and amount > 0:
                heal_amount = min(amount, target.hp - target.current_hp)
                target.current_hp += heal_amount
                print(f"[{target.name}] 恢复了 {heal_amount} 点生命值，当前生命值: {target.current_hp}/{target.hp}")

    def _handle_clear_effects(self, params: Dict, context: Dict):
        target_def = params.get('target')
        if target_def:
            target = self._resolve_target(target_def, context)
            if target and target.effects:
                removed_effects = list(target.effects)
                target.effects.clear()
                for effect in removed_effects:
                    effect.on_remove(target)
                print(f"[{target.name}] 的所有效果被清除了！")

    def _handle_set_flag(self, params: Dict, context: Dict):
        target_def = params.get('target')
        if target_def:
            target = self._resolve_target(target_def, context)
            flag_name = params.get('flag_name')
            value = params.get('value')
            if target and flag_name:
                setattr(target, flag_name, value)
                print(f"[{target.name}] 的状态标志 '{flag_name}' 被设置为 {value}。")
    
    def _handle_modify_attribute(self, params: Dict, context: Dict) -> Dict | None:
        """处理被动属性修改，它只返回值，不执行动作。"""
        target_attr_name = context.get('attr_name')
        effect_target_attr = context['effect'].params.get('target_attribute')

        if target_attr_name == effect_target_attr:
            returns = params.get('returns', {})
            modifiers = {
                'ratio': self._resolve_value(returns.get('ratio', 1.0), context),
                'flat': self._resolve_value(returns.get('flat', 0.0), context)
            }
            return modifiers
        return None