# mash-py
Python 3 interpreter for Mash language

# Mash language
Dynamically typed language (with some optional typing features) for easy prototyping, writing one liners, but also
bigger size scripts and programs.

Mash aims to be consistent and friendly to begginers, but at the same time allow for some higher lever techniques. 

## Syntax
Examples of mash the code can be seen in the `examples` folder.

In Mash semicolons work just like new lines and vice versa, meaning that when you're writing one liners, you
can replace new lines with semicolons and in case of writing multiline code, you can omit semicolons. 

Mash uses brackets (`{` and `}`) for code structuring and not indentations.

Mash has support for object oriented programming (OOP) and offers namespaces as well for the ease of code organization.

Even though Mash is dynamically typed language, implicit conversions are quite strict to help quickly discover
incorrect code and to help with the readability of the code. 

### Operators
| **Operator**                     | **Description**                                  | **Associativity** |
|----------------------------------|--------------------------------------------------|---------------|
| `::`                             | Scope resolution (class or space element selection) | Left       |
| `()`                             | Function call                                    | Left          |
| `[]`                             | List Selection                                   | Left          |
| `.`                              | Objecy element selection                         | Left          |
| `+`, `-`                         | Unary + and -                                    | Right         |
| `^`                              | Exponentiation                                   | Right         |
| `*`, `/`, `//`, `%`              | Multiplication, Division, Floor division, Modulo | Left          |
| `+`, `-`                         | Addition, Subtraction                            | Left          |
| `++`                             | Concatenation                                    | Left          |
| `..`                             | List range constructor                           | Left          |
| `in`                             | Membership                                       | Left          |
| `<=`, `>=`, `>`, `<`             | Comparisons                                      | Left          |
| `==`, `!=`                       | Equals, Not equals                               | Left          |
| `!`, `not`                       | Logical not                                      | Right         |
| `&&`, `and`                      | Logical and                                      | Left          |
| `\|\|`, `or`                     | Logical or                                       | Left          |
| `?:`                             | Ternary if                                       | Right         |
| `=`, `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `^=`, `++=` | Assignment, Operation and assignment | Right       |
| `~`                              | Silence operator                                 | Right         |

### Keywords
| **Keyword**          | **Description**     |
|----------------------|---------------------|
| `if`, `elif`, `else` | If statement        |
| `break`, `continue`  | Flow controls       |
| `do`, `while`, `for` | Loops               |
| `import`, `as`       | Module import       |
| `return`             | Function return     |
| `raise`              | Exception generation |
| `try`, `catch`, `finally` | Exception handeling |
| `nil`                | No value type       |
| `true`, `false`      | Boolean values      |
| `fun`                | Function            |
| `class`              | Class               |
| `space`              | Namespace           |
| `internal`           | Internal implementation |

### Types and values
* `42`, `0x2A`, `0x2a` - Positive integers
* `-42`, `-0xFfa` - Negative integers
* `10_000` - Integer with formatting (10000)
* `3.14159`, `.001`, `3e-8`, `0.33E+8` - Floats
* `true`, `false` - Booleans
* `nil` - No value
* `"text"`, `f"text {foo}"`, `r"new line: \n"` - String

### Strings

Escape characters start with `\` can be one of the following:
* `\\` - Backslash (`\`).
* `\"` - Double quote (`"`).
* `\a` - Alarm/Bell character.
* `\b` - Backspace character.
* `\f` - Form feed (new page).
* `\n` - Mew line (line feed).
* `\r` - Carriage return.
* `\t` - Horizontal tab.
* `\v` - Vertical tab.
