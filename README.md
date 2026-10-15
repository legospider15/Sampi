# **How to code in Sampi**

Sampi is an obsolete Greek letter and symbol for 900.
Sampi is also the name of a high-level programming language.
The symbol for Sampi is ϡ.

## **Installing Sampi**

Download Sampi using the green **Code** button on 
GitHub and select **Download ZIP**. Extract the downloaded folder.
You now have the Sampi editor and source code. You can also go to
[Sampi's website](https://legospider15.github.io/codewithsampi/)
to get a standalone application.

## **Running Sampi**
If you got the standalone application, open it normally. You may need
to tell you computer that it isn't malware. If you downloaded the 
source code, then you will need **Python3**, and **nothing else**.
Open a terminal in the project folder and run:
```text
python3 IDE.py
```
Or run IDE.py in Python.
Once the IDE opens, you can begin experimenting with Sampi.

## **Learning Sampi**
The following instructions wil teach you how to code in
Sampi. For a far more complete and up-to-date tutorial,
go to [Sampi's website's documentation](https://legospider15.github.io/codewithsampi/docs.html)

## **Printing**

To display a value, type:
```text
say("Hello, world!")
```
Output:
```text
Hello, World
```
## **Variables**

To set a variable, do:
```text
set x to 1
```
And to increment it:
```text
set x to x + 1
```
When making a varable in Sampi, **always** use snake_case.
## **Operators**

| Operation | Example | Result |
|---|---|---|
| Addition | `1 + 1` | `2` |
| Subtraction | `3 - 1` | `2` |
| Multiplication | `2 * 4` | `8` |
| Division | `8 / 2` | `4` |

A string plus a number combines them:
```text
say("hello" + 5 + 5)
```
Output:
```text
hello55
```
Sampi does operations from left to right, and doesn't care about PEMDAS:
```text
say(2 + 3 * 4)
```
Output:
```text
20
```
If you want to use PEMDAS, use parentheses:
```text
say(2 + (3 * 4))
```
Output:
```text
14
```
When adding strings and numbers, be careful because:
```text
say(5 + 5 + "hello")
say(5 + (5 + "hello"))
```
Output:
```text
10hello
55hello
```
Sampi also has ways to compare values.

| Comparison | Example | Result |
|---|---|---|
| Equal | `1 = 1` | `true` |
| Greater than | `2 > 1` | `true` |
| Less than | `2 < 3` | `true` |
| Greater than or equal to | `1 >= 1` | `true` |
| Less than or equal to | `1 <= 2` | `true` |
| Not equal | `1 != 2` | `true` |

You can chain together comparisons with:

| Operation | Example | Result |
|---|---|---|
| And | `true and false` | `false` |
| Or | `true or false` | `true` |
| Not | `not true` | `false` |

Sampi uses true and false, not True and False.

## **If Statements**

An if statement takes the form of:
```text
set x to 1
if x = 1:
    say("x is equal to 1!")
end
```
Output:
```text
x is equal to 1!
```
There is also else. if comes first. else comes last, if at all.
```text
set num to 1

if num > 0:
    say("+")
else if num = 0:
    say("0")
else:
    say("-")
end
```
Output:
```text
+
```
## **Loops**
 ```text
repeat 5:
	say("hello")
end
```
Output:
```text
hello
hello
hello
hello
hello
```
If you want the current iteration, do:
```text
repeat 5 as i:
    say(i)
end
```
Output:
```text
1
2
3
4
5
```
It starts at 1

Sampi also supports until loops:
```text
set guess to ""
until guess = "Password":
    say("That is not the password")
	set guess to ask("What is the password? ")
end
```
It stops when the condition is true.
Be careful not to make an infinite loop.

## **Functions**
```text
func greet name:
	say("Hello, " + name + "!")
end
```
To call a function, do:
```text
greet("World")
```
Output:
```text
Hello, World!
```
Use return to get a value, or exit the function.

For example:
```text
func add a b:
    return a + b
end

say(add(1, 2))
```
Output:
```text
3
```
## **Lists and Dictionaries**

Lists are made with square brackets:
```text
set x to ["a", "b", "c"]
say(x[1])
```
Output:
```text
a
```
Indexing starts at 1. 0 is the same as 1. ~1 gives the last index.

Dictionaries are made with curly braces:
```text
set x to {"a":1, "b":2}
say(x["a"])
```
Output
```text
1
```
To get the length of a list, use:
```text
set x to [1, 2, 3]
say(length(x))
```
Output:
```text
3
```
length() also works on dictionaries, strings, and numbers, too.

You can mess with lists and dictionaries:
```text
set x to ["a", "b", "c"]
```
| Method | Example | Result |
|---|---|---|
| add() | `x.add("d")` | `["a", "b", "c", "d"]` |
| remove() | `x.remove("b")` | `["a", "c"]` |
| delete | `x.delete(3)` | `["a","b"]` |
| get_index() | `x.get_index("c")` | `3` |
| insert() | `insert(1, "hello")` | `["a", "hello", "b", "c"]` |
| clear() | `x.clear()` | `[]` |
| join() | `x.join(", ")` | `"a, b, c"` |
```text
set x to {"a": 1, "b": 2, "c": 3}
```
| Method | Example | Result |
|---|---|---|
| add() | `x.add("d", 4)` | `{"a": 1, "b": 2, "c": 3, "d": 4}` |
| remove() | `x.remove("b")` | `{"a": 1, "c": 3}` |
| clear() | `x.clear()` | `{}` |

# **Nerd Section**

Sampi runs a VM that executes "bytecode".
I am hopefully going to move the VM to C for performance reasons.
