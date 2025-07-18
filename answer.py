from common import *


ANSWERING_MODEL = "o3-pro"


if __name__ == "__main__":
    for evlog in os.listdir("data"):
        file_path = os.path.join("data", evlog)
        print(file_path)

        target_path = evlog.split(".")[0] + "__" + ANSWERING_MODEL + ".txt"
        target_path = os.path.join("answers", target_path)

        t = PerformPromptThread(target_path, "Provide a complete analytical report based on the provided process mining event log", ANSWERING_MODEL)
        t.start()
        t.join()
