# Mash language
Dynamically typed language for easy prototyping and working with the operating system and files.

## Syntax
Examples of the code can be seen in the `syntax` folder.

Mash code is constructed from expressions, where each expression ends with a semicolon or a new line.

### Operators
| **Operator**                     | **Description**                                  | **Associativity** |
|----------------------------------|--------------------------------------------------|---------------|
| `()`                             | Function call                                    | Left          |
| `[]`                             | List Selection                                   | Left          |
| `.`                              | Element selection                                | Left          |
| `++`, `--`                       | Increment, Decrement (postifx)                   | Left          |
| `+`, `-`                         | Unary + and -                                    | Right         |
| `^`                              | Exponentiation                                   | Right         |
| `*`, `/`, `//`, `%`              | Multiplication, Division, Floor division, Modulo | Left          |
| `+`, `-`                         | Addition, Subtraction                            | Left          |
| `..`                             | List range constructor                           | Left          |
| `in`                             | Membership                                       | Left          |
| `<=`, `>=`, `>`, `<`             | Comparisons                                      | Left          |
| `==`, `!=`                       | Equals, Not equals                               | Left          |
| `&&`                             | Logical and                                      | Left          |
| `!`                              | Logical not                                      | Right         |
| `&&`                             | Logical and                                      | Left          |
| `\|\|`                           | Logical or                                       | Left          |
| `?:`                             | Ternary if                                       | Right         |
| `=`, `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `^=` | Assignment, Operation and assignment | Right       |

### Keywords
| **Keyword**          | **Description**     |
|----------------------|---------------------|
| `if`, `elif`, `else` | If statement        |
| `break`, `continue`  | Flow controls       |
| `do`, `while`, `for` | Loops               |
| `import`             | Module import       |
| `return`             | Function return     |
| `nil`                | No value type       |
| `true`, `false`      | Boolean values      |
| `fun`                | Function            |
| `class`              | Class               |
| `assert`             | Debugging assertion |

### Types and values
* `42`, `0x2A`, `0x2a` - Positive integers
* `-42`, `-0xFfa` - Negative integers
* `10_000` - Integer with formatting (10000)
* `3.14159`, `.001`, `3e-8`, `0.33E+8` - Floats
* `true`, `false` - Booleans
* `nil` - No value
* `"text"`, `f"text {foo}"`, `r"new line: \n"` - String
