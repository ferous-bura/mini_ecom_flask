def create_payment_link(amount: float, order_id: int) -> str:
    return f"fake-payment-link-{order_id}"

def generate_qr_code(payment_url: str) -> str:
    return f"https://api.qrserver.com/v1/create-qr-code/?data={payment_url}&size=200x200"