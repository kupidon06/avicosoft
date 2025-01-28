import requests

class CinetPayService:
    """Service pour gérer les interactions avec l'API de CinetPay."""

    BASE_URL = "https://api-checkout.cinetpay.com/v2/payment"  # URL de base de l'API

    def __init__(self, api_key, site_id, currency="XOF"):
        self.api_key = api_key
        self.site_id = site_id
        self.currency = currency

    def initiate_payment(self, amount, transaction_id, description, return_url, notify_url):
        """Initie un paiement via CinetPay."""
        payload = {
            "apikey": self.api_key,
            "site_id": self.site_id,
            "transaction_id": transaction_id,
            "amount": int(amount),
            "currency": self.currency,
            "description": description,
            "return_url": return_url,
            "notify_url": notify_url,
            "channels": "ALL",
        }
        response = requests.post(self.BASE_URL, json=payload)
        if response.status_code != 200:
            raise Exception(f"Erreur CinetPay: {response.json()}")
        return response.json()
