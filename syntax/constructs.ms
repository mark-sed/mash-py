/*
Showcase of basic programming constructs.
*/

# Block of code can be placed within curly braces
{ 
    txt = "some text" 
    out.println(txt)
}
out.println(txt) # Throws an error, since txt is out of scope

# If statements
a = true
b = false

if (a == b || b == false) {
    out.println("matched 1st if.")
} elif (a = true) {
    out.println("matched 2nd if.")
} else {
    out.println("fell in else.")
}