class ContestStatus:
    CONTEST_NOT_START = "1"
    CONTEST_ENDED = "-1"
    CONTEST_UNDERWAY = "0"


class ContestType:
    PUBLIC_CONTEST = "Public"
    PASSWORD_PROTECTED_CONTEST = "Password Protected"


class RuleType:
    ACM = "ACM"
    OI = "OI"


class Difficulty:
    EASY = 1
    NORMAL = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5


class AdminType:
    USER = 1
    ADMIN = 2
    SUPER_ADMIN = 3


class JudgeStatus:
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    CPU_TIME_LIMIT_EXCEEDED = 1
    REAL_TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5
    PENDING = 6
    JUDGING = 7
    PARTIALLY_ACCEPTED = 8
