import tomllib, importlib.metadata, pathlib, re, sys
import mujoco

def test_mujoco_pinned_exactly_and_recent_enough():
    deps = tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]["dependencies"]
    pins = [d for d in deps if d.startswith("mujoco")]
    assert len(pins) == 1 and re.fullmatch(r"mujoco==\d+\.\d+\.\d+", pins[0])
    assert importlib.metadata.version("mujoco") == pins[0].split("==")[1]
    assert tuple(map(int, mujoco.__version__.split(".")[:2])) >= (3, 7)

def test_python_is_312():
    assert sys.version_info[:2] == (3, 12)
