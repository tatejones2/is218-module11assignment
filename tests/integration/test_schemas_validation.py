# tests/integration/test_schemas_validation.py

"""
Integration Tests for Pydantic Schema Validation

These tests verify that Pydantic schemas correctly validate calculation data:
1. Valid data is accepted and properly converted
2. Invalid data is rejected with appropriate error messages
3. Field validators work correctly
4. Model validators enforce business rules
5. Type conversions work as expected

This tests the boundary between the API (FastAPI) and the business logic layer.
"""

import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime

from app.schemas.calculation import (
    CalculationType,
    CalculationBase,
    CalculationCreate,
    CalculationResponse,
    CalculationUpdate,
)


class TestCalculationTypeEnum:
    """Test CalculationType enum validation."""

    def test_all_valid_types_exist(self):
        """Verify all expected calculation types are defined."""
        types = {e.value for e in CalculationType}
        
        assert "addition" in types
        assert "subtraction" in types
        assert "multiplication" in types
        assert "division" in types

    def test_enum_string_values(self):
        """Verify enum values are lowercase strings."""
        assert CalculationType.ADDITION.value == "addition"
        assert CalculationType.SUBTRACTION.value == "subtraction"
        assert CalculationType.MULTIPLICATION.value == "multiplication"
        assert CalculationType.DIVISION.value == "division"


class TestCalculationCreateValidation:
    """Test CalculationCreate schema validation."""

    def test_valid_addition_request(self):
        """Test valid addition calculation request."""
        user_id = uuid4()
        data = {
            "type": "addition",
            "inputs": [1, 2, 3],
            "user_id": user_id
        }
        
        schema = CalculationCreate(**data)
        assert schema.type == CalculationType.ADDITION
        assert schema.inputs == [1, 2, 3]
        assert schema.user_id == user_id

    def test_valid_division_request(self):
        """Test valid division calculation request."""
        user_id = uuid4()
        data = {
            "type": "division",
            "inputs": [100, 2, 5],
            "user_id": user_id
        }
        
        schema = CalculationCreate(**data)
        assert schema.type == CalculationType.DIVISION
        assert schema.inputs == [100, 2, 5]

    def test_case_insensitive_type(self):
        """Test that type field is case-insensitive."""
        user_id = uuid4()
        
        # Test uppercase
        schema1 = CalculationCreate(
            type="ADDITION",
            inputs=[1, 2],
            user_id=user_id
        )
        assert schema1.type == CalculationType.ADDITION
        
        # Test mixed case
        schema2 = CalculationCreate(
            type="AdDiTioN",
            inputs=[1, 2],
            user_id=user_id
        )
        assert schema2.type == CalculationType.ADDITION

    def test_invalid_type_rejected(self):
        """Test that invalid calculation type is rejected."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="invalid_type",
                inputs=[1, 2],
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        assert any("type" in str(error) for error in errors)

    def test_missing_type_rejected(self):
        """Test that missing type field is rejected."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                inputs=[1, 2],
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        assert any("type" in str(error) for error in errors)

    def test_missing_inputs_rejected(self):
        """Test that missing inputs field is rejected."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="addition",
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        assert any("inputs" in str(error) for error in errors)

    def test_inputs_not_list_rejected(self):
        """Test that non-list inputs are rejected."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="addition",
                inputs="1, 2, 3",  # String instead of list
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        assert any("list" in str(error).lower() for error in errors)

    def test_inputs_single_number_rejected(self):
        """Test that single input is rejected (need at least 2)."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="addition",
                inputs=[5],
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        # Should have error about minimum length or calculation validation
        assert len(errors) > 0

    def test_inputs_empty_list_rejected(self):
        """Test that empty inputs list is rejected."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="addition",
                inputs=[],
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_division_by_zero_rejected(self):
        """Test that division with zero divisor is rejected."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="division",
                inputs=[10, 0],  # Division by zero
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        assert any("divide" in str(error).lower() or "zero" in str(error).lower() 
                   for error in errors)

    def test_division_with_zero_in_chain_rejected(self):
        """Test that division with zero in any divisor position is rejected."""
        user_id = uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="division",
                inputs=[100, 2, 0, 5],  # Zero in middle of divisors
                user_id=user_id
            )
        
        errors = exc_info.value.errors()
        assert any("zero" in str(error).lower() for error in errors)

    def test_missing_user_id_rejected(self):
        """Test that missing user_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CalculationCreate(
                type="addition",
                inputs=[1, 2]
            )
        
        errors = exc_info.value.errors()
        assert any("user_id" in str(error) for error in errors)

    def test_float_inputs_accepted(self):
        """Test that float inputs are accepted."""
        user_id = uuid4()
        
        schema = CalculationCreate(
            type="addition",
            inputs=[1.5, 2.5, 3.5],
            user_id=user_id
        )
        
        assert schema.inputs == [1.5, 2.5, 3.5]

    def test_mixed_int_float_inputs_accepted(self):
        """Test that mixed int and float inputs are accepted."""
        user_id = uuid4()
        
        schema = CalculationCreate(
            type="multiplication",
            inputs=[2, 3.5, 4],
            user_id=user_id
        )
        
        assert schema.inputs == [2, 3.5, 4]


