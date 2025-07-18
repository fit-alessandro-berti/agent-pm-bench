import os
import json

from evaluation import *

import math


def extract_pairwise_results():
    RESULTS = {}

    for file_name in os.listdir(EVALUATION_FOLDER):
        file_path = os.path.join(EVALUATION_FOLDER, file_name)

        if os.path.getsize(file_path) > 0:
            data = file_name.split("__")[0]
            model1 = file_name.split("__")[1]
            model2 = file_name.split("__")[2].split(".")[0]

            if data not in RESULTS:
                RESULTS[data] = {}

            if model1 not in RESULTS[data]:
                RESULTS[data][model1] = {}

            if model2 not in RESULTS[data]:
                RESULTS[data][model2] = {}

            content = json.loads(read_contents(file_path))

            RESULTS[data][model1][model2] = [content[0], content[1]]
            RESULTS[data][model2][model1] = [content[1], content[0]]

    return RESULTS


def compute_elo_for_dataset(pairwise_results,
                            initial_rating=1000,
                            K=32,
                            iterations=50):
    """
    pairwise_results: { modelA: { modelB: [scoreA, scoreB], ... }, ... }
    Returns: { model: rating }
    """
    # initialize
    ratings = {m: initial_rating for m in pairwise_results}
    # do multiple sweeps for stability
    for _ in range(iterations):
        for A, opponents in pairwise_results.items():
            for B, (sA, sB) in opponents.items():
                # only process each unordered pair once
                if A >= B:
                    continue
                # actual score fraction
                SA = sA / (sA + sB)
                SB = 1 - SA
                RA = ratings[A]
                RB = ratings[B]
                EA = 1 / (1 + 10 ** ((RB - RA) / 400))
                EB = 1 - EA
                # update
                ratings[A] = RA + K * (SA - EA)
                ratings[B] = RB + K * (SB - EB)
    return ratings


if __name__ == "__main__":
    pairwise_results = extract_pairwise_results()
    ELO = {}

    for data, models in pairwise_results.items():
        ELO[data] = compute_elo_for_dataset(models)

    print(ELO)
