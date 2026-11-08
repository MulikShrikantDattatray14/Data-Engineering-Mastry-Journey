# Errors, Exceptions and Reliable Python Programs

## 1. Three categories of programming problems
**Syntax errors** occur when Python cannot parse valid grammar or indentation. **Runtime failures** happen during execution (often as exceptions). **Logical errors** silently produce wrong results despite runnable syntax.

```python
# Runtime failure that can be handled:
try:
    item = [10, 20][8]
except IndexError:
    print('Invalid position')
```
A wrong business calculation can be more dangerous than an exception because it may load incorrect warehouse metrics. Tests catch both categories.

## 2. try and except
```python
raw = 'unavailable'
try:
    count = int(raw)
except ValueError as exc:
    print('Could not parse count:', exc)
```
Catch **specific** exceptions you understand. Avoid a bare `except:` in routine data pipeline code because it also catches signals such as `KeyboardInterrupt` and `SystemExit`.

## 3. Custom exceptions and raising errors
```python
class DataValidationError(Exception):
    pass

def validate_amount(amount):
    if amount < 0:
        raise DataValidationError('amount must be nonnegative')
    return amount
```
A custom exception communicates a domain-specific failure. The `raise` statement triggers an exception intentionally when data violates an invariant.

## 4. Multiple exception types
```python
def parse_ratio(text):
    try:
        numerator, denominator = text.split('/')
        return int(numerator) / int(denominator)
    except (ValueError, ZeroDivisionError) as exc:
        return f'Invalid ratio: {type(exc).__name__}'
```
You can use separate `except` branches when different failures need different recovery strategies, or a tuple of exception types when the response is identical.

## 5. else and finally
```python
try:
    value = int('12')
except ValueError:
    print('Bad input')
else:
    print('Successfully parsed', value)
finally:
    print('Validation attempt finished')
```
`else` runs when the `try` suite completes without raising an exception. `finally` is intended for cleanup and ordinarily executes during normal exit, exception propagation, or return. It is not an absolute guarantee under abrupt process termination. Prefer `with` context managers for file closure where suitable.

## 6. BaseException hierarchy
At the top is `BaseException`. Typical application failures descend from `Exception`, while `SystemExit`, `KeyboardInterrupt` and `GeneratorExit` are direct special branches under `BaseException`. Usually catch `Exception` or narrower types rather than `BaseException`.

## 7. Important advanced connections
The screenshot assignment set includes topics beyond the lecture's introductory notes. We'll explicitly learn them before attempting the corresponding MCQs: **nested try/finally, chained exceptions (`raise ... from ...` and `__cause__`), exception propagation between functions, contextlib.ExitStack, and exceptions in async coroutines**.

These advanced topics will be expanded with practical examples during the relevant PNP and Bosscoder study sessions. They are not claimed as covered by the original class-notes lecture.

## 8. Data Engineering example
An ETL pipeline should reject malformed records with a clear error, optionally quarantine them with metadata, and avoid silently reporting successful loads when critical data was dropped. Logging useful context while keeping sensitive values out of error messages improves incident response.

## Practice checklist
- [ ] Classify syntax, runtime and logical errors.
- [ ] Demonstrate a failed integer conversion and a failed indexed lookup.
- [ ] Catch two different exception types separately.
- [ ] Define and raise a custom domain error.
- [ ] Explain when `else` and `finally` run.
- [ ] Draw the exception hierarchy and explain why catching `BaseException` is often inappropriate.
- [ ] Compare nested handling and propagation to the caller.
- [ ] Review additional async/ExitStack/exception-chain topics before graded questions.

**Status:** Notes created; no graded answers provided.