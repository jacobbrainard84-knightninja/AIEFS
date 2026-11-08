"""Project chronicler: keep AIEFS memory, instruction and introduction documents true.

Entry points
------------
``python -m chronicler status``
    Human digest: which documents exist, how old their own stamps are, what is
    queued.
``python -m chronicler check --fail-on high``
    Deterministic drift rules. Exit code 1 when something at or above the
    threshold is found, so it can gate a commit.
``python -m chronicler tick``
    One self-directed cycle: refresh facts, reconcile the durable queue, choose
    the single next action, and write ``loop/NEXT.md``.

Read ``PROJECT_CHRONICLER_AGENT.md`` at the repository root for the agent
charter that uses these commands.
"""

from . import checks, cli, docs, facts, loop, util  # noqa: F401

__all__ = ["checks", "cli", "docs", "facts", "loop", "util"]
__version__ = "0.1.0"
