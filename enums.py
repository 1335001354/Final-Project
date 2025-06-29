from enum import Enum, auto

class TriggerPhase(Enum):
    # --- 新增下面这两行 ---
    ON_APPLY = auto()        # 效果被施加时
    ON_REMOVE = auto()       # 效果被移除时

    # --- 保留已有成员 ---
    PASSIVE = auto()         # 被动属性修改
    ON_TURN_START = auto()   # 回合开始时
    ON_TURN_END = auto()     # 回合结束时
    ON_DEAL_DAMAGE = auto()  # 当持有者造成伤害时
    ON_TAKE_DAMAGE = auto()  # 当持有者受到伤害时
    ON_ACTION = auto()       # 当持有者出手时