from datetime import datetime


def log_task(task_name, status):
    """
    Logs the task with status (STARTED or COMPLETED) and current timestamp.
    """
    with open("task_log.txt", "a") as file:
        file.write("\n--------------------------------\n")
        file.write(f"Task: {task_name}\n")
        file.write(f"Status: {status}\n")
        file.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write("--------------------------------\n")


# # Example usage:
# log_task("Data Backup", "STARTED")
# log_task("Data Backup", "COMPLETED")
# log_task("Model Training", "STARTED")
# log_task("Model Training", "COMPLETED")
