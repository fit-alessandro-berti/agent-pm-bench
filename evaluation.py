from common import *
import os

EVALUATING_MODEL = "o3"
EVALUATION_FOLDER = "evaluation_" + EVALUATING_MODEL


def read_contents(file_path):
    try:
        # First try: default encoding
        with open(file_path, "r") as F:
            content = F.read()
    except Exception:
        # If fails, try utf-8
        with open(file_path, "r", encoding="utf-8") as F:
            content = F.read()
    return content


if __name__ == "__main__":
    models = {x.split("__")[1].split(".")[0] for x in os.listdir("answers") if os.path.getsize(os.path.join("answers", x)) > 0}
    datasets = {x.split(".")[0] for x in os.listdir("data")}
    print(models)

    for m1 in models:
        for m2 in models:
            if m1 < m2:
                for d in datasets:
                    answer1 = os.path.join("answers", d + "__" + m1 + ".txt")
                    answer2 = os.path.join("answers", d + "__" + m2 + ".txt")

                    if os.path.exists(answer1) and os.path.exists(answer2):
                        if os.path.getsize(answer1) > 0 and os.path.getsize(answer2) > 0:
                            evaluation_path = os.path.join(EVALUATION_FOLDER, d + "__" + m1 + "__" + m2 + ".txt")
                            if not os.path.exists(evaluation_path) or os.path.getsize(evaluation_path) == 0:
                                content1 = read_contents(answer1)
                                content2 = read_contents(answer2)
                                #print(evaluation_path)

                                prompt = []
                                prompt.append("(Ignore, technical ID: "+evaluation_path+")\n")

                                prompt.append("These two responses are process mining analysis reports produced on the attached process mining event log.")
                                prompt.append("Return a single JSON list (included between the ```json and ``` tags) containing [SCORE_FIRST_RESPONSE, SCORE_SECOND_RESPONSE], where the scores are numbers from 1.0 (worst grade) to 10.0 (best grade)")
                                prompt.append("Be very strict in the evaluation: missing aspects or wrong analyses should lead to a meaningful loss in the score.")
                                prompt.append("One of the scores should be higher than the other.")
                                prompt.append("\nRESPONSE 1:")
                                prompt.append(content1)
                                prompt.append("\nRESPONSE 2:")
                                prompt.append(content2)

                                prompt = "\n".join(prompt)

                                t = PerformPromptThread(evaluation_path,
                                                        prompt,
                                                        EVALUATING_MODEL)
                                t.start()
                                t.join()
