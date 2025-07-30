import json
from src.utils.config import Config, load_config, config


def test_load_config(tmp_path):
    # ensure load_config returns Config instance
    cfg_file = tmp_path / "extra.json"
    cfg_file.write_text(json.dumps({"sample_key": "sample_value"}))

    cfg = load_config(str(cfg_file))
    assert isinstance(cfg, Config)
    assert cfg.get("sample_key") == "sample_value"


def test_global_config_exposes_helpers():
    assert isinstance(config.get_deepseek_config(), dict)
    assert hasattr(config, "is_test_mode")
