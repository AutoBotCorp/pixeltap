from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    AUTO_DAILY_JOIN: bool = True
    AUTO_DAILY_COMBO: bool = True
    AUTO_CLAIM: bool = True
    AUTO_UPGRADE: bool = True
    AUTO_BUY: bool = False
    AUTO_BATTLE: bool = False
    DELAY_BETWEEN_BATTLES: list[int] = [5, 10]
    CLICK_COOLDOWN: list[float] = [0.085, 0.09]
    BATTLES_COUNT: int = 10
    BATTLE_METHOD: int = 2
    PET_NAME: str = 'null'
    MAX_PET_LVL: int = 0

    REF_ID: str = '6451244166'
    FAKE_USERAGENT: bool = True

    USE_RANDOM_DELAY_IN_RUN: bool = True
    RANDOM_DELAY_IN_RUN: list[int] = [0, 10]

    ENABLE_PROXY: bool = True

settings = Settings()


