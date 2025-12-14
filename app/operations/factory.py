# app/operations/factory.py

"""
Calculation Factory Module

This module implements the Factory Pattern for creating calculation instances.
The factory pattern provides a centralized way to create and manage different
calculation types without exposing the details of their instantiation.

Key Benefits:
1. Encapsulation: Object creation logic is centralized
2. Flexibility: Easy to add new calculation types without modifying existing code
3. Consistency: All calculations created through the factory follow the same patterns
4. Testability: Easy to mock or swap implementations
5. Maintainability: Changes to creation logic only happen in one place

Design Patterns Used:
- Factory Pattern: Creates objects without specifying exact classes
- Strategy Pattern: Different calculation strategies (Add, Sub, Multiply, Divide)
- Dependency Injection: Calculator instances can be injected into other components

Type Safety:
- Uses ABC (Abstract Base Class) to enforce contract
- Type hints throughout for IDE support and early error detection
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Type, Union
import uuid
from sqlalchemy.orm import Session
from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)
from app.schemas.calculation import CalculationType


class Calculator(ABC):
    """
    Abstract base class for all calculation strategies.
    
    This defines the contract that all concrete calculator implementations
    must follow. Using an ABC ensures type safety and makes the interface
    explicit.
    
    The Strategy Pattern allows us to encapsulate different calculation
    algorithms and make them interchangeable.
    """

    @abstractmethod
    def calculate(self, inputs: List[float]) -> float:
        """
        Perform the calculation.
        
        Args:
            inputs: List of numeric values to calculate
            
        Returns:
            The result of the calculation
            
        Raises:
            ValueError: If inputs are invalid for this calculation type
        """
        pass

    @abstractmethod
    def validate(self, inputs: List[float]) -> None:
        """
        Validate inputs specific to this calculator.
        
        Args:
            inputs: List of numeric values to validate
            
        Raises:
            ValueError: If inputs are invalid
        """
        pass


class AdditionCalculator(Calculator):
    """
    Concrete calculator for addition operations.
    
    Strategy: Sum all input values
    
    Example:
        calc = AdditionCalculator()
        result = calc.calculate([1, 2, 3])  # Returns 6
    """

    def calculate(self, inputs: List[float]) -> float:
        """Sum all input values."""
        self.validate(inputs)
        return sum(inputs)

    def validate(self, inputs: List[float]) -> None:
        """Validate inputs for addition."""
        if not isinstance(inputs, list) or len(inputs) < 2:
            raise ValueError("Addition requires at least 2 numeric inputs")


class SubtractionCalculator(Calculator):
    """
    Concrete calculator for subtraction operations.
    
    Strategy: Subtract each subsequent value from the first value
    Formula: inputs[0] - inputs[1] - inputs[2] - ...
    
    Example:
        calc = SubtractionCalculator()
        result = calc.calculate([10, 3, 2])  # Returns 5 (10 - 3 - 2)
    """

    def calculate(self, inputs: List[float]) -> float:
        """Subtract sequentially from the first number."""
        self.validate(inputs)
        result = inputs[0]
        for value in inputs[1:]:
            result -= value
        return result

    def validate(self, inputs: List[float]) -> None:
        """Validate inputs for subtraction."""
        if not isinstance(inputs, list) or len(inputs) < 2:
            raise ValueError("Subtraction requires at least 2 numeric inputs")


class MultiplicationCalculator(Calculator):
    """
    Concrete calculator for multiplication operations.
    
    Strategy: Multiply all input values together
    Formula: inputs[0] * inputs[1] * inputs[2] * ...
    
    Example:
        calc = MultiplicationCalculator()
        result = calc.calculate([2, 3, 4])  # Returns 24
    """

    def calculate(self, inputs: List[float]) -> float:
        """Multiply all input values together."""
        self.validate(inputs)
        result = 1
        for value in inputs:
            result *= value
        return result

    def validate(self, inputs: List[float]) -> None:
        """Validate inputs for multiplication."""
        if not isinstance(inputs, list) or len(inputs) < 2:
            raise ValueError("Multiplication requires at least 2 numeric inputs")


class DivisionCalculator(Calculator):
    """
    Concrete calculator for division operations.
    
    Strategy: Divide the first value by each subsequent value
    Formula: inputs[0] / inputs[1] / inputs[2] / ...
    
    Example:
        calc = DivisionCalculator()
        result = calc.calculate([100, 2, 5])  # Returns 10 (100 / 2 / 5)
        
    Note: Validates that no divisor is zero using EAFP
    (Easier to Ask for Forgiveness than Permission)
    """

    def calculate(self, inputs: List[float]) -> float:
        """Divide the first number by subsequent numbers sequentially."""
        self.validate(inputs)
        result = inputs[0]
        for value in inputs[1:]:
            if value == 0:
                raise ValueError("Cannot divide by zero")
            result /= value
        return result

    def validate(self, inputs: List[float]) -> None:
        """Validate inputs for division."""
        if not isinstance(inputs, list) or len(inputs) < 2:
            raise ValueError("Division requires at least 2 numeric inputs")
        # Check for zero divisors (all values except the first one)
        if any(x == 0 for x in inputs[1:]):
            raise ValueError("Cannot divide by zero")


class CalculationFactory:
    """
    Factory for creating and managing calculation instances.
    
    This is the central point for creating calculations. It maintains a registry
    of available calculation types and ensures consistent creation patterns.
    
    The Factory Pattern provides several advantages:
    1. Single Responsibility: All creation logic is here
    2. Open/Closed Principle: Easy to add new types without modifying existing code
    3. Testability: Can be mocked or extended for testing
    4. Consistency: All calculations follow the same creation pattern
    
    Usage:
        factory = CalculationFactory()
        calc = factory.get_calculator(CalculationType.ADDITION)
        result = calc.calculate([1, 2, 3])
    """

    # Registry mapping calculation types to calculator classes
    _registry: Dict[str, Type[Calculator]] = {
        CalculationType.ADDITION.value: AdditionCalculator,
        CalculationType.SUBTRACTION.value: SubtractionCalculator,
        CalculationType.MULTIPLICATION.value: MultiplicationCalculator,
        CalculationType.DIVISION.value: DivisionCalculator,
    }

    @classmethod
    def get_calculator(
        cls, calculation_type: Union[CalculationType, str]
    ) -> Calculator:
        """
        Get a calculator instance for the specified calculation type.
        
        Args:
            calculation_type: Either a CalculationType enum or string
            
        Returns:
            An instance of the appropriate calculator
            
        Raises:
            ValueError: If calculation_type is not registered
            
        Example:
            calc = CalculationFactory.get_calculator(CalculationType.ADDITION)
            calc = CalculationFactory.get_calculator("addition")
        """
        # Normalize input to string
        type_str = (
            calculation_type.value
            if isinstance(calculation_type, CalculationType)
            else str(calculation_type).lower()
        )

        calculator_class = cls._registry.get(type_str)
        if not calculator_class:
            available = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(
                f"Unknown calculation type: {type_str}. "
                f"Available types: {available}"
            )

        return calculator_class()

    @classmethod
    def register(cls, type_name: str, calculator_class: Type[Calculator]) -> None:
        """
        Register a new calculator type.
        
        This allows for runtime extension of supported calculation types
        without modifying the factory code.
        
        Args:
            type_name: String identifier for the calculation type
            calculator_class: Calculator class to associate with this type
            
        Raises:
            TypeError: If calculator_class doesn't inherit from Calculator
            ValueError: If type_name is already registered
            
        Example:
            class PowerCalculator(Calculator):
                def calculate(self, inputs):
                    return inputs[0] ** inputs[1]
                def validate(self, inputs):
                    if len(inputs) != 2:
                        raise ValueError("Power needs exactly 2 numbers")
            
            CalculationFactory.register("power", PowerCalculator)
        """
        if not issubclass(calculator_class, Calculator):
            raise TypeError(
                f"{calculator_class} must inherit from Calculator"
            )

        if type_name in cls._registry:
            raise ValueError(
                f"Calculation type '{type_name}' is already registered"
            )

        cls._registry[type_name] = calculator_class

    @classmethod
    def get_available_types(cls) -> List[str]:
        """
        Get all available calculation types.
        
        Returns:
            List of registered calculation type names
            
        Example:
            types = CalculationFactory.get_available_types()
            # Returns: ['addition', 'subtraction', 'multiplication', 'division']
        """
        return sorted(cls._registry.keys())

    @classmethod
    def create_and_store(
        cls,
        calculation_type: Union[CalculationType, str],
        user_id: uuid.UUID,
        inputs: List[float],
        db: Session,
    ) -> Calculation:
        """
        Factory method to create a calculation and store it in the database.
        
        This combines the factory pattern with data persistence. It validates
        the inputs using the appropriate calculator before creating the model.
        
        Args:
            calculation_type: Type of calculation to create
            user_id: UUID of the user who owns this calculation
            inputs: List of numeric inputs
            db: SQLAlchemy session for database operations
            
        Returns:
            Persisted Calculation instance with computed result
            
        Raises:
            ValueError: If inputs are invalid for the calculation type
            
        Example:
            calculation = CalculationFactory.create_and_store(
                CalculationType.ADDITION,
                user_id,
                [1, 2, 3],
                db_session
            )
            assert calculation.result == 6
        """
        # Get the appropriate calculator and validate inputs
        calculator = cls.get_calculator(calculation_type)
        calculator.validate(inputs)

        # Compute the result
        result = calculator.calculate(inputs)

        # Create the model instance using SQLAlchemy's factory
        type_str = (
            calculation_type.value
            if isinstance(calculation_type, CalculationType)
            else str(calculation_type).lower()
        )
        
        calculation = Calculation.create(type_str, user_id, inputs)
        calculation.result = result

        # Persist to database
        db.add(calculation)
        db.commit()
        db.refresh(calculation)

        return calculation


# Convenience factory instance for use as a singleton
factory = CalculationFactory()
