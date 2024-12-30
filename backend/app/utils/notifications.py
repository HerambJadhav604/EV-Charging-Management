def send_notification(user, message):
    """
    Send a notification to a user.
    Args:
        user (str): User identifier.
        message (str): Notification message.
    """
    try:
        print(f"Notification sent to {user}: {message}")
        return {"status": "success", "message": "Notification sent successfully"}
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")
        return {"status": "failure", "message": str(e)}
