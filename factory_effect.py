from __future__ import annotations
from typing import Dict, Callable, Any, Optional
import yaml
from effect import GenericEffect # 导入我们通用的Effect类
from enums import TriggerPhase


# 定义逻辑函数的标准签名：接受效果实例和目标单位作为参数
EffectLogicCallable = Callable[[GenericEffect, Any], None]

class EffectFactory:
    def __init__(self):
        # _templates 用于存储已注册的效果“模板”
        self._templates: Dict[str, Dict] = {}

    def load_effects_from_file(self,file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            all_effects_data = yaml.safe_load(f)
        for name, template_data in all_effects_data.items():
            self._templates[name] = template_data
            print(f"已加载效果模板：{name}")
    
    def create(self, name: str, **kwargs) -> Optional[GenericEffect]:
        """
        根据名称创建一个效果实例。

        Args:
            name (str): 要创建的效果的名称。
            **kwargs: 实例化时提供的参数，将覆盖默认参数。

        Returns:
            一个 GenericEffect 的实例，如果名称未注册则返回 None。
        """
        template = self._templates.get(name)
        if not template:
            print(f"错误：尝试创建未注册的效果 '{name}'。")
            return None

        # 合并参数：默认参数被实例化参数覆盖
        final_params = template.get("default_params", {}).copy()
        final_params.update(kwargs)

        return GenericEffect(
            name=name,
            logic_hooks=template["logic_hooks"],
            **final_params
        )

    def register(self,
                 name: str,
                 logic_hooks: Dict[TriggerPhase, EffectLogicCallable],
                 default_params: Optional[Dict[str, Any]] = None):
        """
        注册一个新的异常状态类型。

        Args:
            name (str): 异常状态的唯一名称。
            logic_hooks (Dict): 定义此状态在不同阶段的行为逻辑。
            default_params (Dict, optional): 此状态的默认参数 (如默认持续时间)。
        """
        if name in self._templates:
            print(f"警告：正在覆盖已注册的效果 '{name}'。")
        
        self._templates[name] = {
            "logic_hooks": logic_hooks,
            "default_params": default_params if default_params is not None else {}
        }
        print(f"成功注册新异常状态：'{name}'。")