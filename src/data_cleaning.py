import pandas as pd

def clean_dataset(file_path, label_value):
    # Load dataset safely
    df = pd.read_csv(
        file_path,
        sep="\t",
        encoding="latin1",
        on_bad_lines='skip',
        low_memory=False
    )

    print(f"\n Original shape ({file_path}):", df.shape)

    #  Remove all junk unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    print(" After removing unnamed columns:", df.shape)

    #  Try to detect columns automatically
    possible_title = [col for col in df.columns if "title" in col.lower()]
    possible_text = [col for col in df.columns if "text" in col.lower()]

    #  Fallback if detection fails
    if not possible_title or not possible_text:
        print("⚠️ Auto-detection failed, using first two columns...")
        df = df.iloc[:, :2]
        df.columns = ["title", "text"]
    else:
        df = df[[possible_title[0], possible_text[0]]]
        df.columns = ["title", "text"]

    #  Clean text fields
    df["title"] = df["title"].astype(str).str.strip()
    df["text"] = df["text"].astype(str).str.strip()

    #  Remove empty or invalid rows
    df = df.dropna()
    df = df[df["text"].str.len() > 20]   # less aggressive
    df = df[df["title"].str.len() > 5]

    #  Remove duplicates
    df = df.drop_duplicates(subset=["title", "text"])

    #  Add label
    df["label"] = label_value

    print(f" Cleaned shape ({file_path}):", df.shape)

    return df


def main():
    fake = clean_dataset("data/Fake.csv", 0)
    true = clean_dataset("data/True.csv", 1)

    if fake is None or true is None:
        print(" Error in dataset cleaning.")
        return

    #  Balance dataset (VERY IMPORTANT)
    min_size = min(len(fake), len(true))
    fake = fake.sample(min_size, random_state=42)
    true = true.sample(min_size, random_state=42)

    print(f"\n Balanced to: {min_size} each")

    #  Combine
    data = pd.concat([fake, true], axis=0)

    #  Shuffle
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)

    print(" Final dataset shape:", data.shape)
    print("\nLabel distribution:\n", data["label"].value_counts())

    #  Save
    data.to_csv("data/cleaned_data.csv", index=False)

    print(" Clean dataset saved to data/cleaned_data.csv")


if __name__ == "__main__":
    main()
