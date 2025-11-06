"""Tests for category queue error handling paths."""

import pytest
from unittest.mock import patch, Mock
from mcp_server_guide.queue.category_queue import (
    get_next_category,
    add_category,
    get_queue,
)


class TestCategoryQueueErrorPaths:
    """Test category queue error handling."""

    @patch("mcp_server_guide.queue.category_queue.get_queue")
    def test_get_next_category_queue_exception(self, mock_get_queue):
        """Test get_next_category when queue raises exception."""
        mock_queue = Mock()
        mock_queue.get_nowait.side_effect = Exception("Queue error")
        mock_get_queue.return_value = mock_queue

        # Should return None when exception occurs
        result = get_next_category()
        assert result is None

    @patch("mcp_server_guide.queue.category_queue.get_queue")
    def test_get_next_category_empty_queue(self, mock_get_queue):
        """Test get_next_category when queue is empty."""
        import queue

        mock_queue = Mock()
        mock_queue.get_nowait.side_effect = queue.Empty()
        mock_get_queue.return_value = mock_queue

        # Should return None when queue is empty
        result = get_next_category()
        assert result is None

    @patch("mcp_server_guide.queue.category_queue.get_queue")
    def test_add_category_queue_exception(self, mock_get_queue):
        """Test add_category when queue raises exception."""
        mock_queue = Mock()
        mock_queue.put_nowait.side_effect = Exception("Queue full")
        mock_get_queue.return_value = mock_queue

        # Should handle exception gracefully
        try:
            add_category("test_category")
            # If no exception raised, test passes
        except Exception:
            pytest.fail("add_category should handle queue exceptions gracefully")

    def test_get_queue_initialization(self):
        """Test queue initialization."""
        queue_instance = get_queue()
        assert queue_instance is not None

        # Should return same instance on subsequent calls
        queue_instance2 = get_queue()
        assert queue_instance is queue_instance2
