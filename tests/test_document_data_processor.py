"""Tests for document data processor."""

from src.mcp_server_guide.utils.document_data_processor import DocumentDataProcessor


class TestDocumentDataProcessor:
    """Test document data processing functionality."""

    def test_process_document_data_valid(self):
        """Test processing valid document data array."""
        data_array = ['"content1"', '"content2"', '"content3"']
        result = DocumentDataProcessor.process_document_data(data_array)

        assert len(result) == 3
        assert result[0]["index"] == 0
        assert result[0]["content"] == "content1"
        assert result[0]["length"] == 8
        assert result[0]["type"] == "text"
        assert "created_at" in result[0]

    def test_process_document_data_empty(self):
        """Test processing empty document data array."""
        result = DocumentDataProcessor.process_document_data([])
        assert result == []

    def test_create_document_data_array_valid(self):
        """Test creating document data array from content."""
        content_items = ["content1", "content2", "content3"]
        result = DocumentDataProcessor.create_document_data_array(content_items)

        assert result == ['"content1"', '"content2"', '"content3"']

    def test_create_document_data_array_empty(self):
        """Test creating document data array from empty content."""
        result = DocumentDataProcessor.create_document_data_array([])
        assert result == []

    def test_merge_document_data_both_valid(self):
        """Test merging two valid document data arrays."""
        existing_data = ['"content1"', '"content2"']
        new_data = ['"content3"', '"content4"']

        result = DocumentDataProcessor.merge_document_data(existing_data, new_data)
        expected = ['"content1"', '"content2"', '"content3"', '"content4"']

        assert result == expected

    def test_merge_document_data_existing_none(self):
        """Test merging when existing data is None."""
        new_data = ['"content1"', '"content2"']
        result = DocumentDataProcessor.merge_document_data(None, new_data)

        assert result == new_data

    def test_merge_document_data_new_empty(self):
        """Test merging when new data is empty."""
        existing_data = ['"content1"', '"content2"']
        result = DocumentDataProcessor.merge_document_data(existing_data, [])

        assert result == existing_data

    def test_validate_document_data_valid(self):
        """Test validating valid document data."""
        data_array = ['"content1"', '"content2"']
        result = DocumentDataProcessor.validate_document_data(data_array)

        assert result["valid"] is True
        assert result["item_count"] == 2
        assert result["total_length"] == 16
        assert len(result["errors"]) == 0

    def test_validate_document_data_empty(self):
        """Test validating empty document data."""
        result = DocumentDataProcessor.validate_document_data([])

        assert result["valid"] is True
        assert result["item_count"] == 0
        assert "Empty data array" in result["warnings"]

    def test_validate_document_data_invalid_json(self):
        """Test validating invalid JSON in document data."""
        data_array = ["invalid-json"]
        result = DocumentDataProcessor.validate_document_data(data_array)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "Failed to decode data array" in result["errors"][0]

    def test_validate_document_data_empty_content(self):
        """Test validating document data with empty content."""
        data_array = ['""', '"content"']
        result = DocumentDataProcessor.validate_document_data(data_array)

        assert result["valid"] is True
        assert result["item_count"] == 2
        assert "Item 0 is empty" in result["warnings"]

    def test_validate_document_data_large_content(self):
        """Test validating document data with large content."""
        large_content = "x" * 15000
        data_array = [f'"{large_content}"']
        result = DocumentDataProcessor.validate_document_data(data_array)

        assert result["valid"] is True
        assert any("Item 0 is very large" in warning for warning in result["warnings"])

    def test_extract_document_metadata_valid(self):
        """Test extracting metadata from valid document data."""
        data_array = ['"content1"', '"content2"', '""']
        result = DocumentDataProcessor.extract_document_metadata(data_array)

        assert result["item_count"] == 3
        assert result["total_length"] == 16
        assert result["average_length"] == 16 / 3
        assert result["empty_items"] == 1
        assert "processed_at" in result

    def test_extract_document_metadata_empty(self):
        """Test extracting metadata from empty document data."""
        result = DocumentDataProcessor.extract_document_metadata([])

        assert result["item_count"] == 0
        assert result["total_length"] == 0
        assert result["average_length"] == 0
        assert result["empty_items"] == 0
        assert "processed_at" in result

    def test_extract_document_metadata_invalid(self):
        """Test extracting metadata from invalid document data."""
        data_array = ["invalid-json"]
        result = DocumentDataProcessor.extract_document_metadata(data_array)

        assert "error" in result
        assert "Failed to process metadata" in result["error"]
        assert "processed_at" in result
