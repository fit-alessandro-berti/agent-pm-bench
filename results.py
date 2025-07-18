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
            for m in (model1, model2):
                if m not in RESULTS[data]:
                    RESULTS[data][m] = {}
            content = json.loads(read_contents(file_path))
            RESULTS[data][model1][model2] = [content[0], content[1]]
            RESULTS[data][model2][model1] = [content[1], content[0]]
    return RESULTS


def compute_elo_for_dataset(pairwise_results,
                            initial_rating=1000,
                            K=32,
                            iterations=50):
    """
    pairwise_results: { modelA: { modelB: [winsA, winsB], ... }, ... }
    Returns: { model: rating }
    """
    # initialize
    ratings = {m: initial_rating for m in pairwise_results}
    for _ in range(iterations):
        for A, opponents in pairwise_results.items():
            for B, (sA, sB) in opponents.items():
                if A >= B:
                    continue
                SA = sA / (sA + sB)
                SB = 1 - SA
                RA = ratings[A]
                RB = ratings[B]
                EA = 1 / (1 + 10 ** ((RB - RA) / 400))
                EB = 1 - EA
                ratings[A] = RA + K * (SA - EA)
                ratings[B] = RB + K * (SB - EB)
    return ratings


def write_leaderboard(elo, pairwise, output_file="leaderboard.md"):
    # 1) gather datasets & models
    datasets = sorted(elo.keys())
    all_models = sorted({m for data in datasets for m in elo[data].keys()})

    # 2) compute average ELO per model
    avg_elo = {
        m: sum(elo[data].get(m, 0) for data in datasets) / len(datasets)
        for m in all_models
    }

    # 3) sort models by average descending
    sorted_models = sorted(all_models, key=lambda m: avg_elo[m], reverse=True)

    # 4) find max per column (average + each dataset)
    max_avg = max(avg_elo.values())
    max_per_dataset = {
        data: max(elo[data].values())
        for data in datasets
    }

    # 5) build markdown lines
    lines = ["## Overall ELO Leaderboard\n"]

    # -- overall leaderboard table
    header = ["Model", "Average"] + datasets
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    for m in sorted_models:
        row = []
        a = avg_elo[m]
        s_avg = f"{a:.2f}"
        if math.isclose(a, max_avg):
            s_avg = f"**{s_avg}**"
        row.append(m)
        row.append(s_avg)
        for data in datasets:
            r = elo[data].get(m, 0)
            s_r = f"{r:.2f}"
            if math.isclose(r, max_per_dataset[data]):
                s_r = f"**{s_r}**"
            row.append(s_r)
        lines.append("| " + " | ".join(row) + " |")

    # -- per-model pairwise breakdown
    for m in sorted_models:
        lines.append(f"\n### {m}\n")
        for data in datasets:
            lines.append(f"#### {data}\n")
            lines.append("| Opponent | {0} Wins | {0} Losses |".format(m))
            lines.append("| --- | --- | --- |")
            opponents = pairwise[data].get(m, {})
            for opp in sorted(opponents):
                wins, losses = opponents[opp]
                lines.append(f"| {opp} | {wins} | {losses} |")

    # 6) write out
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Leaderboard written to {output_file}")


if __name__ == "__main__":
    pairwise_results = extract_pairwise_results()
    ELO = {
        data: compute_elo_for_dataset(models)
        for data, models in pairwise_results.items()
    }
    write_leaderboard(ELO, pairwise_results)
