# Classes, Objects, Attributes and Methods

## 1. Why object-oriented Python?
OOP organizes state and behavior together. A **class** defines attributes and operations; an **instance** is a concrete object of that class. This can make reusable extractors, pipeline configurations and validators easier to manage, though not all code needs classes.

```python
class FileBatch:
    file_type = "csv"                         # class attribute

    def __init__(self, filename, record_count):
        self.filename = filename              # instance attribute
        self.record_count = record_count

    def describe(self):                       # instance method
        return f"{self.filename}: {self.record_count} rows"

batch = FileBatch("orders.csv", 250)
print(batch.describe())
```

Compared with JavaScript classes, Python uses `self` explicitly in instance method definitions; `__init__` initializes an already created instance rather than being the whole object creation mechanism.

## 2. Class and instance attributes
An instance can have its own attribute values while the class holds default or shared attributes. Attribute lookup normally checks the instance before an ordinary class attribute. A value stored on the instance can shadow a class attribute.

```python
class Job:
    environment = "test"

    def __init__(self, name):
        self.name = name

job = Job("daily-load")
print(job.name, job.environment)
```

**Trap:** class-level mutable collections may be shared across instances. Decide deliberately whether state should be global to all instances or owned by each instance.

## 3. The three common method forms
| Kind | First implicit argument | Typical purpose |
|---|---|---|
| Instance method | `self` | Access/change instance state |
| Class method (`@classmethod`) | `cls` | Access class state; alternate constructors |
| Static method (`@staticmethod`) | None | Utility operation in class namespace |

```python
class Dataset:
    schema_version = 1

    def __init__(self, name):
        self.name = name

    def summary(self):
        return self.name

    @classmethod
    def current_schema(cls):
        return cls.schema_version

    @staticmethod
    def normalize_name(value):
        return value.strip().lower()

print(Dataset.current_schema())
print(Dataset.normalize_name(" SALES "))
```

Static methods can generally be accessed through class or instance. An ordinary instance method requires a suitable instance when called through the class.

## 4. Constructors and attribute presence
`__init__` is commonly used to assign per-instance values. Assigning attributes after construction is possible when a class allows a normal instance dictionary.

```python
class Source:
    def __init__(self, url):
        self.url = url

source = Source("memory://sample")
print(hasattr(source, "url"))
```

`hasattr` checks whether attribute lookup succeeds (not simply whether a spelling appears in an instance's own dictionary).

## 5. Attribute shadowing and methods
Python functions stored on a class can bind to instances on access. Assigning a same-named instance attribute can shadow a normal class method on that instance. The class's method remains separately defined.

## Active recall
- [ ] Explain the class/instance distinction and why data attributes live on one or the other.
- [ ] Contrast class, instance and static methods with examples.
- [ ] Explain how attribute lookup can affect a class attribute, an instance attribute and method access.
- [ ] Describe a shared mutable class-attribute bug in a data-processing job.
- [ ] Explain when to use a class rather than a simple function.

**Status:** No Bosscoder MCQ answers provided; practice pending.
