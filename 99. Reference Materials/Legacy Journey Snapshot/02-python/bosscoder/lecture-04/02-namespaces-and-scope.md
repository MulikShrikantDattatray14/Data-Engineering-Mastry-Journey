# Python Namespaces and Scope — LEGB

## 1. Namespaces versus scope
A namespace is a mapping from names to objects, such as a module's global namespace or a function's local namespace. A scope is the region of code in which a name can be resolved. They are related but not identical concepts.

Python commonly searches unqualified names using **LEGB**: Local → Enclosing → Global → Built-ins.

## 2. The four primary lookup levels
| Level | Where it comes from | Example |
|---|---|---|
| Local (L) | Current function | `row_id` inside `parse` |
| Enclosing (E) | Outer function around a nested function | `separator` captured in closure |
| Global (G) | Module namespace | `DEFAULT_REGION` |
| Built-ins (B) | Standard built-in names | `len`, `print` |

```python
region = 'global'

def outer():
    region = 'enclosing'
    def inner():
        region = 'local'
        return region
    return inner(), region

print(outer(), region)
```
Each `region` is a separate binding, so a nested local assignment does not automatically overwrite the outer or module-level name.

## 3. Global and nonlocal rebinding
Use `global` when deliberately **rebinding** a module-level name. Use `nonlocal` when rebinding a name from a function's enclosing non-global scope.

```python
def make_counter():
    count = 0
    def tick():
        nonlocal count
        count += 1
        return count
    return tick

counter = make_counter()
print(counter(), counter())
```
Reading a global doesn't usually require a `global` declaration. Avoid hidden shared mutation where possible; explicit state passed into pure transformations simplifies pipeline testing.

## 4. Shadowing and gotchas
```python
len = 99
# len([1, 2]) would fail while this name shadows the built-in.
del len
print(len([1, 2]))
```
Assignment in a function generally makes a name local throughout that function unless `global` or `nonlocal` applies. This may produce `UnboundLocalError` if the name is read before local assignment.

## 5. Data Engineering connection
When separate ETL jobs share a global mutable list of rejected rows, tests can accidentally influence each other. Returning transformation results explicitly is safer and makes replay/checkpoint behavior easier to reason about.

## Classroom examples to recreate
- [ ] Define a local name and check that it isn't accessible outside its function.
- [ ] Access a value from an enclosing function.
- [ ] Read a module-level value.
- [ ] Call a built-in name and explain its namespace.
- [ ] Use `nonlocal` to update an enclosing variable.
- [ ] Recreate LEGB example with three shadowed names and predict output.
- [ ] Explain the difference between a namespace and the `nonlocal` keyword (there isn't a separate fifth LEGB lookup tier).

**Status:** Concepts mapped, not yet mastered.