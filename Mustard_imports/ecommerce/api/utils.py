from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
import logging
import re

logger = logging.getLogger(__name__)

# Pagination Constants
MAX_RECENT_ITEMS = 5
MAX_DASHBOARD_ITEMS = 5


def invalidate_order_caches(user_id, order_id):
    """
    Invalidate cached order data for a specific user and order.

    Args:
        user_id: ID of the user whose cache to invalidate
        order_id: ID of the specific order to invalidate
    """
    cache_keys = [
        f'user_orders_{user_id}',
        f'user_order_{user_id}_{order_id}',
        f'completed_orders_{user_id}',
        f'completed_order_{user_id}_{order_id}',
    ]

    for key in cache_keys:
        try:
            cache.delete(key)
            logger.debug(f"Invalidated cache key: {key}")
        except (InvalidCacheBackendError, Exception) as e:
            logger.error(f"Failed to invalidate cache key {key}: {e}")


def format_phone_number(phone_number):
    """
    Format phone number to Kenyan format (254xxxxxxxxx).

    Args:
        phone_number: Phone number string to format

    Returns:
        Formatted phone number string

    Raises:
        ValueError: If phone number format is invalid
    """
    logger.info(f"Formatting phone number: {phone_number}")
    phone_number = phone_number.replace("+", "")

    if re.match(r"^254\d{9}$", phone_number):
        logger.info(f"Phone number already in 254 format: {phone_number}")
        return phone_number
    elif phone_number.startswith("0") and len(phone_number) == 10:
        formatted_number = "254" + phone_number[1:]
        logger.info(f"Converted phone number to: {formatted_number}")
        return formatted_number
    else:
        logger.error(f"Invalid phone number format: {phone_number}")
        raise ValueError("Invalid phone number format. Use 254xxxxxxxxx or 07xxxxxxxx")
