# Modules, Imports and Packages

## 1. What is a module?
A module is usually a Python file containing reusable declarations such as functions, constants and classes. Importing lets another Python file access them. Python also has built-in, extension and standard-library modules; not every module is a plain `.py` file.

**Why Data Engineers care:** ETL code becomes much easier to test when extraction, transformation, configuration and loading logic live in separate modules instead of one giant notebook.

## 2. Create and import a custom module
Example folder:
```text
demo/
  metrics.py
  main.py
```
`metrics.py`:
```python
RATE = 0.18

def add_tax(amount):
    return amount * (1 + RATE)
```
`main.py`:
```python
import metrics

print(metrics.add_tax(200))
print(metrics.RATE)
```
Importing a module binds its name; `from metrics import add_tax` imports a particular name into the current namespace. Avoid wildcard imports because collisions and dependencies become difficult to discover.

## 3. Packages and `__init__.py`
A conventional Python package groups related modules in a directory. An `__init__.py` file may define package-level initialization or re-exports. Python also supports namespace packages **without** `__init__.py`, so the note that every package must have it is too absolute.

```text
warehouse/
  __init__.py
  cleaning.py
  validation.py
run.py
```
Possible use: `from warehouse.cleaning import normalize_status`. Keep side effects out of imports whenever practical.

## 4. Run script versus import: the main guard
The special variable is `__name__` (double underscores). Python sets it to `'__main__'` when a file is run directly, but normally uses the module's qualified name when imported.

```python
def show_report():
    return 'Report generated'

if __name__ == '__main__':
    print(show_report())
```
This prevents demonstration or command-line work from running automatically when the module is imported for testing. It is not written `if name == 'main'`.

## 5. Standard library modules from this lecture
| Module | Typical purpose |
|---|---|
| `os` | Operating system details, environment variables and paths |
| `sys` | Runtime arguments, interpreter settings and exit behavior |
| `math` | Mathematical functions |
| `random` | Pseudorandom values |
| `time` | Time measurement and sleep operations |
| `datetime` | Dates, timestamps and time zones |
| `json` | JSON serialization/parsing |
| `pickle` | Python object serialization (never load untrusted pickles) |
| `re` | Regular expression matching |
| `csv` | CSV reading and writing |
| `collections` | `Counter`, `defaultdict`, `namedtuple`, etc. |

```python
import json
from collections import Counter

statuses = ['paid', 'pending', 'paid']
print(Counter(statuses))
print(json.dumps({'rows': len(statuses)}))
```

## 6. Why modularity matters
Modules help reuse code, separate responsibilities, prevent name collisions through namespaces and clarify dependencies. Imports are not a replacement for environment and dependency management.

## Try it yourself
- [ ] Make a two-file mini-project and import a function/constant.
- [ ] Explain `import module` versus `from module import name`.
- [ ] Create a package with `__init__.py` and call a function from a sibling module.
- [ ] Run a module directly and import it; compare behavior with a main guard.
- [ ] Give a real Data Engineering use for each listed standard-library module.
- [ ] Explain why loading untrusted `pickle` files is risky.

**Status:** Notes ready, hands-on mastery pending.