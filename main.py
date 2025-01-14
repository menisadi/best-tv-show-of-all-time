import pandas as pd
import argparse
from pathlib import Path
from rich.console import Console


def process_file(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()
    data = []
    for line in lines:
        if ". " in line:  # Match lines like "1. Show Name"
            rank, title = line.strip().split(". ", 1)
            data.append((int(rank), title))
    return pd.DataFrame(data, columns=["Rank", "Title"])


def main(top_k):
    cons = Console()
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

    combined_df["Title"] = combined_df["Title"].str.title()
    weighted_score_df["Title"] = weighted_score_df["Title"].str.title()

    cons.print("Most Consensus", style="red bold")
    cons.print(consensus_df.head(top_k).reset_index(drop=True))
    cons.print("Weighted Score", style="red bold")
    cons.print(weighted_score_df.head(top_k).reset_index(drop=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and rank shows.")
    parser.add_argument(
        "-k",
        "--top_k",
        type=int,
        default=10,
        help="Number of top results to display (default: 10)",
    )
    args = parser.parse_args()

    main(top_k=args.top_k)
