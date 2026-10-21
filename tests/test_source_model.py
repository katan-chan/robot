"""Kiểm model nguồn đã commit models/spider.blend (không chỉ model dựng mới trong tmp).
Xuất vào tmp_path, không sửa file .blend. Dùng lại các test của test_build.py với fixture dưới đây."""
import pytest

from tests.test_build import ROOT, blender
from tests.test_build import (test_feet_match_blender_at_home, test_stand_keyframe_feet_on_floor,  # noqa: F401
                              test_total_mass_in_budget)

SOURCE = ROOT / "models/spider.blend"


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    out = tmp_path_factory.mktemp("source") / "model"
    blender("export", "--blend", str(SOURCE), "--out", str(out))
    return out


@pytest.fixture(scope="module")
def inspected():
    return blender("inspect", "--blend", str(SOURCE))


def test_source_model_inspect_ok(inspected):
    assert inspected["ok"] and len(inspected["links"]) == 13
