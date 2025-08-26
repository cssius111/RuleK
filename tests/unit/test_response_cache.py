from pathlib import Path

from src.api.deepseek_http_client import ResponseCache


def test_set_creates_error_file_on_failure(tmp_path, monkeypatch):
    cache = ResponseCache(tmp_path)

    original_open = Path.open

    def fake_open(self, mode="r", *args, **kwargs):
        if str(self).endswith(".json") and "w" in mode:
            raise OSError("disk error")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    cache.set("p", {"k": "v"}, {"result": True})

    error_files = list(tmp_path.glob("*.error"))
    assert len(error_files) == 1


def test_get_removes_error_file(tmp_path):
    cache = ResponseCache(tmp_path)
    key = cache._generate_key("p", {"k": "v"})
    error_file = tmp_path / f"{key}.error"
    error_file.touch()

    result = cache.get("p", {"k": "v"})

    assert result is None
    assert not error_file.exists()

