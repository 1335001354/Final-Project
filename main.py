# 1. 导入所有必要的工厂和核心类

from factory_effect import EffectFactory
from factory_skill import SkillFactory
from factory_unit import UnitFactory
from battle import Battle

def main():
    # --- 步骤一：初始化所有系统模块（工厂） ---
    print("--- 正在初始化系统模块... ---")
    effect_factory = EffectFactory()
    # 技能工厂依赖效果工厂来创建技能附带的效果
    skill_factory = SkillFactory(effect_factory)
    # 单位工厂依赖技能工厂来为英雄创建技能
    unit_factory = UnitFactory(skill_factory)

    # --- 步骤二：从文件加载所有游戏内容数据 ---
    print("\n--- 正在加载游戏内容数据... ---")
    effect_factory.load_effects_from_file('effects.yaml')
    skill_factory.load_skills_from_file('skills.yaml')
    unit_factory.load_heroes_from_file('hero.yaml')

    # --- 步骤三：使用工厂创建游戏世界的顶层对象（英雄） ---
    # 您现在只需要提供英雄的名字，所有数值和技能都将从YAML文件中自动加载和装配
    print("\n--- 正在创建英雄... ---")
    garrosh = unit_factory.create("加尔鲁什")
    jaina = unit_factory.create("吉安娜")

    # 检查英雄是否成功创建
    if not garrosh or not jaina:
        print("英雄创建失败，战斗无法开始。")
        return
        
    print("\n--- 英雄准备就绪 ---")
    print(garrosh)
    print(jaina)

    # --- 步骤四：启动核心游戏逻辑（战斗） ---
    battle = Battle(garrosh, jaina)
    battle.run()

if __name__ == "__main__":
    main()