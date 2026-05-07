from __future__ import annotations

import marimo as mo
from hotdata_core_notebook.client import HotdataClient
from hotdata_core_notebook.env import (
    default_api_key,
    default_host,
    default_session_id,
    explicit_workspace_id,
    list_workspaces,
)


class WorkspaceSelector:
    """Workspace picker that rebuilds `HotdataClient` as selection changes."""

    def __init__(
        self,
        *,
        api_key: str,
        host: str | None = None,
        session_id: str | None = None,
        label: str = "Workspace",
    ) -> None:
        self._api_key = api_key
        self._host = host or default_host()
        self._session_id = session_id
        self._explicit = explicit_workspace_id()

        workspaces = list_workspaces(api_key, self._host, session_id)
        if not workspaces:
            raise RuntimeError("No Hotdata workspaces found for this API key.")

        if self._explicit:
            self._pick = None
            self._workspace_id = self._explicit
            return

        if len(workspaces) == 1:
            self._pick = None
            self._workspace_id = workspaces[0].public_id
            return

        active = [w for w in workspaces if w.active]
        chosen = active[0] if active else workspaces[0]

        labels: list[tuple[str, str]] = []
        seen: set[str] = set()
        for w in workspaces:
            base = w.name
            label_text = base if base not in seen else f"{base} ({w.public_id})"
            seen.add(base)
            labels.append((label_text, w.public_id))

        labels.sort(key=lambda t: 0 if t[1] == chosen.public_id else 1)
        options = {k: v for k, v in labels}
        self._pick = mo.ui.dropdown(options=options, label=label, full_width=True)
        self._workspace_id = chosen.public_id

    @property
    def workspace_id(self) -> str:
        if self._pick is None:
            return self._workspace_id
        v = self._pick.value
        return v if v else self._workspace_id

    @property
    def client(self) -> HotdataClient:
        return HotdataClient(
            self._api_key,
            self.workspace_id,
            host=self._host,
            session_id=self._session_id,
        )

    @property
    def ui(self):
        if self._pick is None:
            return mo.md(f"**Workspace** `{self.workspace_id}`")
        _ = self._pick.value
        return mo.vstack([self._pick], gap=1)


def workspace_selector_from_env(*, label: str = "Workspace") -> WorkspaceSelector:
    api_key = default_api_key()
    if not api_key:
        raise RuntimeError("HOTDATA_API_KEY or HOTDATA_TOKEN must be set.")
    host = default_host()
    session = default_session_id()
    return WorkspaceSelector(
        api_key=api_key,
        host=host,
        session_id=session,
        label=label,
    )
