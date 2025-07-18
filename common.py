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

    def __init__(self, file_path, prompt, model):
        super().__init__()
        self.file_path = file_path
        self.prompt = prompt
        self.model = model

    def run(self):
        # Acquire the lock immediately at the start of the thread
        PerformPromptThread._input_lock.acquire()
        try:
            # Determine the answer file name
            base = os.path.basename(self.file_path)
            name, _ = os.path.splitext(base)
            answer_filename = f"{name}__{self.model}.txt"
            answer_path = os.path.join("answers", answer_filename)

            # Make sure the answers directory exists
            os.makedirs(os.path.dirname(answer_path), exist_ok=True)

            # If the file doesn't exist or is empty, create it and prompt
            if not os.path.exists(answer_path) or os.path.getsize(answer_path) == 0:
                # Create an empty file
                with open(answer_path, "w"):
                    pass

                # Copy the prompt to the clipboard
                pyperclip.copy(self.prompt)

                # Wait for user to press Enter
                input("-> ")
        finally:
            # Release the lock immediately after input()
            PerformPromptThread._input_lock.release()

        # Open the answer file in Notepad (outside the lock)
        subprocess.run(["notepad.exe", answer_path])


if __name__ == "__main__":
    t = PerformPromptThread("data/ccc19.csv", "ciao", "o3")
    t.start()
    t.join()
