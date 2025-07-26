import gzip
import shutil
import re
import os
from pathlib import Path
import logging.handlers
from datetime import datetime
from typing import Set, Tuple, List, Optional


class SkypoukLoggerError(Exception):
    """Custom Exception for SkypoukLogger class.

    Args:
        message (str): The error message.
        original_exception (Exception, optional): The original exception that caused this error.
    """

    def __init__(self, message: str, original_exception: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.original_exception = original_exception


class SkypoukLogger:
    """
    A customized rotational logger that prints logs to console and stores them in monthly files.

    Features:
    - Logs to both console and file
    - Monthly log files with maximum size of 512 MB
    - Automatic rotation when max size is reached
    - Monthly archiving of previous month's logs into compressed .gz files
    - Automatic cleanup of old log files after archiving

    Attributes:
        logger (logging.Logger): The underlying Python logger instance.
        log_directory (Path): Directory where log files are stored.

    Example:
        >>> logger = SkypoukLogger()
        >>> logger.info("This is an info message")
        >>> logger.error("This is an error message")
    """

    def __init__(self, log_directory: str = "logs") -> None:
        """
        Initialize the SkypoukLogger.

        Args:
            log_directory (str): Directory path where log files will be stored.
                                Defaults to "logs".
        """
        self.logger: Optional[logging.Logger] = None
        self.log_directory: Path = Path(log_directory)
        self.setup_logger()

    def setup_logger(self) -> None:
        """
        Set up the logger with file and console handlers.

        Creates the log directory if it doesn't exist and configures both
        file and console handlers with appropriate formatting.

        Raises:
            SkypoukLoggerError: If there's an error setting up the logger.
        """
        try:
            if not os.path.exists(self.log_directory):
                os.makedirs(self.log_directory)

            base_filename = self._get_log_filename()
            file_handler = logging.handlers.RotatingFileHandler(
                base_filename, maxBytes=512 * 1024 * 1024, backupCount=10
            )
            console_handler = logging.StreamHandler()

            self.logger = logging.getLogger("skypouk_logger")
            self.logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Clear existing handlers to avoid duplicates
            self.logger.handlers = []
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        except Exception as e:
            raise SkypoukLoggerError(f"Failed to setup logger: {str(e)}", e)

    def log(self, log_level: str, message: str) -> None:
        """
        Log a message at the specified level.

        Before logging, checks if there are previous month's logs that need
        to be archived and compressed.

        Args:
            log_level (str): The logging level (debug, info, warning, error, critical).
            message (str): The message to log.

        Raises:
            SkypoukLoggerError: If there's an error during logging or archiving.
        """
        try:
            current_date = datetime.now()

            # Check for logs from previous months that need to be zipped
            to_zip_dates = self._get_month_year_unzipped_logs()
            for last_log_month, last_log_year in to_zip_dates:
                if (
                    current_date.month != last_log_month
                    or current_date.year != last_log_year
                ):
                    self._merge_and_zip_log_files(last_log_month, last_log_year)

            # Log the message
            if self.logger is None:
                raise SkypoukLoggerError("Logger is not initialized")

            getattr(self.logger, log_level)(message)

        except AttributeError:
            raise SkypoukLoggerError(f"Invalid log level: {log_level}")
        except Exception as e:
            raise SkypoukLoggerError(f"Failed to log message: {str(e)}", e)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.log("debug", message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.log("info", message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.log("warning", message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.log("error", message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self.log("critical", message)

    def _get_log_filename(self) -> Path:
        """
        Get the current log filename based on current month and year.

        Returns:
            Path: The path to the current month's log file.
        """
        current_date = datetime.now()
        return self.log_directory / f"logs_{current_date.strftime('%m_%Y')}.log"

    def _get_month_year_str(self, month: int, year: int) -> str:
        """
        Format month and year into a string with zero-padded month.

        Args:
            month (int): Month number (1-12).
            year (int): Year number.

        Returns:
            str: Formatted string in format "MM_YYYY".
        """
        return f"{month:02d}_{year}"

    def _get_month_year_unzipped_logs(self) -> Set[Tuple[int, int]]:
        """
        Get all month/year combinations that have unzipped log files.

        Scans the log directory for unzipped log files from previous months
        and returns their month/year combinations.

        Returns:
            Set[Tuple[int, int]]: Set of (month, year) tuples for unzipped logs
                                 from previous months.

        Raises:
            SkypoukLoggerError: If there's an error reading the log directory.
        """
        try:
            unzipped_pattern = r"logs_(\d{2})_(\d{4})\.log(\.\d+)?$"
            files = os.listdir(self.log_directory)
            ret: Set[Tuple[int, int]] = set()

            for file in files:
                match = re.match(unzipped_pattern, file)
                if match:
                    month_str, year_str = match.groups()[:2]
                    month, year = int(month_str), int(year_str)
                    current_date = datetime.now()
                    if month != current_date.month or year != current_date.year:
                        ret.add((month, year))

            return ret

        except Exception as e:
            raise SkypoukLoggerError(f"Failed to scan log directory: {str(e)}", e)

    def _merge_and_zip_log_files(self, month: int, year: int) -> None:
        """
        Merge and compress all log files from a specific month/year.

        Combines all log files (including rotated ones) from the specified
        month/year into a single compressed .gz file, then removes the
        original files.

        Args:
            month (int): Month number (1-12).
            year (int): Year number.

        Raises:
            SkypoukLoggerError: If there's an error during merging or compression.
        """
        try:
            month_year_str = self._get_month_year_str(month, year)
            files_to_merge: List[str] = [
                f for f in os.listdir(self.log_directory)
                if month_year_str in f and not f.endswith('.gz')
            ]

            if not files_to_merge:
                return

            base_name = f"logs_{month_year_str}.log"
            merged_filename = self.log_directory / f"{base_name}.merged"

            # Merge all files
            with open(merged_filename, "wb") as merged_file:
                for file in files_to_merge:
                    file_path = self.log_directory / file
                    with open(file_path, "rb") as f:
                        shutil.copyfileobj(f, merged_file)

            # Compress the merged file
            gz_filename = self.log_directory / f"{base_name}.gz"
            with open(merged_filename, "rb") as f_in:
                with gzip.open(gz_filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Clean up
            os.remove(merged_filename)
            for file in files_to_merge:
                file_path = self.log_directory / file
                if file_path.exists():
                    os.remove(file_path)

        except Exception as e:
            raise SkypoukLoggerError(
                f"Failed to merge and zip log files for {month}/{year}: {str(e)}", e
            )