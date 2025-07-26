"""
SkypoukLogger - A customized rotational logger with monthly archiving.

This package provides a logger that prints logs to console and stores them in a
separate logs folder into monthly log files with a maximum size of 512 MB.
When max size is reached, a new file with suffix ".1" is created. At the start
of every month, the previous month logs are merged and zipped into a
logs_month_year.log.gz file.
"""

from .logger import SkypoukLogger, SkypoukLoggerError

__version__ = "0.1.0"
__author__ = "Achraf Bentaher"
__email__ = "achraf.bentaher.ing@gmail.com"
__all__ = ["SkypoukLogger"]