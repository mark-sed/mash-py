/**
Parser testing
All of the code bellow is SYNTACTICALLY valid (for the parser), but might not be semantically valid
*/

import a; import b

a

b = 42;
c = 4.45e-9

# Consts
0xF
0xaa848FdC
"Unicode 🍣"
42
f"Format string {b}"

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

fun bar(a = 4.5, b = .5) {
    return fun(a, b) = a
}



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
    arg1; arg2 = true
    A() {

    }
}

space {
    class A : b {
        A() {

        }

        fun nn(a = 4) = 8

        class A2 {
            b
            c = nil

            space N {
                import t
                a = 85
                a  # This is SYNTACTICALLY correct, but semantically its is a redefinition 
                b

                fun a() {
                    import C
                    return nil
                }
            }
        }
    }
}

fun f(a=fun()=4) = 4

fun(a=fun(b)=b*4) = a(5)

a(4, b)[(54+4+a)^4]()

# Internal implementation of a variable
some_const = # [! internal !]

someObj.a::f = f(a = 42) ? fun(a)=42*a : nil

a = [x*y : x = 1..a, y = f(4)]
