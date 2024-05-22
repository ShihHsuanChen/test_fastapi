import os
from typing import Optional

import dotenv
from pydantic import BaseSettings, SecretStr


class AppConfig(BaseSettings):

    root_path: str = ''
    product_name: str = 'AAAAAAA'

    class Config:
        case_sensitive = False

    @classmethod
    def load_configs(cls,
            env_file: Optional[str] = '.env',
            create_default: bool = False,
            verbose: bool = True,
            ) -> BaseSettings:
        if env_file is None:
            return cls()

        env_file = os.path.normpath(os.path.expanduser(env_file))
        if not os.path.isfile(env_file):
            config = cls()

            print(f'Create env file with default values: {env_file}')
            with open(env_file, 'w') as fp:
                fp.write('')
            for k, v in config.dict().items():
                if isinstance(v, SecretStr):
                    v = v.get_secret_value()
                _v = '' if v is None else json.dumps(v)
                _k = k.upper()
                _k = f'# {_k}' if v is None else _k
                dotenv.set_key(env_file, _k, _v, quote_mode='never')
            return config
        else:
            cls.Config.env_file = env_file
            return cls()


cfg = AppConfig.load_configs()
