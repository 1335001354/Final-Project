# unit_factory.py
from __future__ import annotations
import yaml

from typing import Dict, Any, Optional, TYPE_CHECKING
from hero import Unit, Hero

if TYPE_CHECKING:
    from factory_skill import SkillFactory

class UnitFactory:
    def __init__(self, skill_factory: SkillFactory):
        self._templates: Dict[str, Dict] = {}
        self.skill_factory = skill_factory
        self.unit_classes = {'Unit': Unit, 'Hero': Hero}

    def load_heroes_from_file(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            all_heroes_data = yaml.safe_load(f)
        if all_heroes_data:
            for name, template_data in all_heroes_data.items():
                self._templates[name] = template_data
                print(f"从文件加载了英雄模板：'{name}'")

    def create(self, name: str, **kwargs) -> Optional[Unit]:
        template = self._templates.get(name)
        if not template:
            print(f"错误：尝试创建未定义的英雄 '{name}'。")
            return None

        skill_instances = []
        skills_config_list = template.get('skills', [])
        for skill_config in skills_config_list:
            skill_name = skill_config.get('name')
            if not skill_name: continue
            
            # 提取技能配置
            skill_params = skill_config.copy()
            skill_params.pop('name', None)
            
            # 提取自定义效果配置
            custom_effects = skill_params.pop('effects', None)
            
            skill_instance = self.skill_factory.create(skill_name, custom_effects=custom_effects, **skill_params)
            if skill_instance:
                skill_instances.append(skill_instance)

        final_stats = template.get('base_stats', {}).copy()
        final_stats.update(kwargs)
        
        UnitClass = self.unit_classes.get(template.get('class', 'Hero'), Hero)
        
        return UnitClass(
            name=name,
            skills=skill_instances,
            **final_stats
        )