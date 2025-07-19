from main import main


class TestMain:
    def test_main_returns_none(self) -> None:
        assert main() is None
