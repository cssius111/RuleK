from enum import Enum


class GamePhase(str, Enum):
    """遊戲階段枚舉"""

    SETUP = "setup"
    MORNING_DIALOGUE = "morning_dialogue"
    EVENING_DIALOGUE = "evening_dialogue"
    ACTION = "action"
    RESOLUTION = "resolution"


class GameMode(str, Enum):
    """遊戲模式枚舉"""

    BACKSTAGE = "backstage"
    IN_SCENE = "in_scene"


__all__ = ["GamePhase", "GameMode"]
