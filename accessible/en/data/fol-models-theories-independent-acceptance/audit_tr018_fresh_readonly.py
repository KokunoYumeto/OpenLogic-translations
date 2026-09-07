#!/usr/bin/env python3
"""Fresh read-only execution of the frozen independent TR-018 audit.

The complete audit implementation is itself preserved in the immediately
preceding independent zero-finding evidence generation.  This launcher binds
that program to a new evidence-only write root; every prior audit generation,
including every FAIL, remains a protected input.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPECTED_DIRECTORY = "final_fresh_readonly_reaudit_20260821"
PROGRAM = (
    HERE.parent
    / "fresh_operand_order_zero_finding_reaudit_20260820"
    / "audit_tr018_final_operand_order.py"
)


def main() -> int:
    if HERE.name != EXPECTED_DIRECTORY:
        raise RuntimeError(f"audit write root drift: {HERE}")
    spec = importlib.util.spec_from_file_location(
        "tr018_frozen_final_operand_audit", PROGRAM
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen TR-018 audit program")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)

    # Rebind every helper's evidence-local write root. The protected-input
    # enumerator consequently excludes only this new generation and includes
    # every earlier independent PASS and FAIL byte as a read-only boundary.
    audit.HERE = HERE
    audit.F.HERE = HERE
    audit.B.HERE = HERE
    audit.B.INITIAL = audit.AUDIT_ROOT

    original_require = audit.require

    def require(condition: bool, detail: str) -> None:
        if detail == "audit write root drift":
            original_require(HERE.name == EXPECTED_DIRECTORY, detail)
        else:
            original_require(condition, detail)

    audit.require = require
    return audit.main()


if __name__ == "__main__":
    raise SystemExit(main())
