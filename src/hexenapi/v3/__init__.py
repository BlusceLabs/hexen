"""
### v3 - Backwards compatibility shim
All v3 functionality has been moved to hexenapi.v2.
This module re-exports everything for backwards compatibility.
"""

import logging

logger = logging.getLogger(__name__)

from hexenapi.v2.http_client import MovieBoxHttpClient  # noqa: F401
from hexenapi.v2.crypto import *  # noqa: F401, F403
from hexenapi.v2.urls import *  # noqa: F401, F403
