"""
test_calculator_engine.py
──────────────────────────
Unit tests for CalculatorEngine.
Run with:  python -m pytest test_calculator_engine.py -v
           (or) python test_calculator_engine.py
"""

import math
import sys
import unittest

from calculator_engine import CalculatorEngine


class TestBasicArithmetic(unittest.TestCase):

    def setUp(self):
        self.calc = CalculatorEngine()

    def _eval(self, expr: str) -> str:
        self.calc.current_expression = expr
        result, error = self.calc.evaluate()
        self.assertIsNone(error, f"Unexpected error for '{expr}': {error}")
        return result

    # ── Addition
    def test_addition_integers(self):
        self.assertEqual(self._eval("2+3"), "5")

    def test_addition_floats(self):
        result = float(self._eval("1.5+2.5"))
        self.assertAlmostEqual(result, 4.0)

    # ── Subtraction
    def test_subtraction(self):
        self.assertEqual(self._eval("10-3"), "7")

    def test_subtraction_negative_result(self):
        self.assertEqual(self._eval("3-10"), "-7")

    # ── Multiplication
    def test_multiplication(self):
        self.assertEqual(self._eval("6*7"), "42")

    def test_multiplication_by_zero(self):
        self.assertEqual(self._eval("999*0"), "0")

    # ── Division
    def test_division(self):
        self.assertEqual(self._eval("10/2"), "5")

    def test_division_float_result(self):
        result = float(self._eval("1/3"))
        self.assertAlmostEqual(result, 1 / 3, places=8)

    def test_division_by_zero(self):
        self.calc.current_expression = "1/0"
        _, error = self.calc.evaluate()
        self.assertIsNotNone(error)
        self.assertIn("Zero", error)

    # ── Mixed operations (operator precedence)
    def test_precedence_mul_before_add(self):
        result = float(self._eval("2+3*4"))
        self.assertAlmostEqual(result, 14.0)

    def test_parentheses_override_precedence(self):
        result = float(self._eval("(2+3)*4"))
        self.assertAlmostEqual(result, 20.0)

    def test_complex_expression(self):
        result = float(self._eval("(10+5)*2-3**2"))
        self.assertAlmostEqual(result, 21.0)


class TestScientificFunctions(unittest.TestCase):

    def setUp(self):
        self.calc = CalculatorEngine()

    def _eval(self, expr: str) -> float:
        self.calc.current_expression = expr
        result, error = self.calc.evaluate()
        self.assertIsNone(error, f"Error for '{expr}': {error}")
        return float(result)

    def test_sqrt_of_9(self):
        self.assertAlmostEqual(self._eval("sqrt(9)"), 3.0)

    def test_sqrt_of_2(self):
        self.assertAlmostEqual(self._eval("sqrt(2)"), math.sqrt(2), places=8)

    def test_sqrt_negative_raises_error(self):
        self.calc.current_expression = "sqrt(-1)"
        _, error = self.calc.evaluate()
        self.assertIsNotNone(error)

    def test_sin_0(self):
        self.assertAlmostEqual(self._eval("sin(0)"), 0.0, places=8)

    def test_sin_90(self):
        self.assertAlmostEqual(self._eval("sin(90)"), 1.0, places=8)

    def test_cos_0(self):
        self.assertAlmostEqual(self._eval("cos(0)"), 1.0, places=8)

    def test_cos_180(self):
        self.assertAlmostEqual(self._eval("cos(180)"), -1.0, places=8)

    def test_tan_45(self):
        self.assertAlmostEqual(self._eval("tan(45)"), 1.0, places=8)

    def test_log_100(self):
        self.assertAlmostEqual(self._eval("log(100)"), 2.0, places=8)

    def test_ln_e(self):
        self.assertAlmostEqual(self._eval("ln(e)"), 1.0, places=8)

    def test_factorial_5(self):
        self.assertAlmostEqual(self._eval("factorial(int(5))"), 120.0)

    def test_pi_constant(self):
        self.assertAlmostEqual(self._eval("pi"), math.pi, places=8)

    def test_euler_constant(self):
        self.assertAlmostEqual(self._eval("e"), math.e, places=8)

    def test_power(self):
        self.assertAlmostEqual(self._eval("2**10"), 1024.0)