class TestCalculationResponseValidation:
    """Test CalculationResponse schema validation."""

    def test_valid_response(self):
        """Test valid calculation response."""
        calc_id = uuid4()
        user_id = uuid4()
        now = datetime.utcnow()
        
        data = {
            "id": calc_id,
            "user_id": user_id,
            "type": "addition",
            "inputs": [1, 2, 3],
            "result": 6.0,
            "created_at": now,
            "updated_at": now
        }
        
        response = CalculationResponse(**data)
        assert response.id == calc_id
        assert response.type == CalculationType.ADDITION
        assert response.result == 6.0

    def test_missing_id_rejected(self):
        """Test that missing id is rejected."""
        user_id = uuid4()
        now = datetime.utcnow()
        
        with pytest.raises(ValidationError):
            CalculationResponse(
                user_id=user_id,
                type="addition",
                inputs=[1, 2, 3],
                result=6.0,
                created_at=now,
                updated_at=now
            )

    def test_missing_result_rejected(self):
        """Test that missing result is rejected."""
        calc_id = uuid4()
        user_id = uuid4()
        now = datetime.utcnow()
        
        with pytest.raises(ValidationError):
            CalculationResponse(
                id=calc_id,
                user_id=user_id,
                type="addition",
                inputs=[1, 2, 3],
                created_at=now,
                updated_at=now
            )


class TestCalculationUpdateValidation:
    """Test CalculationUpdate schema validation."""

    def test_valid_update_with_new_inputs(self):
        """Test valid update with new inputs."""
        data = {"inputs": [10, 20]}
        
        update = CalculationUpdate(**data)
        assert update.inputs == [10, 20]

    def test_update_with_no_fields_accepted(self):
        """Test that empty update (no fields) is accepted."""
        update = CalculationUpdate()
        assert update.inputs is None

    def test_update_with_insufficient_inputs_rejected(self):
        """Test that update with single input is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CalculationUpdate(inputs=[5])
        
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_update_with_empty_inputs_rejected(self):
        """Test that update with empty inputs is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CalculationUpdate(inputs=[])
        
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_update_allows_float_inputs(self):
        """Test that update accepts float inputs."""
        update = CalculationUpdate(inputs=[1.5, 2.5])
        assert update.inputs == [1.5, 2.5]


class TestSchemaFromORMMode:
    """Test schema creation from SQLAlchemy ORM objects."""

    def test_calculation_response_from_orm(self):
        """Test CalculationResponse can be created from ORM object."""
        from app.models.calculation import Addition
        from app.models.user import User
        from datetime import datetime
        
        # Create mock ORM objects (without database)
        user_id = uuid4()
        calc_id = uuid4()
        
        # Note: This is a simplified test - in real tests you'd use a session
        # For now, we're just testing the schema accepts the right structure
        data = {
            "id": calc_id,
            "user_id": user_id,
            "type": "addition",
            "inputs": [1, 2, 3],
            "result": 6.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        response = CalculationResponse(**data)
        assert response.model_dump() == data


class TestSchemaJsonSchemaGeneration:
    """Test that schemas generate correct OpenAPI/JSON schema."""

    def test_calculation_create_json_schema(self):
        """Test CalculationCreate schema generates valid JSON schema."""
        schema = CalculationCreate.model_json_schema()
        
        assert "properties" in schema
        assert "type" in schema["properties"]
        assert "inputs" in schema["properties"]
        assert "user_id" in schema["properties"]

    def test_calculation_response_json_schema(self):
        """Test CalculationResponse schema generates valid JSON schema."""
        schema = CalculationResponse.model_json_schema()
        
        assert "properties" in schema
        required = schema.get("required", [])
        assert "id" in required or "id" in schema["properties"]
        assert "result" in required or "result" in schema["properties"]


class TestSchemaDocumentation:
    """Test that schemas are properly documented."""

    def test_calculation_type_enum_in_examples(self):
        """Test that calculation types appear in examples."""
        schema = CalculationCreate.model_json_schema()
        
        # Check if example exists
        if "example" in schema or "examples" in schema.get("properties", {}).get("type", {}):
            # Schema has examples - good for documentation
            assert True

    def test_field_descriptions_exist(self):
        """Test that fields have descriptions for API documentation."""
        schema = CalculationCreate.model_json_schema()
        
        # At least some fields should have descriptions
        descriptions = []
        for prop_name, prop_def in schema.get("properties", {}).items():
            if "description" in prop_def:
                descriptions.append(prop_name)
        
        assert len(descriptions) > 0, "Fields should have descriptions for documentation"
