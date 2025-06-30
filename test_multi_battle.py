from factory_effect import EffectFactory
from factory_skill import SkillFactory
from factory_unit import UnitFactory
from multi_battle import MultiBattle
import random

def test_multi_battle():
    print("🎮 多英雄对战系统 - 自动测试")
    print("=" * 50)
    
    # 初始化工厂
    effect_factory = EffectFactory()
    skill_factory = SkillFactory(effect_factory)
    unit_factory = UnitFactory(skill_factory)
    
    # 加载数据
    effect_factory.load_effects_from_file('effects.yaml')
    skill_factory.load_skills_from_file('skills.yaml')
    unit_factory.load_heroes_from_file('hero.yaml')
    
    # 测试3v3对战
    team_size = 3
    print(f"\n测试 {team_size}v{team_size} 对战")
    
    # 自动获取所有可用英雄
    available_heroes = list(unit_factory._templates.keys())
    print(f"可用英雄: {', '.join(available_heroes)}")
    
    # 随机选择英雄
    team1_heroes = random.sample(available_heroes, team_size)
    team2_heroes = random.sample([h for h in available_heroes if h not in team1_heroes], team_size)
    
    print(f"队伍1: {', '.join(team1_heroes)}")
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

def test_skill_target_count():
    """测试技能的多目标功能"""
    print("\n🔍 测试技能多目标功能")
    print("=" * 30)
    
    # 初始化工厂
    effect_factory = EffectFactory()
    skill_factory = SkillFactory(effect_factory)
    unit_factory = UnitFactory(skill_factory)
    
    # 加载数据
    effect_factory.load_effects_from_file('effects.yaml')
    skill_factory.load_skills_from_file('skills.yaml')
    unit_factory.load_heroes_from_file('hero.yaml')
    
    # 创建测试英雄
    heroes = []
    for name in ["加尔鲁什", "吉安娜", "阿尔萨斯"]:
        hero = unit_factory.create(name)
        if hero:
            heroes.append(hero)
    
    if len(heroes) >= 3:
        print("测试闪电链技能 (target_count: 2)")
        user = heroes[0]
        opponents = heroes[1:]
        
        # 找到闪电链技能
        lightning_chain = None
        for skill in user.skills.values():
            if skill.name == "闪电链":
                lightning_chain = skill
                break
        
        if lightning_chain:
            print(f"闪电链目标数量: {lightning_chain.target_count}")
            print(f"对手数量: {len(opponents)}")
            lightning_chain.use(user, opponents[0])  # 传入第一个对手，但会随机选择多个

if __name__ == "__main__":
    test_skill_target_count()
    test_multi_battle() 