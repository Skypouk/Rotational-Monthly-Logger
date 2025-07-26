# SkypoukLogger

A customized rotational logger that prints logs to console and stores them in monthly log files with automatic archiving and compression.

## Features

- **Dual Output**: Logs to both console and file simultaneously
- **Monthly Rotation**: Creates monthly log files (format: `logs_MM_YYYY.log`)
- **Size-based Rotation**: Automatically rotates files when they reach 512 MB
- **Automatic Archiving**: At the start of each month, previous month's logs are merged and compressed into `.gz` files
- **Clean Management**: Removes original files after successful archiving
- **Type Safety**: Full type hints for better IDE support and code reliability
- **Exception Handling**: Custom exceptions for better error management

## Installation

```bash
pip install date-aware-logger
```

## Quick Start

```python
from dateawarelogger import SkypoukLogger

# Initialize the logger
logger = SkypoukLogger()

# Log messages at different levels
logger.info("Application started")
logger.debug("Debug information")
logger.warning("This is a warning")
logger.error("An error occurred")
logger.critical("Critical system failure")
```

## Advanced Usage

### Custom Log Directory

```python
from dateawarelogger import SkypoukLogger

# Use a custom directory for logs
logger = SkypoukLogger(log_directory="custom_logs")
logger.info("Logging to custom directory")
```

### Error Handling

```python
from dateawarelogger import SkypoukLogger, SkypoukLoggerError

try:
    logger = SkypoukLogger()
    logger.info("This works fine")
except SkypoukLoggerError as e:
    print(f"Logger error: {e}")
    if e.original_exception:
        print(f"Original cause: {e.original_exception}")
```

## How It Works

### File Structure

The logger creates the following structure:

```
logs/
├── logs_01_2024.log          # Current month's log file
├── logs_01_2024.log.1        # Rotated file (when size limit reached)
├── logs_12_2023.log.gz       # Previous month's compressed archive
└── logs_11_2023.log.gz       # Earlier month's compressed archive
```

### Rotation Logic

1. **Size-based Rotation**: When a log file reaches 512 MB, it's rotated (renamed with `.1`, `.2`, etc. suffix)
2. **Monthly Archiving**: At the start of each month:
   - All log files from the previous month are merged
   - The merged file is compressed into a `.gz` archive
   - Original uncompressed files are removed
3. **Backup Count**: Maintains up to 10 rotated files per month

### Log Format

Each log entry follows this format:
```
2024-01-15 10:30:45,123 - INFO - Your log message here
2024-01-15 10:30:46,124 - ERROR - Error message here
```

## API Reference

### SkypoukLogger

#### `__init__(log_directory: str = "logs")`

Initialize the logger.

**Parameters:**
- `log_directory` (str): Directory where log files will be stored. Defaults to "logs".

#### Logging Methods

- `debug(message: str)`: Log a debug message
- `info(message: str)`: Log an info message
- `warning(message: str)`: Log a warning message
- `error(message: str)`: Log an error message
- `critical(message: str)`: Log a critical message

### SkypoukLoggerError

Custom exception class for logger-related errors.

**Attributes:**
- `original_exception`: The original exception that caused this error (if any)

## Requirements

- Python 3.7+
- No external dependencies (uses only Python standard library)

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/Skypouk/Rotational-Monthly-Logger.git
cd skypouk-logger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=dateawarelogger --cov-report=html
```

### Code Quality

```bash
# Format code
black dateawarelogger tests

# Lint code
flake8 dateawarelogger tests

# Type checking
mypy dateawarelogger
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass and code is properly formatted
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.1.0
- Initial release
- Basic rotational logging functionality
- Monthly archiving and compression
- Console and file output
- Type hints and comprehensive documentation

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Skypouk/Rotational-Monthly-Logger/issues) on GitHub.