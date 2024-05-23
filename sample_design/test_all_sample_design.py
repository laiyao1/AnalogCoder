import os
import subprocess
import sys

def work():
    failed_tasks = []
    for task_id in range(1, 25):
        file_path = os.path.join(f"p{task_id}.py")
        result = subprocess.run(['python', file_path], capture_output=True)
        if result.returncode == 0:
            print(f"Task {task_id} passed.")
        else:
            print(f"Task {task_id} failed.")
            failed_tasks.append(task_id)
    
    if len(failed_tasks) > 0:
        print(f"Failed tasks: {failed_tasks}")
        print(f"Please check your environment and try again.")
        sys.exit(1)
    else:
        print("All tasks passed.")
        sys.exit(0)

def main():
    work()


if __name__ == "__main__":
    main()