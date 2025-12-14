# tests/unit/test_factory.py

"""
Unit Tests for Calculation Factory Pattern

These tests validate the factory pattern implementation, ensuring:
1. Correct calculator instances are returned for each calculation type
2. Invalid types are properly rejected
3. Calculations produce correct results
4. Input validation works across all calculator types
5. Error handling is consistent

Design Pattern Tests:
- Factory Pattern: Verify object creation encapsulation
- Strategy Pattern: Verify different calculation strategies work correctly
- Registry Pattern: Verify dynamic type registration
"""

import pytest
from app.operations.factory import (
    CalculationFactory,
    Calculator,
    AdditionCalculator,
    SubtractionCalculator,
    MultiplicationCalculator,
    DivisionCalculator,
)
from app.schemas.calculation import CalculationType


class TestCalculatorInstances:
    """Test that factory returns correct calculator types."""

    def test_factory_returns_addition_calculator(self):
        """Verify factory returns AdditionCalculator for addition type."""
        calc = CalculationFactory.get_calculator(CalculationType.ADDITION)
        assert isinstance(calc, AdditionCalculator)

    def test_factory_returns_subtraction_calculator(self):
        """Verify factory returns SubtractionCalculator for subtraction type."""
        calc = CalculationFactory.get_calculator(CalculationType.SUBTRACTION)
        assert isinstance(calc, SubtractionCalculator)

    def test_factory_returns_multiplication_calculator(self):
        """Verify factory returns MultiplicationCalculator for multiplication type."""
        calc = CalculationFactory.get_calculator(CalculationType.MULTIPLICATION)
        assert isinstance(calc, MultiplicationCalculator)

    def test_factory_returns_division_calculator(self):
        """Verify factory returns DivisionCalculator for division type."""
        calc = CalculationFactory.get_calculator(CalculationType.DIVISION)
        assert isinstance(calc, DivisionCalculator)

    def test_factory_accepts_string_type(self):
        """Verify factory accepts string type names (case-insensitive)."""
        calc_lower = CalculationFactory.get_calculator("addition")
        calc_upper = CalculationFactory.get_calculator("ADDITION")
        calc_mixed = CalculationFactory.get_calculator("AdDiTioN")
        
        assert isinstance(calc_lower, AdditionCalculator)
        assert isinstance(calc_upper, AdditionCalculator)
        assert isinstance(calc_mixed, AdditionCalculator)

    def test_factory_rejects_invalid_type(self):
        """Verify factory raises ValueError for invalid calculation type."""
        with pytest.raises(ValueError) as exc_info:
            CalculationFactory.get_calculator("invalid_type")
        
        assert "Unknown calculation type" in str(exc_info.value)
        assert "Available types" in str(exc_info.value)


class TestAdditionCalculator:
    """Test Addition calculator strategy."""

    @pytest.mark.parametrize(
        "inputs,expected",
        [
            ([1, 2], 3),
            ([1, 2, 3], 6),
            ([10, 20, 30, 40], 100),
            ([-1, -2], -3),
            ([-5, 10], 5),
            ([1.5, 2.5], 4.0),
            ([1.1, 2.2, 3.3], 6.6),
        ],
        ids=[
            "two_positive_ints",
            "three_positive_ints",
            "four_positive_ints",
            "two_negative_ints",
            "negative_and_positive",
            "two_floats",
            "three_floats",
        ],
    )
    def test_addition_calculations(self, inputs, expected):
        """Test addition with various input combinations."""
        calc = AdditionCalculator()
        result = calc.calculate(inputs)
        assert result == pytest.approx(expected)

    def test_addition_requires_minimum_two_inputs(self):
        """Test addition validation requires at least 2 inputs."""
        calc = AdditionCalculator()
        
        with pytest.raises(ValueError) as exc_info:
            calc.calculate([5])
        
        assert "at least 2" in str(exc_info.value).lower()

    def test_addition_rejects_non_list(self):
        """Test addition rejects non-list inputs."""
        calc = AdditionCalculator()
        
        with pytest.raises(ValueError):
            calc.calculate("not a list")


