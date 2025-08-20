import sys
from pathlib import Path

from config.config_manager import ConfigManager


def test_check_executable_with_absolute_path():
    cm = ConfigManager()
    assert cm._check_executable(sys.executable)


def test_check_executable_with_basename_in_path():
    cm = ConfigManager()
    exe_name = Path(sys.executable).name
    assert cm._check_executable(exe_name)


def test_check_executable_with_stem_in_path():
    cm = ConfigManager()
    exe_stem = Path(sys.executable).stem
    assert cm._check_executable(exe_stem)


def test_check_executable_not_found():
    cm = ConfigManager()
    assert not cm._check_executable("not_a_real_command")
