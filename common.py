import threading
import pyperclip
import subprocess
import os


class PerformPromptThread(threading.Thread):
    """
    Threaded version of perform_prompt. Ensures that only one thread
    is prompting for input at a time: the lock is held from the start
    of run() until after input() returns.
    """
    _input_lock = threading.Lock()

    def __init__(self, target_path, prompt, model):
        super().__init__()
        self.target_path = target_path
        self.prompt = prompt
        self.model = model

    def run(self):
        # Acquire the lock immediately at the start of the thread
        PerformPromptThread._input_lock.acquire()

        # Ensure the target directory exists
        os.makedirs(os.path.dirname(self.target_path), exist_ok=True)

        # If the file doesn't exist or is empty, create it and prompt
        if not os.path.exists(self.target_path) or os.path.getsize(self.target_path) == 0:
            # Copy the prompt to the clipboard
            pyperclip.copy(self.prompt)

            # Wait for user to press Enter
            print(self.target_path, self.model)
            input("press ENTER to continue ->")

            # Release the lock immediately after input()
            PerformPromptThread._input_lock.release()

            # Open the target file in Notepad (outside the lock)
            subprocess.run(
                f'start "" notepad.exe "{self.target_path}"',
                shell=True
            )


def clear_nonempty_files(directories):
    """
    Remove every file in each of the given directories if its size is 0 bytes.
    """
    for d in directories:
        # make sure the directory actually exists
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            path = os.path.join(d, fname)
            # only consider regular files
            if os.path.isfile(path) and os.path.getsize(path) == 0:
                os.remove(path)


clear_nonempty_files(["answers", "evaluations"])

if __name__ == "__main__":
    # Example usage: provide the full path where the answer should be saved
    target = "answers/ccc19__o3.txt"
    t = PerformPromptThread(target, "ciao", "o3")
    t.start()
    t2 = PerformPromptThread(target+"2", "ciao2", "o3")
    t2.start()
    t.join()
    t2.join()