class TestMemoryOperations(unittest.TestCase):

    def setUp(self):
        self.calc = CalculatorEngine()

    def test_memory_store_and_recall(self):
        self.calc.current_expression = "42"
        self.calc.evaluate()
        self.calc.memory_store()
        self.assertEqual(self.calc.memory, 42.0)
        self.calc.clear_all()
        self.calc.memory_recall()
        self.assertIn("42", self.calc.current_expression)

    def test_memory_add(self):
        self.calc.current_expression = "10"
        self.calc.evaluate()
        self.calc.memory_store()
        self.calc.current_expression = "5"
        self.calc.evaluate()
        self.calc.memory_add()
        self.assertAlmostEqual(self.calc.memory, 15.0)

    def test_memory_clear(self):
        self.calc.memory = 99.0
        self.calc.memory_clear()
        self.assertEqual(self.calc.memory, 0.0)


class TestClearAndBackspace(unittest.TestCase):

    def setUp(self):
        self.calc = CalculatorEngine()

    def test_clear_all_resets_expression(self):
        self.calc.current_expression = "123+456"
        self.calc.clear_all()
        self.assertEqual(self.calc.current_expression, "")
        self.assertIsNone(self.calc.last_result)

    def test_clear_entry_removes_last_char(self):
        self.calc.current_expression = "1234"
        self.calc.clear_entry()
        self.assertEqual(self.calc.current_expression, "123")

    def test_clear_entry_on_result_clears_all(self):
        self.calc.current_expression = "5"
        self.calc.evaluate()
        self.calc.clear_entry()
        self.assertEqual(self.calc.current_expression, "")


class TestHistory(unittest.TestCase):

    def setUp(self):
        self.calc = CalculatorEngine()

    def test_history_records_evaluations(self):
        self.calc.current_expression = "2+2"
        self.calc.evaluate()
        self.calc.current_expression = "3*3"
        self.calc.evaluate()
        history = self.calc.get_history()
        self.assertEqual(len(history), 2)

    def test_history_most_recent_first(self):
        self.calc.current_expression = "1+1"
        self.calc.evaluate()
        self.calc.current_expression = "9+9"
        self.calc.evaluate()
        history = self.calc.get_history()
        self.assertIn("18", history[0][1])

    def test_clear_history(self):
        self.calc.current_expression = "5*5"
        self.calc.evaluate()
        self.calc.clear_history()
        self.assertEqual(len(self.calc.get_history()), 0)


class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        self.calc = CalculatorEngine()

    def test_empty_expression_returns_empty(self):
        self.calc.current_expression = ""
        result, error = self.calc.evaluate()
        self.assertEqual(result, "")
        self.assertIsNone(error)

    def test_syntax_error_expression(self):
        self.calc.current_expression = "2+*3"
        _, error = self.calc.evaluate()
        self.assertIsNotNone(error)

    def test_large_factorial_overflow(self):
        # 1000! triggers OverflowError in float context (factorial returns int)
        # Our engine uses math.factorial which returns Python bigint - it should work
        self.calc.current_expression = "factorial(int(10))"
        result, error = self.calc.evaluate()
        self.assertIsNone(error)
        self.assertEqual(result, str(math.factorial(10)))

    def test_negate_expression(self):
        self.calc.current_expression = "5"
        self.calc.apply_negate()
        self.assertIn("5", self.calc.current_expression)
        self.assertIn("-", self.calc.current_expression)

    def test_ans_chaining_with_operator(self):
        self.calc.current_expression = "10"
        self.calc.evaluate()
        # After evaluation, appending operator should chain from result
        self.calc.append("+")
        self.assertIn("10", self.calc.current_expression)
        self.assertIn("+", self.calc.current_expression)


if __name__ == "__main__":
    unittest.main(verbosity=2)
