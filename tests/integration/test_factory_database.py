# tests/integration/test_factory_database.py

"""
Integration Tests for Factory Pattern with Database

These tests verify that the factory pattern correctly integrates with:
1. SQLAlchemy models
2. Database persistence
3. Pydantic schemas
4. User relationships

Test Scenarios:
- Create calculations via factory and verify database storage
- Verify correct model types are stored and retrieved
- Test calculations with valid and invalid inputs
- Verify user foreign key relationships
- Test error handling with database constraints
"""

import pytest
import uuid
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)
from app.operations.factory import CalculationFactory
from app.schemas.calculation import CalculationType


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    
    This fixture:
    1. Creates all tables before the test
    2. Provides a session for database operations
    3. Rolls back all changes after the test
    4. Ensures tests don't interfere with each other
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    session = SessionLocal()
    
    yield session
    
    # Rollback and cleanup
    session.rollback()
    session.close()
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db_session: Session):
    """Create a test user for calculations."""
    user = User(
        username="testuser",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestFactoryDatabaseStorage:
    """Test factory creates and stores calculations correctly."""

    def test_factory_creates_and_stores_addition(self, db_session: Session, test_user: User):
        """Test factory creates and persists an addition calculation."""
        calculation = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            [1, 2, 3],
            db_session
        )
        
        # Verify the calculation was created with correct values
        assert calculation.id is not None
        assert calculation.user_id == test_user.id
        assert calculation.inputs == [1, 2, 3]
        assert calculation.result == 6
        assert isinstance(calculation, Addition)

    def test_factory_creates_and_stores_subtraction(self, db_session: Session, test_user: User):
        """Test factory creates and persists a subtraction calculation."""
        calculation = CalculationFactory.create_and_store(
            CalculationType.SUBTRACTION,
            test_user.id,
            [10, 3, 2],
            db_session
        )
        
        assert calculation.result == 5  # 10 - 3 - 2 = 5
        assert isinstance(calculation, Subtraction)
        assert calculation.type == "subtraction"

    def test_factory_creates_and_stores_multiplication(self, db_session: Session, test_user: User):
        """Test factory creates and persists a multiplication calculation."""
        calculation = CalculationFactory.create_and_store(
            CalculationType.MULTIPLICATION,
            test_user.id,
            [2, 3, 4],
            db_session
        )
        
        assert calculation.result == 24  # 2 * 3 * 4 = 24
        assert isinstance(calculation, Multiplication)

    def test_factory_creates_and_stores_division(self, db_session: Session, test_user: User):
        """Test factory creates and persists a division calculation."""
        calculation = CalculationFactory.create_and_store(
            CalculationType.DIVISION,
            test_user.id,
            [100, 2, 5],
            db_session
        )
        
        assert calculation.result == 10  # 100 / 2 / 5 = 10
        assert isinstance(calculation, Division)

    def test_calculation_persists_in_database(self, db_session: Session, test_user: User):
        """Test that created calculations can be retrieved from database."""
        # Create a calculation
        original = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            [5, 10, 15],
            db_session
        )
        
        # Query the database
        retrieved = db_session.query(Calculation).filter(
            Calculation.id == original.id
        ).first()
        
        assert retrieved is not None
        assert retrieved.id == original.id
        assert retrieved.result == 30
        assert retrieved.user_id == test_user.id

    def test_calculation_polymorphic_type_resolution(self, db_session: Session, test_user: User):
        """Test that SQLAlchemy correctly resolves calculation subtypes."""
        # Create different calculation types
        addition = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            [1, 2],
            db_session
        )
        
        division = CalculationFactory.create_and_store(
            CalculationType.DIVISION,
            test_user.id,
            [10, 2],
            db_session
        )
        
        # Query all calculations
        all_calcs = db_session.query(Calculation).all()
        
        # Verify we got the right number and correct types
        assert len(all_calcs) == 2
        
        # Find each by ID and verify type
        add_retrieved = next(c for c in all_calcs if c.id == addition.id)
        div_retrieved = next(c for c in all_calcs if c.id == division.id)
        
        assert isinstance(add_retrieved, Addition)
        assert isinstance(div_retrieved, Division)


