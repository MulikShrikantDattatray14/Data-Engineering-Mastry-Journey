# PDF cross-check — Lecture 05: Object-Oriented Programming

**Source:** Learner-supplied `OOPs - Colab.pdf` (20 PDF pages, reviewed 2026-11-06).
**Result:** All principal PDF topic groups have matching independent public chapters. Specific source cautions and tracker corrections are below. **Student mastery and assignments remain pending.**

## PDF page-to-GitHub comparison

| PDF pages | Source subject area | Existing learning chapter |
|---|---|---|
| 1–4 | OOP motivation, class/object distinction, attributes, instance/class/static methods | [Chapter](01-classes-objects-methods.md) |
| 4–9 | single, multiple, multilevel, hierarchical and hybrid inheritance, parent initializers, super, overriding | [Chapter](02-inheritance-and-mro.md) |
| 9–13 | encapsulation, public/single/double underscore names, getters, setters, name mangling | [Chapter](03-encapsulation-polymorphism-abstraction.md) |
| 14–18 | compile-time vs runtime terminology, default-argument simulation, duck typing, operator overloading, inheritance polymorphism | [Chapter](03-encapsulation-polymorphism-abstraction.md) |
| 18–20 | ABC, abstractmethod, interfaces, concrete implementations and advantages/limitations | [Chapter](03-encapsulation-polymorphism-abstraction.md) |

## Cautions and mismatches confirmed during PDF verification
- The notebook uses 'private/protected access modifiers' as explanatory analogies; Python single underscore is a convention and double underscore triggers name mangling, not access security.
- A later example calls an ordinary instance method a 'class method' in prose; distinguish `@classmethod` from a method defined inside a class.
- The graded MCQs add MRO diamond and mutable-class-attribute traps beyond the beginner PDF; included in the assessment checklist.

## Changes or additional review requirements
- All five inheritance shapes and abstraction tradeoffs verified against PDF.

## Not an assignment submission

- [ ] Learner reviews every source-aligned topic and independently reruns relevant Python exercises.
- [ ] Learner completes the corresponding Bosscoder graded assignments later.
- [ ] We verify first attempts, pitfalls and edge cases before checking mastery boxes.

**No graded assignment solutions or MCQ answer keys supplied in this audit.**
