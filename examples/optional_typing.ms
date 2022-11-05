fun foo(a:Int, b) { 
    return "Int first\n"
}; 

fun foo(a:String, b) { 
    return "String first\n"
}; 

fun foo(a:Rnd, b) { 
    return a::shuffle(b) 
}; 

fun foo(a, b) {
    return "\nAll other types\n"
}

foo(1, 2)
foo("1", 2)
foo(Rnd, [2,3,4,5])
foo(true, false)

/** Output: */
# first
# redef
# [5, 4, 2, 3]
# all else

