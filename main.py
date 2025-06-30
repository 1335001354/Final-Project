# 1. 导入所有必要的工厂和核心类

from factory_effect import EffectFactory
from factory_skill import SkillFactory
from factory_unit import UnitFactory
from multi_battle import MultiBattle
import random

def get_available_heroes(unit_factory: UnitFactory) -> list:
    """从unit_factory中获取所有可用的英雄列表"""
    return list(unit_factory._templates.keys())

def main():
    print("🎮 多英雄对战系统")
    print("=" * 50)
    
    # 初始化工厂
    effect_factory = EffectFactory()
    skill_factory = SkillFactory(effect_factory)
    unit_factory = UnitFactory(skill_factory)
    
    # 加载数据
    effect_factory.load_effects_from_file('effects.yaml')
    skill_factory.load_skills_from_file('skills.yaml')
    unit_factory.load_heroes_from_file('hero.yaml')
    
    # 自动设置队伍人数为4
    team_size = 4
    print(f"\n自动设置每队 {team_size} 个英雄进行对战")
    
    # 自动获取所有可用英雄
    available_heroes = list(unit_factory._templates.keys())
    print(f"可用英雄池: {', '.join(available_heroes)}")
    
    # 自动随机选择英雄
    team1_heroes = random.sample(available_heroes, team_size)
    team2_heroes = random.sample([h for h in available_heroes if h not in team1_heroes], team_size)
    
    print(f"\n队伍1: {', '.join(team1_heroes)}")
    print(f"队伍2: {', '.join(team2_heroes)}")
    
    # 创建英雄实例
    team1_units = []
    team2_units = []
    
    for hero_name in team1_heroes:
        unit = unit_factory.create(hero_name)
        if unit:
            team1_units.append(unit)
    
    for hero_name in team2_heroes:
        unit = unit_factory.create(hero_name)
        if unit:
            team2_units.append(unit)
    
    # 开始战斗
    if team1_units and team2_units:
        battle = MultiBattle(team1_units, team2_units)
        battle.run()
    else:
        print("创建英雄失败，无法开始战斗")

if __name__ == "__main__":
    main()