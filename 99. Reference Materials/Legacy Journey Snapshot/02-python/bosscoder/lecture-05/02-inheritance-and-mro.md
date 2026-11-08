# Inheritance, `super()`, Overriding and Method Resolution

## 1. Parent and child classes
A subclass may inherit attributes and methods from a base class and override selected behavior. Use inheritance for a genuine *is-a* relationship, not merely to avoid copying code.

```python
class Loader:
    def load(self, rows):
        return len(rows)

class ValidatingLoader(Loader):
    def load(self, rows):
        checked = [row for row in rows if row is not None]
        return super().load(checked)
```

`super()` follows the method resolution order (MRO), not always the simplistic idea of directly calling one named parent. It is especially important in cooperative multiple inheritance.

## 2. All five inheritance forms named in the lecture
- **Single:** one child inherits from one parent.
- **Multiple:** one child inherits from more than one base.
- **Multilevel:** chains such as grandparent → parent → child.
- **Hierarchical:** siblings share a common base.
- **Hybrid:** more than one of the above structures together.

Draw each structure and explain how overrides are chosen.

## 3. Overriding versus initializers
If a subclass defines its own `__init__`, Python does not automatically invoke the parent initializer in the ordinary case. You often call `super().__init__(...)` when shared base-class initialization is required.

```python
class Task:
    def __init__(self, task_id):
        self.task_id = task_id

class ScheduledTask(Task):
    def __init__(self, task_id, interval):
        super().__init__(task_id)
        self.interval = interval
```

A subclass overriding a normal method can choose a different implementation, optionally delegate to `super()`, and retain the same external interface.

## 4. Method resolution order (MRO)
Python uses a consistent linearization (C3) to determine method search order in multiple inheritance. Inspect `SomeClass.__mro__` or `SomeClass.mro()`.

```python
class Origin: pass
class FromApi(Origin): pass
class FromFile(Origin): pass
class Combined(FromApi, FromFile): pass

print([cls.__name__ for cls in Combined.__mro__])
```

Why important? In multiple inheritance, changing base-class order may change which override runs. Inconsistent hierarchies can be rejected when Python cannot construct a valid MRO.

## 5. Cooperative `super`
A call such as `super(CurrentClass, instance)` starts lookup **after** that class in the instance's MRO, subject to the bound instance/type relationship. It is not shorthand for invoking any arbitrarily selected parent.

## Practice
- [ ] Implement and draw single, multiple, multilevel, hierarchical and hybrid inheritance.
- [ ] Override one method and compare parent/child calls.
- [ ] Initialize a subclass with and without a deliberate super call; inspect which attributes exist.
- [ ] Predict `__mro__` for a simple diamond and verify by running Python.
- [ ] Explain why cooperative `super` matters when mixing multiple parent classes.

**Status:** Lecture concepts documented; assignments unsolved.
