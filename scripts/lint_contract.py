import sys
from genvm_linter import GenVMLinter

linter = GenVMLinter()
target = sys.argv[1] if len(sys.argv) > 1 else "contracts/gen_state.py"
res = linter.lint_file(target)
print("Validation result:", res)
if hasattr(res, "errors") and res.errors:
    print("Errors found:")
    for err in res.errors:
        print(f" - {err}")
    sys.exit(1)
else:
    print("Zero errors! Lint passed successfully.")
