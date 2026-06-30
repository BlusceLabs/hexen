"""
### v3 - Backwards compatibility shim
All v3 functionality has been moved to hexenapi.v2.
This module re-exports everything for backwards compatibility.
"""

import logging

from hexenapi.v2.crypto import *  # noqa: F403
from hexenapi.v2.http_client import MovieBoxHttpClient
from hexenapi.v2.urls import *  # noqa: F403

logger = logging.getLogger(__name__)
