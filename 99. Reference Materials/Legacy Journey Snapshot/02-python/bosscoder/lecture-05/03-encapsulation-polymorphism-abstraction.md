# Encapsulation, Polymorphism and Data Abstraction

## 1. Encapsulation
Encapsulation groups state and behavior and gives clients a deliberate interface. Python **does not have enforced Java-like public/protected/private access modifiers**:
- `name` is conventionally public.
- `_name` signals internal/protected-by-convention usage, but is accessible.
- `__name` triggers **name mangling** in class definitions, primarily to avoid accidental subclass clashes; it is *not* absolute privacy.

```python
class Configuration:
    def __init__(self, retry_limit):
        self._retry_limit = retry_limit

    @property
    def retry_limit(self):
        return self._retry_limit

    @retry_limit.setter
    def retry_limit(self, value):
        if value < 0:
            raise ValueError("retry limit must be nonnegative")
        self._retry_limit = value
```

Explicit get/set methods are another interface option; `@property` is idiomatic when attribute-like access is helpful. The lecture also demonstrates accessing mangled names, which should not be confused with a security barrier.

## 2. Polymorphism
One interface can work with multiple types of objects. **Overriding** specializes inherited methods at runtime. **Duck typing** relies on supported behavior rather than requiring a shared parent.

```python
class ApiInput:
    def read(self):
        return ["api-row"]

class FileInput:
    def read(self):
        return ["file-row"]

def inspect_source(source):
    return len(source.read())

print(inspect_source(ApiInput()), inspect_source(FileInput()))
```

### The various forms from the lecture
- **Default-argument flexibility:** emulate some method-overloading behavior by optional arguments. Defining the same method twice with different signatures does **not** create Java/C++ style overloads.
- **Operator overloading:** special methods such as `__add__` and `__str__` customize supported operators/printing.
- **Methods on different objects:** distinct types expose the same method name but do different things.
- **Polymorphism through inheritance:** common base class plus specialized implementations.

```python
class RowCount:
    def __init__(self, count):
        self.count = count

    def __add__(self, other):
        return RowCount(self.count + other.count)

    def __str__(self):
        return f"{self.count} records"

print(RowCount(4) + RowCount(6))
```

## 3. Abstraction
Abstraction exposes essential operations while hiding implementation decisions. Python's `abc` module provides abstract base classes and `@abstractmethod` markers.

```python
from abc import ABC, abstractmethod

class Reader(ABC):
    @abstractmethod
    def read(self):
        """Return source records."""

class MemoryReader(Reader):
    def read(self):
        return [{"id": 1}]

print(MemoryReader().read())
```

An abstract subclass that has not provided required concrete implementations cannot normally be instantiated. Interface-like behavior can also be modeled with duck typing or protocols in other lessons.

### Benefits and limitations
Abstraction can simplify the caller's mental model, improve reuse and organize large projects. Over-abstraction adds indirection, requires design effort, and may introduce some overhead. Use the simplest interface that fits your Data Engineering system.

## Practice
- [ ] Demonstrate public, underscore and double-underscore naming conventions.
- [ ] Explain name mangling, getters/setters and `@property`.
- [ ] Implement duck typing without a common base class.
- [ ] Demonstrate inherited method overriding and optional-parameter flexibility.
- [ ] Define a basic custom operator through a special method.
- [ ] Build one ABC and two concrete implementations; identify what cannot be instantiated.
- [ ] Explain trade-offs of abstraction in an ETL connector design.

**Status:** Notes documented; no assignment completed.
