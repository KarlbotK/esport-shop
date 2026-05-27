"""Background order processing (replaces Kafka consumers)."""

import logging

logger = logging.getLogger(__name__)


# Order processing is primarily synchronous in this simplified version.
# Email sending is handled as async background tasks in the order service.
# This module exists for future async order processing needs.
