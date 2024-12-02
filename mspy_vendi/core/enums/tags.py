from enum import StrEnum


class ApiTagEnum(StrEnum):
    HEALTH_CHECK = "Health Check"
    USER = "User"
    ACTIVITY_LOG = "[Admin] Activity Log"
    ADMIN_USER = "[Admin] User"
    AUTH_LOGIN = "[Auth] Login"
    AUTH_RESISTER = "[Auth] Register"
    AUTH_VERIFY = "[Auth] Verify"
    AUTH_RESET_PASSWORD = "[Auth] Reset Password"
    SALES = "Sales"
    MACHINES = "Machines"
    MACHINE_IMPRESSION = "Machine Impression"
    IMPRESSIONS = "Impressions"
    GEOGRAPHIES = "Geographies"
