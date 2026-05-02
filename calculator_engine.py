"""
calculator_engine.py
────────────────────
Pure computation layer for the Advanced Scientific Calculator.
No Tkinter imports; fully unit-testable in isolation.

Supports:
  • Basic arithmetic  (+, -, *, /)
  • Integer division  (//)
  • Modulus           (%)
  • Power             (^ or **)
  • Square root       (√)
  • Trigonometry      (sin, cos, tan – degrees input)
  • Inverse trig      (asin, acos, atan)
  • Logarithms        (log10, ln)
  • Factorial         (n!)
  • Absolute value    (|x|)
  • Constants         (π, e)
  • Percentage        (%)
  • Expression parsing via Python's `eval` with a safe namespace
"""

import math
import re
from decimal import Decimal, InvalidOperation


# ─────────────────────────────────────────────────────────
#  Safe evaluation namespace – only math functions allowed
# ─────────────────────────────────────────────────────────
SAFE_NAMESPACE: dict = {
    "__builtins__": {},
    "int":   int,
    "float": float,
    "round": round,
    "sin":  lambda x: math.sin(math.radians(x)),
    "cos":  lambda x: math.cos(math.radians(x)),
    "tan":  lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "sqrt": math.sqrt,
    "log":  math.log10,          # log() = log base 10
    "ln":   math.log,            # ln()  = natural log
    "abs":  abs,
    "factorial": math.factorial,
    "ceil":  math.ceil,
    "floor": math.floor,
    "pi":   math.pi,
    "e":    math.e,
    "pow":  math.pow,
}


