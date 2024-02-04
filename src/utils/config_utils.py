import os
from functools import lru_cache

import hiyapyco
from pydantic import BaseModel, SecretStr, field_validator, Extra
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet
import base64


class Constants:
    CONFIG_ROOT_PATH = "config"


class ServiceSettings(BaseSettings):
    ENCRYPTION_KEY: str

    class Config:
        extra = Extra.ignore

# Uncomment when trying to run this file to encrypt any secrets
os.environ["ENCRYPTION_KEY"] = "RagAThon-key-2024-@1"

service_settings = ServiceSettings()
if len(service_settings.ENCRYPTION_KEY * 5) < 32:
    raise ValueError("Encryption Key should be longer")
cryptor = Fernet(base64.urlsafe_b64encode((service_settings.ENCRYPTION_KEY * 5)[:32].encode("utf-8")))


class RootConfig(BaseModel):
    @field_validator('*')
    def decrypt_config(cls, v):
        if isinstance(v, SecretStr) and service_settings.ENCRYPTION_KEY:
            v = v.get_secret_value()
            if v.startswith("enc(") and v.endswith(")"):
                v = v[4:-1]
                v = SecretStr(cryptor.decrypt(v).decode('utf-8'))
            else:
                raise Exception("Invalid encrypted value")
        return v


class AstraDBConfig(RootConfig):
    endpoint_url: str
    token: SecretStr

    image_collection_name: str


class ServiceConfig(BaseModel):
    service_name: str
    db_config_astra: AstraDBConfig


@lru_cache(maxsize=1)
def load_config_object():
    paths = [os.path.join(Constants.CONFIG_ROOT_PATH, "config.yml")]
    merged_yaml = hiyapyco.load(*paths)
    service_config_object = ServiceConfig(**merged_yaml)
    return service_config_object


if __name__ == "__main__":
    secret_str = "AstraCS:DilDjrIoNYCpXvSygevPPhAQ:ca0d97a0bd26c91ca002b03105134d0204cd2c52f0abba4cc8528881c6dedbe6"
    print(cryptor.encrypt(secret_str.encode('utf-8')))
