"""
Tests for SkypoukLogger
"""

import os
import gzip
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytest

from dateawarelogger import SkypoukLogger, SkypoukLoggerError


class TestSkypoukLogger:
    """Test cases for SkypoukLogger class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.logger = SkypoukLogger(log_directory=self.test_dir)

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_logger_initialization(self):
        """Test that logger initializes correctly."""
        assert self.logger.logger is not None
        assert self.logger.log_directory == Path(self.test_dir)
        assert os.path.exists(self.test_dir)

    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist."""
        new_dir = os.path.join(tempfile.gettempdir(), "test_logs_new")
        if os.path.exists(new_dir):
            shutil.rmtree(new_dir)

        logger = SkypoukLogger(log_directory=new_dir)
        assert os.path.exists(new_dir)

        # Cleanup
        shutil.rmtree(new_dir)

    def test_logging_methods(self):
        """Test all logging methods work correctly."""
        test_message = "Test message"

        # Test each logging method
        self.logger.debug(test_message)
        self.logger.info(test_message)
        self.logger.warning(test_message)
        self.logger.error(test_message)
        self.logger.critical(test_message)

        # Check that log file was created
        current_date = datetime.now()
        expected_filename = f"logs_{current_date.strftime('%m_%Y')}.log"
        log_file_path = Path(self.test_dir) / expected_filename

        assert log_file_path.exists()

        # Check that log file contains our messages
        with open(log_file_path, 'r') as f:
            content = f.read()
            assert test_message in content
            assert "DEBUG" in content
            assert "INFO" in content
            assert "WARNING" in content
            assert "ERROR" in content
            assert "CRITICAL" in content

    def test_get_log_filename(self):
        """Test that log filename is generated correctly."""
        filename = self.logger._get_log_filename()
        current_date = datetime.now()
        expected = Path(self.test_dir) / f"logs_{current_date.strftime('%m_%Y')}.log"
        assert filename == expected

    def test_get_month_year_str(self):
        """Test month/year string formatting."""
        assert self.logger._get_month_year_str(1, 2024) == "01_2024"
        assert self.logger._get_month_year_str(12, 2024) == "12_2024"
        assert self.logger._get_month_year_str(10, 2023) == "10_2023"

    def test_get_month_year_unzipped_logs(self):
        """Test detection of unzipped log files from previous months."""
        # Create some test log files
        current_date = datetime.now()

        # Create a file from "previous month" (simulated)
        if current_date.month == 1:
            prev_month, prev_year = 12, current_date.year - 1
        else:
            prev_month, prev_year = current_date.month - 1, current_date.year

        prev_filename = f"logs_{prev_month:02d}_{prev_year}.log"
        prev_file_path = Path(self.test_dir) / prev_filename
        prev_file_path.touch()

        # Create a rotated file from previous month
        prev_rotated_filename = f"logs_{prev_month:02d}_{prev_year}.log.1"
        prev_rotated_path = Path(self.test_dir) / prev_rotated_filename
        prev_rotated_path.touch()

        # Get unzipped logs
        unzipped_logs = self.logger._get_month_year_unzipped_logs()

        # Should contain the previous month
        assert (prev_month, prev_year) in unzipped_logs

    def test_invalid_log_level(self):
        """Test that invalid log level raises appropriate error."""
        with pytest.raises(SkypoukLoggerError) as exc_info:
            self.logger.log("invalid_level", "test message")

        assert "Invalid log level" in str(exc_info.value)

    def test_merge_and_zip_functionality(self):
        """Test the merge and zip functionality."""
        # Create some test log files for a specific month/year
        test_month, test_year = 11, 2023
        month_year_str = f"{test_month:02d}_{test_year}"

        # Create multiple log files
        log_files = [
            f"logs_{month_year_str}.log",
            f"logs_{month_year_str}.log.1",
            f"logs_{month_year_str}.log.2"
        ]

        test_content = [
            "First log file content\n",
            "Second log file content\n",
            "Third log file content\n"
        ]

        for i, filename in enumerate(log_files):
            file_path = Path(self.test_dir) / filename
            with open(file_path, 'w') as f:
                f.write(test_content[i])

        # Run merge and zip
        self.logger._merge_and_zip_log_files(test_month, test_year)

        # Check that gz file was created
        gz_filename = f"logs_{month_year_str}.log.gz"
        gz_path = Path(self.test_dir) / gz_filename
        assert gz_path.exists()

        # Check that original files were removed
        for filename in log_files:
            file_path = Path(self.test_dir) / filename
            assert not file_path.exists()

        # Check that gz file contains merged content
        with gzip.open(gz_path, 'rt') as f:
            merged_content = f.read()
            for content in test_content:
                assert content in merged_content

    def test_custom_exception_with_original(self):
        """Test SkypoukLoggerError with original exception."""
        original_error = ValueError("Original error")
        custom_error = SkypoukLoggerError("Custom message", original_error)

        assert str(custom_error) == "Custom message"
        assert custom_error.original_exception == original_error

    def test_custom_exception_without_original(self):
        """Test SkypoukLoggerError without original exception."""
        custom_error = SkypoukLoggerError("Custom message")

        assert str(custom_error) == "Custom message"
        assert custom_error.original_exception is None

    def test_logger_name(self):
        """Test that logger uses correct name."""
        assert self.logger.logger.name == "skypouk_logger"