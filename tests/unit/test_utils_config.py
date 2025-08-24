from src.utils.config import _parse_cors_origins, Config


def test_parse_cors_origins_json():
    assert _parse_cors_origins('["http://a.com", "http://b.com"]') == [
        "http://a.com",
        "http://b.com",
    ]


def test_parse_cors_origins_python_list():
    assert _parse_cors_origins("['http://a.com', 'http://b.com']") == [
        "http://a.com",
        "http://b.com",
    ]


def test_parse_cors_origins_comma_separated():
    assert _parse_cors_origins('http://a.com, http://b.com') == [
        "http://a.com",
        "http://b.com",
    ]


def test_get_web_config_uses_parser(monkeypatch):
    monkeypatch.setenv('WEB_CORS_ORIGINS', 'http://a.com, http://b.com')
    cfg = Config()
    web = cfg.get_web_config()
    assert web['cors_origins'] == ["http://a.com", "http://b.com"]
