/**
Parser testing
All of the code bellow is SYNTACTICALLY valid (for the parser), but might not be semantically valid
*/

import a; import b

a

b = 42;

fun (a, b) = 4
fun (a = 4, b = 5) = a
fun () = 4
fun (a, z, b = 42, c = 44) = a

fun foo(a, z, b = 42, c = 44) = a(b, 8)

fun foo(a, b, c = 4) {
    a
    return
}

fun foo() {
    return 4
}

fun foo() {
    fun bar() {
        return 4
    }
    return
}

fun bar(a = 4, b = 5) {
    return fun(a, b) = a
}

"Unicode 🍣"
42

fun a(a) {
    A = 5
    return 42
}

# Import can be also in the code further bellow and in functions
import b;
fun a() {
    import c
    return hae(4)
}

f(4, a, c())

class MyClass {
    # empty class
}

/**
 * class with internal implementation
 */
class InternalClass {
    # [!internal!]
}

class A : B, C {
    arg1; arg2
    A() {

    }
}

space {
    class A : b {
        A() {

        }

        fun nn(a = 4) = 8

        class A2 {
            a
            b = 5
        }
    }
}