class TestSubtractionCalculator:
    """Test Subtraction calculator strategy."""

    @pytest.mark.parametrize(
        "inputs,expected",
        [
            ([10, 3], 7),
            ([10, 3, 2], 5),  # 10 - 3 - 2 = 5
            ([100, 20, 30, 10], 40),  # 100 - 20 - 30 - 10 = 40
            ([0, 5], -5),
            ([-10, -5], -5),  # -10 - (-5) = -5
            ([10.5, 2.5], 8.0),
            ([20.0, 5.5, 3.2], 11.3),
        ],
        ids=[
            "two_positive_ints",
            "three_positive_ints",
            "four_positive_ints",
            "zero_and_positive",
            "two_negative_ints",
            "two_floats",
            "three_floats",
        ],
    )
    def test_subtraction_calculations(self, inputs, expected):
        """Test subtraction with various input combinations."""
        calc = SubtractionCalculator()
        result = calc.calculate(inputs)
        assert result == pytest.approx(expected)

    def test_subtraction_requires_minimum_two_inputs(self):
        """Test subtraction validation requires at least 2 inputs."""
        calc = SubtractionCalculator()
        
        with pytest.raises(ValueError) as exc_info:
            calc.calculate([5])
        
        assert "at least 2" in str(exc_info.value).lower()

    def test_subtraction_rejects_non_list(self):
        """Test subtraction rejects non-list inputs."""
        calc = SubtractionCalculator()
        
        with pytest.raises(ValueError):
            calc.calculate("not a list")


class TestMultiplicationCalculator:
    """Test Multiplication calculator strategy."""

    @pytest.mark.parametrize(
        "inputs,expected",
        [
            ([2, 3], 6),
            ([2, 3, 4], 24),
            ([2, 3, 4, 5], 120),
            ([0, 5], 0),
            ([-2, 3], -6),
            ([-2, -3], 6),
            ([2.5, 4], 10.0),
            ([1.5, 2.0, 3.0], 9.0),
        ],
        ids=[
            "two_positive_ints",
            "three_positive_ints",
            "four_positive_ints",
            "zero_and_positive",
            "negative_and_positive",
            "two_negative_ints",
            "float_and_int",
            "three_floats",
        ],
    )
    def test_multiplication_calculations(self, inputs, expected):
        """Test multiplication with various input combinations."""
        calc = MultiplicationCalculator()
        result = calc.calculate(inputs)
        assert result == pytest.approx(expected)

    def test_multiplication_requires_minimum_two_inputs(self):
        """Test multiplication validation requires at least 2 inputs."""
        calc = MultiplicationCalculator()
        
        with pytest.raises(ValueError) as exc_info:
            calc.calculate([5])
        
        assert "at least 2" in str(exc_info.value).lower()

    def test_multiplication_rejects_non_list(self):
        """Test multiplication rejects non-list inputs."""
        calc = MultiplicationCalculator()
        
        with pytest.raises(ValueError):
            calc.calculate("not a list")


