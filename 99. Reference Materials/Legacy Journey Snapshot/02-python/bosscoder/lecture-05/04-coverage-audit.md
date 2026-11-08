# Lecture 5 — Exhaustive No-Skip Coverage Audit

**Source:** Supplied Bosscoder OOP lecture and 12 MCQ screenshots. **Documentation mapped; mastery not yet verified.** Every checkbox requires later independent practice.

## Foundations and classes
- [ ] Explain OOP purpose, organization, reusability, flexibility and maintainability
- [ ] Class definition vs object instance; creation and instance-specific state
- [ ] Class-level vs instance-level attributes and name lookup
- [ ] `__init__`, `self`, instance creation, class/method namespace
- [ ] Instance methods, class methods (`@classmethod`) and static methods (`@staticmethod`)
- [ ] Recreate the lecture's Dog and Car class-object demonstrations independently

## Inheritance
- [ ] Parent/child roles; single inheritance
- [ ] Multiple inheritance
- [ ] Multilevel inheritance
- [ ] Hierarchical inheritance
- [ ] Hybrid inheritance
- [ ] Child initializer and deliberate base initialization with `super().__init__`
- [ ] `super()` method delegation and MRO semantics
- [ ] Method overriding; inherited method versus replaced method
- [ ] Draw and code independent variations of the lecture's hierarchy examples

## Encapsulation
- [ ] Public names, default accessibility
- [ ] Protected-style underscore convention
- [ ] Double-underscore names and Python name mangling
- [ ] Explicit getters
- [ ] Explicit setters and validation
- [ ] Internal/private-style methods
- [ ] Explain that Python mangling is not a security/access-control barrier

## Polymorphism
- [ ] Definition and how one interface serves different object types
- [ ] Runtime overriding in inheritance
- [ ] Optional/default arguments used in place of traditional overload signatures
- [ ] Duck typing and behavioral compatibility without a common base
- [ ] Operator overloading through `__add__` and display through `__str__`
- [ ] Same-named methods on unrelated classes
- [ ] Polymorphism through common base classes; unimplemented methods and failure behavior
- [ ] Recreate Shape, Animal and Vector-style demonstrations independently

## Abstraction
- [ ] Abstraction vs encapsulation
- [ ] `abc.ABC` and `@abstractmethod`
- [ ] Required implementations by concrete subclasses
- [ ] Interface/contract thinking and instantiation restrictions
- [ ] Benefits: simplified interface, reuse, maintainability
- [ ] Limitations: overhead, design complexity, over-abstraction
- [ ] Recreate the lecture's vehicle-style abstract class example independently

## MCQ extensions from the supplied 12 screenshots
- [ ] Class variable vs instance shadowing
- [ ] Mangled double-underscore attribute and `hasattr`
- [ ] Instance attribute shadowing a class method (two screenshot variants)
- [ ] Static methods vs instance methods called through class/instance
- [ ] Abstract class with unimplemented abstract method
- [ ] Overriding with subclass polymorphism
- [ ] Diamond inheritance and search order
- [ ] Multiple-inheritance `__mro__`
- [ ] Subclass `__init__` overriding parent's initializer
- [ ] Mutable class attribute shared between instances
- [ ] Explicit `super(Class, instance)` method lookup

## Source accuracy notes
- Class-level attributes and instance-level attributes are different; mutable class attributes may be shared.
- A Python `_name` is a convention and `__name` is mangled, not strictly private.
- Python does not offer traditional compile-time method overloading simply by redefining the same method.
- Calling `super()` follows MRO and may not be equivalent to naming a direct parent.
- An instance that assigns an attribute with a method's name may shadow the bound method; keep this distinct from redefining the class itself.

## Cross-source study workflow
1. Learn the PNP Python core concept once using the matching OOP/decorators lessons.
2. Use this audit to fill all Bosscoder subtopics without repeating already mastered explanations.
3. Attempt relevant academy MCQs **independently in Python**.
4. Review after the student gives their selected answer and reasoning.
5. Track individual assignment completion separately from curriculum concept mastery and attendance.

**No checkboxes are marked complete by creating these notes.**
