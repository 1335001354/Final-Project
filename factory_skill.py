# skill_factory.py
from __future__ import annotations
import yaml
from typing import Dict, Any, Optional, TYPE_CHECKING
from skill import Skill

if TYPE_CHECKING:
    from factory_effect import EffectFactory

class SkillFactory:
    def __init__(self, effect_factory: EffectFactory):
        self._templates: Dict[str, Dict] = {}
        self.effect_factory = effect_factory

    def load_skills_from_file(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            all_skills_data = yaml.safe_load(f)
        if all_skills_data:
            for name, template_data in all_skills_data.items():
                self._templates[name] = template_data
                print(f"从文件加载了技能模板：'{name}'")

    def create(self, name: str, **kwargs) -> Optional[Skill]:
        template = self._templates.get(name)
        if not template:
            print(f"错误：尝试创建未注册的技能 '{name}'。")
            return None
            
        final_params = template.copy()
        final_params.update(kwargs)

        return Skill(
            name=name,
            effect_factory=self.effect_factory,
            **final_params
        )
    