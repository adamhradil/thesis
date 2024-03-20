from enum import Enum


class Disposition(Enum):
    ONE_PLUS_KK = "1+kk"
    ONE_PLUS_ONE = "1+1"
    TWO_PLUS_KK = "2+kk"
    TWO_PLUS_ONE = "2+1"
    THREE_PLUS_KK = "3+kk"
    THREE_PLUS_ONE = "3+1"
    FOUR_PLUS_KK = "4+kk"
    FOUR_PLUS_ONE = "4+1"
    FIVE_PLUS_KK = "5+kk"
    FIVE_PLUS_ONE = "5+1"
    SIX_AND_LARGER = "6-a-více"
    OTHER = "other"
