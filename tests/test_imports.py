import importlib


def test_core_imports():
    modules = [
        "src.detect_edge",
        "src.utils",
        "src.gps_handler",
        "src.api_client",
        "src.esp32_camera",
        "src.database",
        "src.dashboard",
    ]

    for m in modules:
        # ensure module imports without raising unexpected exceptions
        importlib.import_module(m)

    assert True
