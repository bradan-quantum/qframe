# QFrame package for quantum calculations

QFrame is a Python library layered over [Eclipse Qrisp](https://qrisp.eu/index.html), which enables you to search for solutions to equations of the form $g(x, y, z)=(x_t, y_t, z_t)$.

The library provides operations to define the function of interest $g(x, y, z)$ and then applies the partial oracle search algorithm to find the solution values $x_s, y_s, z_s$ that satisfy $g(x_s, y_s, z_s)=(x_t, y_t, z_t)$ for the given target values $x_t, y_t, z_t$.

QFrame forms part of an ongoing research project into exponentially fast quantum algorithms and is currently in a very early stage of development with limited functionality. The set of function and operations provided in the 0.0.x release are only capable of defining functions $g(\cdot)$ that are classically reversible, so that no quantum advantage is demonstrated. The next phase of research will attempt to extend QFrame's functionality to cover non-trivial functions that are difficult to invert.


## Using the QFrame library

The `qframe.QFrameUInt` type provides an abstract representation of the qubit registers and QFrame provides a limited set of functions and operations for combining `QFrameUInt` instances.

The following operations and functions are provided by QFrame:

* $\mathrel{+}=$ operation&mdash;defines in-place addition modulo $2^w$, where $w$ is the bit-width of the `QFrameUInt` arguments. The following cases are supported:
  - Given `QFrameUInt` instances $x$ and $y$, the operation $x \mathrel{+}= y$ implements $P\,\ket{x}\ket{y} = \ket{x+y}\ket{y}$.
  - Given a `QFrameUInt` instance $x$ and an integer constant $c$, the operation $x \mathrel{+}= c$ implements $\ket{x}\mapsto\ket{x+c}$.
  - Given a `QFrameUInt` instance $x$ and a temporary function $t(y)$, such that $V\,\ket{y} = \ket{t(y)}$, the operation $x \mathrel{+}= t(y)$ implements $V^\dagger PV \ket{x}\ket{y} = \ket{x + t(y)}\ket{y}$.

* `qframe.maj(a, b, c)`&mdash;defines the majority function $Maj(a, b, c)$, where $a$, $b$, and $c$ are $w$-bit registers. The `maj(a, b, c)` function is a temporary function, in the sense that it does not permanently change the values of registers $a$, $b$, and $c$. It is intended to be used on the right-hand side of a $\mathrel{+}=$ expression.

* `qframe.ch(a, b, c)`&mdash;defines the choose function $Ch(a, b, c)$, where $a$, $b$, and $c$ are $w$-bit registers. The `ch(a, b, c)` function is a temporary function, in the sense that it does not permanently change the values of registers $a$, $b$, and $c$. It is intended to be used on the right-hand side of a $\mathrel{+}=$ expression.

* `qframe.Rotr` class&mdash;can be used to define shift operator instances. For example, `r = qframe.Rotr(4, [0, 1], shr_list=[3])` defines a 4-bit wide shift operator of type $\mu=(0,1)(3)$. The `r.shift_inline(x)` method can then be invoked to apply the shift function to register $x$. If you need to add the result of a shift operation to another register in a $\mathrel{+}=$ expression, you should invoke `r.shift(x)`, which acts as a temporary function (leaving register $x$ unchanged after the addition operation).

This utility provides all of the operations and functions you would need to implement the SHA-256 algorithm. After defining an algorithm with QFrame, the `QFrameSession` object provides access to the following generated methods:

* `QFrameSession.calculate(input_args)`&mdash;implements the classical function $g(\cdot)$, taking the given `input_arg` values for the registers and returning the values of the registers after calculating $g(\cdot)$.

* `QFrameSession.apply_oracle_gate(target_dict)`&mdash;generates the circuit of the oracle function, where the relevant target values are specified by the `target_dict` argument.

* `QFrameSession.apply_recip_oracle_gate()`&mdash;generates the circuit for the reciprocal oracle function, $R[f(\cdot)]$.

* `QFrameSession.partial_oracle_iteration(target_dict)`&mdash;generates complete code for the partial oracle algorithm (except for the initialization of the qubit registers).

## Examples

A set of working examples will shortly be published in a GitHub repository.

In the meantime, you can get an idea of how to use the library functions by looking at the test files in `tests/core`.

## Running unit tests

Use hatchling to run unit tests (based on pytest):

```bash
hatch test
```

To see the output from `print` statements while running the tests, enter:
```bash
hatch test --capture=no
```

