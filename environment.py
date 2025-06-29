import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class SimpleCardEnv(gym.Env):
    """
    A toy 1v1 card game, Gymnasium style.
    action: 0 = Attack, 1 = Defend, 2 = Heal
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self, max_hp: int = 30, max_round: int = 50, seed: int | None = None):
        super().__init__()
        self.max_hp = max_hp
        self.max_round = max_round

        # Discrete actions: play A / D / H
        self.action_space = spaces.Discrete(3)

        # obs = [my_hp, opp_hp, my_card_type]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0], dtype=np.int32),
            high=np.array([max_hp, max_hp, 2], dtype=np.int32),
            dtype=np.int32,
        )
        self.random = random.Random(seed)

    def _draw_card(self):
        # 随机抽 A, D, H
        return self.random.randint(0, 2)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.my_hp = self.opp_hp = self.max_hp
        self.round = 0
        self.my_card = self._draw_card()
        obs = np.array([self.my_hp, self.opp_hp, self.my_card], dtype=np.int32)
        info = {}
        return obs, info

    def step(self, action):
        self.round += 1

        # 取对手动作（随机策略演示）
        opp_action = self._draw_card()

        # 解析动作效果
        def apply(act, self_hp, opp_hp):
            if act == 0:               # Attack
                opp_hp -= 6
            elif act == 1:             # Defend
                self_hp += 3
            else:                      # Heal
                self_hp = min(self_hp + 5, self.max_hp)
            return self_hp, opp_hp

        self.my_hp, self.opp_hp = apply(action, self.my_hp, self.opp_hp)
        self.opp_hp, self.my_hp = apply(opp_action, self.opp_hp, self.my_hp)

        # 抽下一张手牌
        self.my_card = self._draw_card()

        # 终止条件
        terminated = (self.my_hp <= 0) or (self.opp_hp <= 0)
        truncated = self.round >= self.max_round

        # 奖励
        if terminated or truncated:
            if self.my_hp > self.opp_hp:
                reward = 1.0
            elif self.my_hp < self.opp_hp:
                reward = -1.0
            else:
                reward = 0.0
        else:
            reward = 0.0  # 纯终局奖励

        obs = np.array([self.my_hp, self.opp_hp, self.my_card], dtype=np.int32)
        info = {"opp_action": opp_action}
        return obs, reward, terminated, truncated, info

    def render(self, mode="human"):
        print(f"Round {self.round}: HP_you={self.my_hp}, HP_opp={self.opp_hp}, card={self.my_card}")
