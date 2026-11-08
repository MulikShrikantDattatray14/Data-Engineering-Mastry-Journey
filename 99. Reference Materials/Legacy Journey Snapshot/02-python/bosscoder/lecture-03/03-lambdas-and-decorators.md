# Part 3 — Lambda Functions and Decorators

## 1. Lambda expressions
A lambda creates a small function from one expression. Syntax: lambda parameters: expression. It can take multiple parameters, but its body is a single expression rather than a statement block.
```python
by_amount = lambda record: record['amount']
orders = [{'amount': 200}, {'amount': 50}]
print(sorted(orders, key=by_amount))

choose_label = lambda amount: 'high' if amount > 100 else 'low'
print(choose_label(150))
```

Compared with def, lambda is concise but less suitable for multi-step logic, meaningful documentation or reuse. You already know arrow functions in JavaScript; the idea of passing functions is similar, but Python lambda syntax is more restricted.

## 2. Lambda late binding in loops
```python
late = [lambda: i for i in range(3)]
print([f() for f in late])                 # late binding

captured = [lambda i=i: i for i in range(3)]
print([f() for f in captured])             # capture at creation
```

The class notebook uses default arguments in a list of lambdas. Understand **why** defaults capture the value; don't memorize the output alone.

## 3. Lecture use cases
- Data transformation and cleaning using map/apply-like functions
- Filtering rows by predicates
- Deriving features from fields
- Sorting by chosen key
- Small aggregations (sometimes sum/max or a named function is clearer)

## 4. What is a decorator?
A decorator takes a callable and returns another callable, typically wrapping behavior such as timing, access checks, retries or logging without rewriting every function's core logic.

```python
from functools import wraps

def announce(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('Beginning transformation')
        result = func(*args, **kwargs)
        print('Transformation complete')
        return result
    return wrapper

@announce
def normalize(value):
    return value.strip().lower()

print(normalize('  PAID '))
```

@announce is shorthand for normalize = announce(normalize). functools.wraps helps preserve metadata such as the original function name and docstring. Logging/printing in the wrapper makes the **decorated callable impure** even if the wrapped calculation itself is pure.

## 5. Decorator factory with arguments
```python
from functools import wraps

def repeat(times):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorate

@repeat(2)
def label(value):
    return value.upper()

print(label('ok'))
```

Distinguish a decorator (which accepts a function) from a decorator factory (which first accepts configuration and then returns a decorator). This is a generic example, not an academy assignment solution.

## 6. Built-in decorators
### @staticmethod
Treats a function in a class namespace like a regular function without implicit self or cls.
```python
class SchemaHelper:
    @staticmethod
    def normalize_key(key):
        return key.strip().lower()
```

### @classmethod
Receives the class (usually cls); commonly used for alternate constructors and class-wide behavior.
```python
class Batch:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_name(cls, text):
        return cls(text.strip())
```

### @property and setters
Expose a method as attribute-like access; optionally validate assignments.
```python
class Record:
    def __init__(self, score):
        self.score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if value < 0:
            raise ValueError('score must be non-negative')
        self._score = value
```

## Review questions
- [ ] Contrast def and lambda; show an if/else expression.
- [ ] Explain lambda capturing in loop comprehensions.
- [ ] Implement a wrapper preserving arguments, results and function metadata.
- [ ] Explain decorator factory call order.
- [ ] Demonstrate @staticmethod, @classmethod, @property and a validated setter.
- [ ] Explain why decorators are useful for ETL instrumentation and where side effects enter.

**Status:** Examples are original; learner exercises and Bosscoder graded assignments pending.