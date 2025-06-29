from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hero import Unit

class Battle:
    def __init__(self, unit1: Unit, unit2: Unit):
        self.unit1 = unit1
        self.unit2 = unit2
        print("====== 战斗开始 ======")
        print(f"{self.unit1.name} VS {self.unit2.name}")

    def run(self):
        """执行战斗循环，直到一方倒下。"""
        turn = 1
        # 根据速度决定谁先手
        attacker, defender = sorted([self.unit1, self.unit2], key=lambda u: u.speed, reverse=True)
        
        while self.unit1.current_hp > 0 and self.unit2.current_hp > 0:
            print(f"\n★★★★★ 回合 {turn} ★★★★★")
            
            # 当前攻击者行动
            print(f"\n轮到 [{attacker.name}] 行动...")
            attacker.process_turn_start()
            attacker.act(defender)
            attacker.process_turn_end()

            # 检查战斗是否结束
            if self.unit1.current_hp <= 0 or self.unit2.current_hp <= 0:
                break
            
            # 交换角色
            attacker, defender = defender, attacker
            turn += 1

        # 战斗结束，宣布胜利者
        print("\n====== 战斗结束 ======")
        winner = self.unit1 if self.unit1.current_hp > 0 else self.unit2
        print(f"胜利者是：🏆 {winner.name}！")
        print("最终状态：")
        print(self.unit1)
        print(self.unit2)