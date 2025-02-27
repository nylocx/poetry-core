from typing import TYPE_CHECKING
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlparse

from poetry.core.packages.dependency import Dependency


if TYPE_CHECKING:
    from poetry.core.packages.constraints import BaseConstraint


class URLDependency(Dependency):
    def __init__(
        self,
        name: str,
        url: str,
        groups: Optional[List[str]] = None,
        optional: bool = False,
        extras: Union[List[str], FrozenSet[str]] = None,
    ):
        self._url = url

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"{url} does not seem like a valid url")

        super().__init__(
            name,
            "*",
            groups=groups,
            optional=optional,
            allows_prereleases=True,
            source_type="url",
            source_url=self._url,
            extras=extras,
        )

    @property
    def url(self) -> str:
        return self._url

    @property
    def base_pep_508_name(self) -> str:
        requirement = self.pretty_name

        if self.extras:
            extras = ",".join(self.extras)
            requirement += f"[{extras}]"

        requirement += f" @ {self._url}"

        return requirement

    def is_url(self) -> bool:
        return True

    def with_constraint(self, constraint: "BaseConstraint") -> "URLDependency":
        new = URLDependency(
            self.pretty_name,
            url=self._url,
            optional=self.is_optional(),
            groups=list(self._groups),
            extras=self._extras,
        )

        new._constraint = constraint
        new._pretty_constraint = str(constraint)

        new.is_root = self.is_root
        new.python_versions = self.python_versions
        new.marker = self.marker
        new.transitive_marker = self.transitive_marker

        for in_extra in self.in_extras:
            new.in_extras.append(in_extra)

        return new

    def __str__(self) -> str:
        return f"{self._pretty_name} ({self._pretty_constraint} url)"

    def __hash__(self) -> int:
        return hash((self._name, self._url))