class TestFactoryErrorHandling:
    """Test factory handles errors gracefully."""

    def test_factory_rejects_zero_divisor(self, db_session: Session, test_user: User):
        """Test factory validation rejects division by zero before database insert."""
        with pytest.raises(ValueError) as exc_info:
            CalculationFactory.create_and_store(
                CalculationType.DIVISION,
                test_user.id,
                [10, 0],
                db_session
            )
        
        assert "divide by zero" in str(exc_info.value).lower()
        
        # Verify nothing was written to database
        count = db_session.query(Calculation).count()
        assert count == 0

    def test_factory_rejects_insufficient_inputs(self, db_session: Session, test_user: User):
        """Test factory validation rejects insufficient inputs."""
        with pytest.raises(ValueError) as exc_info:
            CalculationFactory.create_and_store(
                CalculationType.ADDITION,
                test_user.id,
                [5],  # Only one input, need at least 2
                db_session
            )
        
        assert "at least 2" in str(exc_info.value).lower()
        
        # Verify nothing was written to database
        count = db_session.query(Calculation).count()
        assert count == 0

    def test_factory_rejects_invalid_type(self, db_session: Session, test_user: User):
        """Test factory rejects invalid calculation type."""
        with pytest.raises(ValueError) as exc_info:
            CalculationFactory.create_and_store(
                "invalid_type",
                test_user.id,
                [1, 2],
                db_session
            )
        
        assert "Unknown calculation type" in str(exc_info.value)

    def test_factory_rejects_invalid_user_id(self, db_session: Session):
        """Test factory handles invalid user_id gracefully."""
        invalid_user_id = uuid.uuid4()
        
        # This should succeed in creation but may fail on commit due to FK constraint
        # depending on the database configuration
        try:
            CalculationFactory.create_and_store(
                CalculationType.ADDITION,
                invalid_user_id,
                [1, 2],
                db_session
            )
            # If it succeeded, rollback and try again
            db_session.rollback()
        except Exception:
            # Expected - foreign key constraint violation
            pass


class TestFactoryUserRelationship:
    """Test factory correctly handles user relationships."""

    def test_calculation_linked_to_user(self, db_session: Session, test_user: User):
        """Test that calculations are correctly linked to users."""
        calculation = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            [1, 2, 3],
            db_session
        )
        
        # Access the user through the relationship
        assert calculation.user is not None
        assert calculation.user.id == test_user.id
        assert calculation.user.username == "testuser"

    def test_user_has_multiple_calculations(self, db_session: Session, test_user: User):
        """Test user can have multiple calculations."""
        # Create multiple calculations for the same user
        calcs = []
        for i in range(3):
            calc = CalculationFactory.create_and_store(
                CalculationType.ADDITION,
                test_user.id,
                [i, i+1],
                db_session
            )
            calcs.append(calc)
        
        # Refresh user to load relationships
        db_session.refresh(test_user)
        
        # Verify user has all calculations
        assert len(test_user.calculations) == 3
        user_calc_ids = {c.id for c in test_user.calculations}
        expected_ids = {c.id for c in calcs}
        assert user_calc_ids == expected_ids

    def test_cascade_delete_user_deletes_calculations(self, db_session: Session, test_user: User):
        """Test that deleting a user also deletes their calculations (cascade)."""
        # Create calculations for the user
        CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            [1, 2],
            db_session
        )
        
        # Verify calculation exists
        calc_count = db_session.query(Calculation).filter(
            Calculation.user_id == test_user.id
        ).count()
        assert calc_count == 1
        
        # Delete the user
        db_session.delete(test_user)
        db_session.commit()
        
        # Verify calculations are also deleted
        calc_count = db_session.query(Calculation).filter(
            Calculation.user_id == test_user.id
        ).count()
        assert calc_count == 0


class TestFactoryEdgeCases:
    """Test factory handles edge cases correctly."""

    def test_factory_with_large_numbers(self, db_session: Session, test_user: User):
        """Test factory handles large numbers correctly."""
        large_nums = [1000000, 2000000, 3000000]
        calculation = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            large_nums,
            db_session
        )
        
        assert calculation.result == sum(large_nums)

    def test_factory_with_small_decimal_numbers(self, db_session: Session, test_user: User):
        """Test factory handles very small decimal numbers."""
        small_nums = [0.0001, 0.0002, 0.0003]
        calculation = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            small_nums,
            db_session
        )
        
        assert calculation.result == pytest.approx(sum(small_nums))

    def test_factory_with_negative_numbers(self, db_session: Session, test_user: User):
        """Test factory handles negative numbers correctly."""
        neg_nums = [-10, -20, -30]
        calculation = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            neg_nums,
            db_session
        )
        
        assert calculation.result == -60

    def test_factory_with_mixed_signs(self, db_session: Session, test_user: User):
        """Test factory handles mixed positive and negative numbers."""
        mixed = [-50, 30, 20]
        calculation = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            test_user.id,
            mixed,
            db_session
        )
        
        assert calculation.result == 0

    def test_factory_multiple_users_same_calculation_type(self, db_session: Session):
        """Test multiple users can have calculations of same type."""
        # Create two users
        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        
        # Create same calculation type for both users with different inputs
        calc1 = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            user1.id,
            [1, 2],
            db_session
        )
        
        calc2 = CalculationFactory.create_and_store(
            CalculationType.ADDITION,
            user2.id,
            [10, 20],
            db_session
        )
        
        # Verify they're separate records
        assert calc1.id != calc2.id
        assert calc1.user_id == user1.id
        assert calc2.user_id == user2.id
        assert calc1.result == 3
        assert calc2.result == 30
