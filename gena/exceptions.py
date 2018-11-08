"""This module contains all GenA exception classes."""

from __future__ import annotations

from typing import Optional

from gena.files import FileLike
from gena.processors import Processor


__all__ = (
    'StopProcessing',
)


class StopProcessing(Exception):
    """Stop the current file processing."""

    def __init__(self, message: str = '', processor: Optional[Processor] = None, file: Optional[FileLike] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.processor = processor
        self.file = file
