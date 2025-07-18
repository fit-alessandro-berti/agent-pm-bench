import os.path

from common import *


ANSWERING_MODELS = ["o4-mini", "o3", "o3-pro"]


if __name__ == "__main__":
    for evlog in os.listdir("data"):
        file_path = os.path.join("data", evlog)
        print(file_path)

        for answering_model in ANSWERING_MODELS:
            target_path = evlog.split(".")[0] + "__" + answering_model + ".txt"
            target_path = os.path.join("answers", target_path)

            if not os.path.exists(target_path):
                t = PerformPromptThread(target_path, "Provide a complete analytical report based on the provided process mining event log", answering_model)
                t.start()
                t.join()