class TestDivisionCalculator:
    """Test Division calculator strategy."""

    @pytest.mark.parametrize(
        "inputs,expected",
        [
            ([10, 2], 5.0),
            ([100, 2, 5], 10.0),  # 100 / 2 / 5 = 10
            ([100, 4, 5, 2], 2.5),  # 100 / 4 / 5 / 2 = 2.5
            ([15, 3], 5.0),
            ([-10, 2], -5.0),
            ([-10, -2], 5.0),
            ([7.5, 2.5], 3.0),
            ([100.0, 4.0, 5.0], 5.0),
        ],
        ids=[
            "two_positive_ints",
            "three_positive_ints",
            "four_positive_ints",
            "simple_division",
            "negative_and_positive",
            "two_negative_ints",
            "two_floats",
            "three_floats",
        ],
    )
    def test_division_calculations(self, inputs, expected):
        """Test division with various input combinations."""
        calc = DivisionCalculator()
        result = calc.calculate(inputs)
        assert result == pytest.approx(expected)

    def test_division_rejects_zero_divisor(self):
        """Test division rejects zero in divisor positions."""
        calc = DivisionCalculator()
        
        with pytest.raises(ValueError) as exc_info:
            calc.calculate([10, 0])
        
        assert "divide by zero" in str(exc_info.value).lower()

    def test_division_rejects_zero_in_chain(self):
        """Test division rejects zero in any divisor position."""
        calc = DivisionCalculator()
        
        with pytest.raises(ValueError) as exc_info:
            calc.calculate([100, 2, 0, 5])
        
        assert "divide by zero" in str(exc_info.value).lower()

    def test_division_requires_minimum_two_inputs(self):
        """Test division validation requires at least 2 inputs."""
        calc = DivisionCalculator()
        
        with pytest.raises(ValueError) as exc_info:
            calc.calculate([5])
        
        assert "at least 2" in str(exc_info.value).lower()

    def test_division_rejects_non_list(self):
        """Test division rejects non-list inputs."""
        calc = DivisionCalculator()
        
        with pytest.raises(ValueError):
            calc.calculate("not a list")


class TestFactoryRegistry:
    """Test factory registry functionality."""

    def test_get_available_types(self):
        """Test factory returns list of available types."""
        available = CalculationFactory.get_available_types()
        
        assert len(available) >= 4
        assert "addition" in available
        assert "subtraction" in available
        assert "multiplication" in available
        assert "division" in available

    def test_register_new_calculator_type(self):
        """Test registering a new calculator type at runtime."""
        
        # Create a mock calculator class for testing
        class SquareCalculator(Calculator):
            def calculate(self, inputs):
                self.validate(inputs)
                return inputs[0] ** 2
            
            def validate(self, inputs):
                if not isinstance(inputs, list) or len(inputs) < 1:
                    raise ValueError("Square requires at least 1 input")
        
        # Register the new type
        CalculationFactory.register("square", SquareCalculator)
        
        # Verify it can be retrieved
        calc = CalculationFactory.get_calculator("square")
        assert isinstance(calc, SquareCalculator)
        assert calc.calculate([5]) == 25

    def test_register_rejects_non_calculator_class(self):
        """Test register rejects classes that don't inherit from Calculator."""
        
        class NotACalculator:
            pass
        
        with pytest.raises(TypeError) as exc_info:
            CalculationFactory.register("invalid", NotACalculator)
        
        assert "must inherit from Calculator" in str(exc_info.value)

    def test_register_rejects_duplicate_type(self):
        """Test register rejects duplicate type registration."""
        
        class AnotherAddition(Calculator):
            def calculate(self, inputs):
                pass
            
            def validate(self, inputs):
                pass
        
        with pytest.raises(ValueError) as exc_info:
            CalculationFactory.register("addition", AnotherAddition)
        
        assert "already registered" in str(exc_info.value)


class TestFactoryIntegration:
    """Test factory working with Pydantic schemas."""

    def test_factory_with_calculation_type_enum(self):
        """Test factory works correctly with CalculationType enum."""
        for calc_type in CalculationType:
            calc = CalculationFactory.get_calculator(calc_type)
            assert isinstance(calc, Calculator)
            assert hasattr(calc, "calculate")
            assert hasattr(calc, "validate")

    def test_factory_handles_mixed_case_strings(self):
        """Test factory correctly normalizes case for string inputs."""
        test_cases = [
            ("ADDITION", AdditionCalculator),
            ("addition", AdditionCalculator),
            ("AdDiTioN", AdditionCalculator),
            ("DIVISION", DivisionCalculator),
            ("division", DivisionCalculator),
        ]
        
        for type_str, expected_class in test_cases:
            calc = CalculationFactory.get_calculator(type_str)
            assert isinstance(calc, expected_class)
