
import hashlib
import hmac
import logging

from src.config import settings

logger = logging.getLogger(__name__)


def verify_webhook_signature(
    payload: bytes,
    signature_header: str
) -> bool:
    """
    Verify the HMAC SHA-256 signature from Meta's webhook payload.

    Meta sends an X-Hub-Signature-256 header with each webhook
    POST request. This function checks whether the payload
    genuinely came from Meta and has not been modified.

    Args:
        payload: Raw request body bytes.
        signature_header: X-Hub-Signature-256 header value.

    Returns:
        True if the signature is valid, False otherwise.
    """

    # Do not bypass signature verification if the secret is missing.
    if not settings.WHATSAPP_SECRET:
        logger.error("WHATSAPP_SECRET is not configured")
        return False

    if not signature_header:
        logger.warning("No signature header provided")
        return False

    try:
        # Expected format: sha256=<hex_digest>
        hash_method, signature = signature_header.split("=", 1)

    except ValueError:
        logger.error("Invalid signature header format")
        return False

    if hash_method != "sha256":
        logger.error("Unexpected hash method: %s", hash_method)
        return False

    expected_signature = hmac.new(
        key=settings.WHATSAPP_SECRET.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    is_valid = hmac.compare_digest(
        signature,
        expected_signature
    )

    if not is_valid:
        logger.warning("Webhook signature verification failed")

    return is_valid
