import uuid

def process_payment(payment_details):
    """
    Process payment details.
    Args:
        payment_details (dict): Payment information.
    Returns:
        dict: Payment status and transaction ID.
    """
    try:
        print(f"Processing payment for {payment_details}")
        transaction_id = f"TX-{uuid.uuid4().hex[:8]}"
        return {"status": "success", "transaction_id": transaction_id}
    except Exception as e:
        print(f"Payment failed: {str(e)}")
        return {"status": "failure", "message": str(e)}
