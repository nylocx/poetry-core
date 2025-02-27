from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pep517.build import build
from pep517.check import check

from tests.testutils import subprocess_run
from tests.testutils import temporary_project_directory


if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "getter, project",
    [
        ("common_project", "simple_project"),
        ("masonry_project", "src_extended"),
        ("masonry_project", "disable_setup_py"),
    ],
)
def test_pep517_check_poetry_managed(
    request: "FixtureRequest", getter: str, project: str
):
    with temporary_project_directory(request.getfixturevalue(getter)(project)) as path:
        assert check(path)


def test_pep517_check(project_source_root: Path):
    assert check(str(project_source_root))


def test_pep517_build_sdist(temporary_directory: Path, project_source_root: Path):
    build(
        source_dir=str(project_source_root), dist="sdist", dest=str(temporary_directory)
    )
    distributions = list(temporary_directory.glob("poetry-core-*.tar.gz"))
    assert len(distributions) == 1


def test_pep517_build_wheel(temporary_directory: Path, project_source_root: Path):
    build(
        source_dir=str(project_source_root), dist="wheel", dest=str(temporary_directory)
    )
    distributions = list(temporary_directory.glob("poetry_core-*-none-any.whl"))
    assert len(distributions) == 1


def test_pip_wheel_build(temporary_directory: Path, project_source_root: Path):
    tmp = str(temporary_directory)
    pip = subprocess_run(
        "pip", "wheel", "--use-pep517", "-w", tmp, str(project_source_root)
    )
    assert "Successfully built poetry-core" in pip.stdout

    assert pip.returncode == 0

    wheels = list(Path(tmp).glob("poetry_core-*-none-any.whl"))
    assert len(wheels) == 1


def test_pip_install_no_binary(python: str, project_source_root: Path):
    subprocess_run(
        python,
        "-m",
        "pip",
        "install",
        "--no-binary",
        ":all:",
        project_source_root.as_posix(),
    )

    pip_show = subprocess_run(python, "-m", "pip", "show", "poetry-core")
    assert "Name: poetry-core" in pip_show.stdout
