from enum import StrEnum


class ImpressionEntityTypeEnum(StrEnum):
    IMPRESSION = "Impressions"
    NEAR_ZONE = "Near Zone"
    FAR_ZONE = "Far Zone"
    IMMEDIATE_ZONE = "Immediate Zone"
    REMOTE_ZONE = "Remote Zone"
