"""Minifiers extension."""

from gena.contrib.minifiers.processors import HTMLMinifierProcessor
from gena.contrib.minifiers.shortcuts import html_minifier


__all__ = (
    'html_minifier',
    'HTMLMinifierProcessor',
)
