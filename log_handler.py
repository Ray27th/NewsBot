from datetime import datetime, timedelta


def logger(message: str, type_log: str = "LOGS"):
    utc_now = datetime.utcnow()  # Get current UTC time
    sgt_now = utc_now + timedelta(hours=8)
    timestamp = sgt_now.strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    log_message = f"[{timestamp}] [{type_log}] {message}"

    print(log_message)
    with open("logs.log", "a") as f:
        f.write(log_message + "\n")
