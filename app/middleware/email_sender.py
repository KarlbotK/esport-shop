"""Email sender — background task that sends order confirmation emails via SMTP."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def send_order_confirmation_email(
    to_email: str,
    order_id: int,
    total_amount: float,
    items: list[dict],
    smtp_host: str = "smtp.qq.com",
    smtp_port: int = 587,
    smtp_username: str = "",
    smtp_password: str = "",
):
    """Send an order confirmation email as a background task.

    This is intentionally fire-and-forget. Failures are logged but not retried.
    """
    import aiosmtplib
    from email.message import EmailMessage

    if not all([smtp_host, smtp_username, smtp_password, to_email]):
        logger.warning(f"Email config incomplete or no recipient — skipping email for order {order_id}")
        return

    # Build plain-text email body
    item_lines = "\n".join(
        f"  - {item.get('sku_name', 'SKU #' + str(item.get('sku_id', '')))} × {item.get('quantity', 1)}"
        for item in items
    )

    body = f"""Thank you for your order!

Order ID: {order_id}
Total Amount: ¥{total_amount:.2f}

Items:
{item_lines}

Your order is being processed. Estimated delivery: 3-7 business days.

Best regards,
ShopAgent Team"""

    msg = EmailMessage()
    msg["Subject"] = f"Order Confirmation - ShopAgent (#{order_id})"
    msg["From"] = smtp_username
    msg["To"] = to_email
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            start_tls=True,
            username=smtp_username,
            password=smtp_password,
        )
        logger.info(f"Order confirmation email sent for order {order_id} to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email for order {order_id}: {e}")
