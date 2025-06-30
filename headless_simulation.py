from factory_effect import EffectFactory
from factory_skill import SkillFactory
from factory_unit import UnitFactory
from multi_battle import MultiBattle
import random
import time
from collections import defaultdict

def run_single_battle(unit_factory, team1_names, team2_names, silent=True):
    """运行单场战斗"""
    # 创建英雄实例
    team1_units = []
    team2_units = []
    
    for hero_name in team1_names:
        unit = unit_factory.create(hero_name)
        if unit:
            team1_units.append(unit)
    
    for hero_name in team2_names:
        unit = unit_factory.create(hero_name)
        if unit:
            team2_units.append(unit)
    
    if not team1_units or not team2_units:
        return None
    
    # 开始战斗
    battle = MultiBattle(team1_units, team2_units, silent=silent)
    return battle.run()

def run_batch_simulation(num_battles=100, team_size=4):
    """运行批量模拟"""
    print(f"🤖 Headless模拟模式")
    print(f"=" * 50)
    print(f"运行 {num_battles} 场 {team_size}v{team_size} 战斗...")
    
    # 初始化工厂
    effect_factory = EffectFactory()
    skill_factory = SkillFactory(effect_factory)
    unit_factory = UnitFactory(skill_factory)
    
    # 加载数据（静默加载）
    effect_factory.load_effects_from_file('effects.yaml')
    skill_factory.load_skills_from_file('skills.yaml')
    unit_factory.load_heroes_from_file('hero.yaml')
    
    # 获取所有可用英雄
    available_heroes = list(unit_factory._templates.keys())
    
    # 统计数据
    results = {
        'team1_wins': 0,
        'team2_wins': 0,
        'draws': 0,
        'total_turns': 0,
        'hero_win_rates': defaultdict(lambda: {'wins': 0, 'games': 0}),
        'hero_vs_hero': defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'games': 0})),
        'battle_results': []
    }
    
    start_time = time.time()
    
    for i in range(num_battles):
        # 随机选择英雄
        team1_heroes = random.sample(available_heroes, team_size)
        team2_heroes = random.sample([h for h in available_heroes if h not in team1_heroes], team_size)
        
        # 运行战斗
        result = run_single_battle(unit_factory, team1_heroes, team2_heroes, silent=True)
        
        if result:
            results['battle_results'].append({
                'team1': team1_heroes,
                'team2': team2_heroes,
                'winner': result['winner'],
                'turns': result['turns'],
                'survivors': result['survivors']
            })
            
            # 统计胜负
            if result['winner'] == 'team1':
                results['team1_wins'] += 1
                # 统计整体英雄胜率
                for hero in team1_heroes:
                    results['hero_win_rates'][hero]['wins'] += 1
                    results['hero_win_rates'][hero]['games'] += 1
                for hero in team2_heroes:
                    results['hero_win_rates'][hero]['games'] += 1
                
                # 统计英雄对英雄胜率
                for hero1 in team1_heroes:
                    for hero2 in team2_heroes:
                        results['hero_vs_hero'][hero1][hero2]['wins'] += 1
                        results['hero_vs_hero'][hero1][hero2]['games'] += 1
                        results['hero_vs_hero'][hero2][hero1]['games'] += 1
                        
            elif result['winner'] == 'team2':
                results['team2_wins'] += 1
                # 统计整体英雄胜率
                for hero in team2_heroes:
                    results['hero_win_rates'][hero]['wins'] += 1
                    results['hero_win_rates'][hero]['games'] += 1
                for hero in team1_heroes:
                    results['hero_win_rates'][hero]['games'] += 1
                
                # 统计英雄对英雄胜率
                for hero2 in team2_heroes:
                    for hero1 in team1_heroes:
                        results['hero_vs_hero'][hero2][hero1]['wins'] += 1
                        results['hero_vs_hero'][hero2][hero1]['games'] += 1
                        results['hero_vs_hero'][hero1][hero2]['games'] += 1
                        
            else:
                results['draws'] += 1
                # 平局时所有英雄都算参与但不算胜利
                for hero in team1_heroes + team2_heroes:
                    results['hero_win_rates'][hero]['games'] += 1
                
                # 平局时英雄对英雄也算参与但不算胜利
                for hero1 in team1_heroes:
                    for hero2 in team2_heroes:
                        results['hero_vs_hero'][hero1][hero2]['games'] += 1
                        results['hero_vs_hero'][hero2][hero1]['games'] += 1
            
            results['total_turns'] += result['turns']
        
        # 显示进度
        if (i + 1) % (num_battles // 10) == 0:
            progress = (i + 1) / num_battles * 100
            print(f"进度: {progress:.0f}% ({i + 1}/{num_battles})")
    
    end_time = time.time()
    
    # 输出结果
    print(f"\n📊 模拟结果统计")
    print(f"=" * 50)
    print(f"总战斗数: {num_battles}")
    print(f"模拟时间: {end_time - start_time:.2f}秒")
    print(f"平均每场战斗: {(end_time - start_time) / num_battles * 1000:.1f}毫秒")
    
    print(f"\n胜负统计:")
    print(f"队伍1胜利: {results['team1_wins']} ({results['team1_wins']/num_battles*100:.1f}%)")
    print(f"队伍2胜利: {results['team2_wins']} ({results['team2_wins']/num_battles*100:.1f}%)")
    print(f"平局: {results['draws']} ({results['draws']/num_battles*100:.1f}%)")
    
    print(f"\n战斗数据:")
    print(f"平均回合数: {results['total_turns']/num_battles:.1f}")
    
    # 英雄胜率排行
    print(f"\n🏆 英雄胜率排行 (至少参与10场):")
    hero_stats = []
    for hero, stats in results['hero_win_rates'].items():
        if stats['games'] >= 10:
            win_rate = stats['wins'] / stats['games'] * 100
            hero_stats.append((hero, win_rate, stats['games'], stats['wins']))
    
    hero_stats.sort(key=lambda x: x[1], reverse=True)
    
    for i, (hero, win_rate, games, wins) in enumerate(hero_stats[:10]):
        print(f"{i+1:2d}. {hero:12s} {win_rate:5.1f}% ({wins:3d}/{games:3d})")
    
    # 英雄对英雄胜率表
    print_hero_vs_hero_table(results['hero_vs_hero'], available_heroes)
    
    return results

def print_hero_vs_hero_table(hero_vs_hero_data, available_heroes, min_games=3):
    """打印英雄对英雄的胜率表"""
    print(f"\n⚔️ 英雄对战胜率表 (至少{min_games}场对战):")
    print("=" * 80)
    
    # 筛选有足够对战数据的英雄对
    valid_matchups = []
    for hero1 in available_heroes:
        for hero2 in available_heroes:
            if hero1 != hero2:
                data = hero_vs_hero_data[hero1][hero2]
                if data['games'] >= min_games:
                    win_rate = data['wins'] / data['games'] * 100
                    valid_matchups.append((hero1, hero2, win_rate, data['games'], data['wins']))
    
    if not valid_matchups:
        print("没有足够的对战数据生成胜率表")
        return
    
    # 按胜率排序
    valid_matchups.sort(key=lambda x: x[2], reverse=True)
    
    print("最强克制关系 (前15位):")
    print(f"{'英雄1':12s} vs {'英雄2':12s} {'胜率':>6s} {'对战数':>6s}")
    print("-" * 50)
    
    for i, (hero1, hero2, win_rate, games, wins) in enumerate(valid_matchups[:15]):
        print(f"{hero1:12s} vs {hero2:12s} {win_rate:5.1f}% ({wins:2d}/{games:2d})")
    
    # 为每个英雄生成个人胜率表
    print(f"\n📋 各英雄详细胜率表:")
    print("=" * 80)
    
    for hero in available_heroes:
        matchups = []
        for opponent in available_heroes:
            if hero != opponent:
                data = hero_vs_hero_data[hero][opponent]
                if data['games'] >= min_games:
                    win_rate = data['wins'] / data['games'] * 100
                    matchups.append((opponent, win_rate, data['games'], data['wins']))
        
        if matchups:
            matchups.sort(key=lambda x: x[1], reverse=True)
            print(f"\n{hero} 的对战记录:")
            print(f"{'对手':12s} {'胜率':>6s} {'对战数':>6s}")
            print("-" * 30)
            
            for opponent, win_rate, games, wins in matchups:
                status = "💪" if win_rate >= 70 else "⚔️" if win_rate >= 50 else "😰"
                print(f"{opponent:12s} {win_rate:5.1f}% ({wins:2d}/{games:2d}) {status}")

def analyze_hero_relationships(hero_vs_hero_data, available_heroes, min_games=5):
    """分析英雄之间的克制关系"""
    print(f"\n🔍 英雄克制关系分析:")
    print("=" * 50)
    
    # 找出最强的克制关系
    strongest_counters = []
    for hero1 in available_heroes:
        for hero2 in available_heroes:
            if hero1 != hero2:
                data = hero_vs_hero_data[hero1][hero2]
                if data['games'] >= min_games:
                    win_rate = data['wins'] / data['games'] * 100
                    if win_rate >= 75:  # 胜率超过75%算强克制
                        strongest_counters.append((hero1, hero2, win_rate, data['games']))
    
    if strongest_counters:
        strongest_counters.sort(key=lambda x: x[2], reverse=True)
        print("强克制关系 (胜率≥75%):")
        for hero1, hero2, win_rate, games in strongest_counters:
            print(f"  {hero1} 克制 {hero2} ({win_rate:.1f}%, {games}场)")
    
    # 找出最均衡的对战
    balanced_matchups = []
    for hero1 in available_heroes:
        for hero2 in available_heroes:
            if hero1 < hero2:  # 避免重复
                data1 = hero_vs_hero_data[hero1][hero2]
                data2 = hero_vs_hero_data[hero2][hero1]
                total_games = data1['games'] + data2['games']
                if total_games >= min_games * 2:
                    hero1_wins = data1['wins']
                    hero2_wins = data2['wins']
                    total_wins = hero1_wins + hero2_wins
                    if total_wins > 0:
                        hero1_rate = hero1_wins / total_wins * 100
                        if 45 <= hero1_rate <= 55:  # 胜率在45-55%之间算均衡
                            balanced_matchups.append((hero1, hero2, hero1_rate, total_games))
    
    if balanced_matchups:
        print(f"\n均衡对战 (胜率45-55%):")
        for hero1, hero2, hero1_rate, games in balanced_matchups:
            print(f"  {hero1} vs {hero2} ({hero1_rate:.1f}% vs {100-hero1_rate:.1f}%, {games}场)")

def run_specific_matchup(team1_names, team2_names, num_battles=50):
    """运行特定对阵的多场战斗"""
    print(f"\n⚔️ 特定对阵模拟")
    print(f"=" * 30)
    print(f"队伍1: {', '.join(team1_names)}")
    print(f"队伍2: {', '.join(team2_names)}")
    print(f"战斗场数: {num_battles}")
    
    # 初始化工厂
    effect_factory = EffectFactory()
    skill_factory = SkillFactory(effect_factory)
    unit_factory = UnitFactory(skill_factory)
    
    # 加载数据
    effect_factory.load_effects_from_file('effects.yaml')
    skill_factory.load_skills_from_file('skills.yaml')
    unit_factory.load_heroes_from_file('hero.yaml')
    
    team1_wins = 0
    team2_wins = 0
    draws = 0
    total_turns = 0
    
    for i in range(num_battles):
        result = run_single_battle(unit_factory, team1_names, team2_names, silent=True)
        if result:
            if result['winner'] == 'team1':
                team1_wins += 1
            elif result['winner'] == 'team2':
                team2_wins += 1
            else:
                draws += 1
            total_turns += result['turns']
    
    print(f"\n结果:")
    print(f"队伍1胜利: {team1_wins} ({team1_wins/num_battles*100:.1f}%)")
    print(f"队伍2胜利: {team2_wins} ({team2_wins/num_battles*100:.1f}%)")
    print(f"平局: {draws} ({draws/num_battles*100:.1f}%)")
    print(f"平均回合数: {total_turns/num_battles:.1f}")

def main():
    print("🎮 Headless战斗模拟器")
    print("=" * 50)
    
    # 运行批量模拟
    results = run_batch_simulation(num_battles=200, team_size=3)
    
    # 分析英雄克制关系
    analyze_hero_relationships(results['hero_vs_hero'], list(results['hero_win_rates'].keys()))
    
    # 运行特定对阵测试
    run_specific_matchup(
        team1_names=["加尔鲁什", "吉安娜", "阿尔萨斯"],
        team2_names=["伊利丹", "萨尔", "泰兰德"],
        num_battles=20
    )

if __name__ == "__main__":
    main() 