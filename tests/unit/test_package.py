import re

import agent_platform


def test_version_is_semver() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", agent_platform.__version__)
