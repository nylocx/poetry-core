from pathlib import Path
from typing import TYPE_CHECKING
from typing import Optional
from typing import Union


if TYPE_CHECKING:
    from poetry.core.poetry import Poetry  # noqa


class Builder:
    def __init__(self, poetry: "Poetry") -> None:
        from poetry.core.masonry.builders.sdist import SdistBuilder
        from poetry.core.masonry.builders.wheel import WheelBuilder

        self._poetry = poetry

        self._formats = {
            "sdist": SdistBuilder,
            "wheel": WheelBuilder,
        }

    def build(self, fmt: str, executable: Optional[Union[str, Path]] = None) -> None:
        if fmt in self._formats:
            builders = [self._formats[fmt]]
        elif fmt == "all":
            builders = list(self._formats.values())
        else:
            raise ValueError(f"Invalid format: {fmt}")

        for builder in builders:
            builder(self._poetry, executable=executable).build()
