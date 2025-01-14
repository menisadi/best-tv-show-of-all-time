import pandas as pd
from pathlib import Path


def process_file(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()
    data = []
    for line in lines:
        if ". " in line:  # Match lines like "1. Show Name"
            rank, title = line.strip().split(". ", 1)
            data.append((int(rank), title))
    return pd.DataFrame(data, columns=["Rank", "Title"])


if __name__ == "__main__":
    ranks_folder = "./sourcses/"
    text_files = [ranks_folder + f.name for f in list(Path(ranks_folder).glob("*.txt"))]
    all_data = []
    for file in text_files:
        df = process_file(file)
        df["Source"] = file.split("/")[-1]  # Add source column for reference
        all_data.append(df)

    combined_df = pd.concat(all_data, ignore_index=True)

    combined_df["Title"] = combined_df["Title"].str.lower().str.strip()

    # Most Consensus: Count occurrences of each show
    consensus_df = combined_df.groupby("Title").size().reset_index(name="Count")
    consensus_df = consensus_df.sort_values(
        by=["Count", "Title"], ascending=[False, True]
    )

    # Weighted Score: Assign 1/Rank as weight and sum scores
    combined_df["WeightedScore"] = 1 / combined_df["Rank"]
    weighted_score_df = (
        combined_df.groupby("Title")["WeightedScore"].sum().reset_index()
    )
    weighted_score_df = weighted_score_df.sort_values(
        by="WeightedScore", ascending=False
    )

    print(consensus_df.head())
    print(weighted_score_df.head())