class CalculatorEngine:
    """
    Stateful calculator engine.

    Maintains:
      • current_expression  – the expression string being built
      • last_result         – result of the last successful evaluation
      • history             – list of (expression, result) tuples
      • memory              – single memory register (M+/MR/MC)
    """

    MAX_HISTORY = 50

    def __init__(self) -> None:
        self.current_expression: str = ""
        self.last_result:        float | None = None
        self.history:            list[tuple[str, str]] = []
        self.memory:             float = 0.0
        self._last_was_result:   bool = False   # Tracks ANS continuity

    # ─────────────────────────────────────────────────────
    #  Core: append a token to the expression
    # ─────────────────────────────────────────────────────
    def append(self, token: str) -> str:
        """
        Append a digit, operator, or function token.
        Handles ANS chaining: if the last action was an evaluation,
        and the new token is an operator, prepend the last result.
        Returns the current expression string.
        """
        if self._last_was_result:
            # If user types a digit/function after result → start fresh
            if token not in ("+", "-", "*", "/", "//", "%", "^", ")"):
                self.current_expression = ""
            else:
                # Continue from last result
                self.current_expression = self._format_result(self.last_result)
            self._last_was_result = False

        self.current_expression += token
        return self.current_expression

    # ─────────────────────────────────────────────────────
    #  Core: evaluate the current expression
    # ─────────────────────────────────────────────────────
    def evaluate(self) -> tuple[str, str | None]:
        """
        Evaluate self.current_expression.

        Returns:
            (result_str, error_str)
            One of them will be None.
        """
        expr = self.current_expression.strip()
        if not expr:
            return ("", None)

        # Normalise: replace ^ with ** for Python eval
        normalised = self._normalise_expression(expr)

        try:
            raw = eval(normalised, SAFE_NAMESPACE)  # noqa: S307
        except ZeroDivisionError:
            return ("", "Division by Zero")
        except OverflowError:
            return ("", "Result too large")
        except ValueError as exc:
            return ("", f"Math Error: {exc}")
        except SyntaxError:
            return ("", "Syntax Error")
        except Exception as exc:  # noqa: BLE001
            return ("", str(exc))

        if not isinstance(raw, (int, float)):
            return ("", "Type Error")
        if math.isnan(raw):
            return ("", "Not a Number")
        if math.isinf(raw):
            return ("", "Infinity")

        result_str = self._format_result(raw)
        self.last_result = float(raw)
        self._last_was_result = True

        # Store in history
        entry = (expr, result_str)
        self.history.append(entry)
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)

        self.current_expression = result_str
        return (result_str, None)

    # ─────────────────────────────────────────────────────
    #  Core: clear / backspace / reset
    # ─────────────────────────────────────────────────────
    def clear_entry(self) -> str:
        """Remove the last character from the expression (CE / backspace)."""
        if self._last_was_result:
            self.current_expression = ""
            self._last_was_result = False
        elif self.current_expression:
            self.current_expression = self.current_expression[:-1]
        return self.current_expression

    def clear_all(self) -> str:
        """Full reset: clear expression and last result (AC)."""
        self.current_expression = ""
        self.last_result = None
        self._last_was_result = False
        return ""

    # ─────────────────────────────────────────────────────
    #  Memory operations
    # ─────────────────────────────────────────────────────
    def memory_store(self) -> None:
        """MS – store last result (or 0) into memory."""
        self.memory = self.last_result if self.last_result is not None else 0.0

    def memory_recall(self) -> str:
        """MR – append memory value to expression."""
        return self.append(self._format_result(self.memory))

    def memory_add(self) -> None:
        """M+ – add last result to memory."""
        if self.last_result is not None:
            self.memory += self.last_result

    def memory_clear(self) -> None:
        """MC – reset memory register to zero."""
        self.memory = 0.0

    # ─────────────────────────────────────────────────────
    #  Unary scientific operations  (apply to last result)
    # ─────────────────────────────────────────────────────
    def apply_sqrt(self) -> tuple[str, str | None]:
        """Wrap current expression in sqrt(...)."""
        self.current_expression = f"sqrt({self.current_expression})"
        return self.evaluate()

    def apply_square(self) -> tuple[str, str | None]:
        """Square the current expression: expr**2."""
        self.current_expression = f"({self.current_expression})**2"
        return self.evaluate()

    def apply_inverse(self) -> tuple[str, str | None]:
        """1/x – reciprocal of current expression."""
        self.current_expression = f"1/({self.current_expression})"
        return self.evaluate()

    def apply_negate(self) -> str:
        """Toggle sign: wrap in -(...)."""
        expr = self.current_expression
        if expr.startswith("-(") and expr.endswith(")"):
            self.current_expression = expr[2:-1]
        elif expr:
            self.current_expression = f"-({expr})"
        return self.current_expression

    def apply_percent(self) -> str:
        """Divide current value by 100."""
        self.current_expression = f"({self.current_expression})/100"
        return self.current_expression

    def apply_factorial(self) -> tuple[str, str | None]:
        """n! – factorial of current expression."""
        self.current_expression = f"factorial(int({self.current_expression}))"
        return self.evaluate()

    def apply_log(self) -> tuple[str, str | None]:
        """log10 of current expression."""
        self.current_expression = f"log({self.current_expression})"
        return self.evaluate()

    def apply_ln(self) -> tuple[str, str | None]:
        """Natural log of current expression."""
        self.current_expression = f"ln({self.current_expression})"
        return self.evaluate()

    def apply_sin(self) -> tuple[str, str | None]:
        self.current_expression = f"sin({self.current_expression})"
        return self.evaluate()

    def apply_cos(self) -> tuple[str, str | None]:
        self.current_expression = f"cos({self.current_expression})"
        return self.evaluate()

    def apply_tan(self) -> tuple[str, str | None]:
        self.current_expression = f"tan({self.current_expression})"
        return self.evaluate()

    # ─────────────────────────────────────────────────────
    #  History access
    # ─────────────────────────────────────────────────────
    def get_history(self) -> list[tuple[str, str]]:
        return list(reversed(self.history))

    def clear_history(self) -> None:
        self.history.clear()

    # ─────────────────────────────────────────────────────
    #  Private helpers
    # ─────────────────────────────────────────────────────
    @staticmethod
    def _normalise_expression(expr: str) -> str:
        """
        Replace display tokens with Python-eval-compatible equivalents.
        """
        expr = expr.replace("^", "**")
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")
        expr = expr.replace("π", "pi")
        return expr

    @staticmethod
    def _format_result(value: float | None) -> str:
        """
        Format a float for display:
          • Integers shown without decimal point
          • Up to 10 significant figures for floats
        """
        if value is None:
            return "0"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        # Remove trailing zeros after decimal
        formatted = f"{value:.10g}"
        return formatted
