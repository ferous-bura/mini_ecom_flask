import requests
import stripe

stripe.api_key = "your-stripe-secret-key"

def create_payment_link(amount: float, order_id: int) -> str:
    payment_link = stripe.PaymentLink.create(
        line_items=[{"price": "price_123", "quantity": 1}],  # Replace with your Stripe Price ID
        metadata={"order_id": order_id},
    )
    return payment_link.url

def generate_qr_code(payment_url: str) -> str:
    qr_api = "https://api.qrserver.com/v1/create-qr-code/"
    params = {"data": payment_url, "size": "200x200", "format": "png"}
    response = requests.get(qr_api, params=params)
    return response.url  # URL to QR code image

def check_payment_status(payment_intent: str) -> bool:
    intent = stripe.PaymentIntent.retrieve(payment_intent)
    return intent.status == "succeeded"