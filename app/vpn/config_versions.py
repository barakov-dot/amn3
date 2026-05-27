from app.vpn.amneziawg_v1_5.config import render_client_config as render_v1_5_config
from app.vpn.amneziawg_v2.config import ClientConfigInput
from app.vpn.amneziawg_v2.config import render_client_config as render_v2_config


SUPPORTED_CONFIG_VERSIONS = ("amneziawg_v1_5", "amneziawg_v2")


class ConfigVersionError(ValueError):
    pass


def validate_config_version(version: str) -> str:
    if version not in SUPPORTED_CONFIG_VERSIONS:
        supported = ", ".join(SUPPORTED_CONFIG_VERSIONS)
        raise ConfigVersionError(f"Unsupported config version: {version}. Supported: {supported}")
    return version


def render_client_config_for_version(config: ClientConfigInput, version: str) -> str:
    validated = validate_config_version(version)
    if validated == "amneziawg_v1_5":
        return render_v1_5_config(config)
    return render_v2_config(config)
