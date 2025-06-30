# 测试新英雄和技能
from factory_effect import EffectFactory
from factory_skill import SkillFactory
from factory_unit import UnitFactory
from battle import Battle

def test_new_heroes():
    print("=== 测试新英雄和技能 ===")
    
    # 初始化工厂
    effect_factory = EffectFactory()
    skill_factory = SkillFactory(effect_factory)
    unit_factory = UnitFactory(skill_factory)
    
    # 加载数据
    effect_factory.load_effects_from_file('effects.yaml')
    skill_factory.load_skills_from_file('skills.yaml')
    unit_factory.load_heroes_from_file('hero.yaml')
    
    # 测试创建新英雄
    new_heroes = [
        "阿尔萨斯", "伊利丹", "萨尔", "泰兰德", 
        "乌瑟尔", "雷克萨", "玛法里奥", "希尔瓦娜斯"
    ]
    
    print("\n--- 测试英雄创建 ---")
    for hero_name in new_heroes:
        hero = unit_factory.create(hero_name)
        if hero:
            print(f"✓ {hero_name} 创建成功: {hero}")
        else:
            print(f"✗ {hero_name} 创建失败")
    
    # 测试几场战斗
    print("\n--- 测试战斗 ---")
    
    # 测试1: 阿尔萨斯 vs 伊利丹
    print("\n【战斗1】阿尔萨斯 vs 伊利丹")
    arthas = unit_factory.create("阿尔萨斯")
    illidan = unit_factory.create("伊利丹")
    if arthas and illidan:
        battle1 = Battle(arthas, illidan)
        battle1.run()
    
    print("\n" + "="*50)
    
    # 测试2: 萨尔 vs 泰兰德
    print("\n【战斗2】萨尔 vs 泰兰德")
    thrall = unit_factory.create("萨尔")
    tyrande = unit_factory.create("泰兰德")
    if thrall and tyrande:
        battle2 = Battle(thrall, tyrande)
        battle2.run()

if __name__ == "__main__":
    test_new_heroes() 