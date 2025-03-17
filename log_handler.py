def logger(message: str, type_log: str = "LOGS"):
    log_message = f"[{type_log}] {message}"
    print(log_message)
    with open("logs.log",'a') as f:
        f.write(log_message + "\n")

