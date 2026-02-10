import pandas as pd
from datetime import datetime
from pathlib import Path

def date_matches(song_date, target_date) -> bool:
    if pd.isna(song_date):
        return False

    if isinstance(song_date, datetime):
        parsed_song_date = song_date
    else:
        # Some CSVs contain empty values (NaN) or timestamp-like strings.
        song_date_text = str(song_date).strip()
        try:
            parsed_song_date = datetime.strptime(song_date_text[:10], "%Y-%m-%d")
        except ValueError:
            return False

    return (
        target_date.year == parsed_song_date.year
        and target_date.month == parsed_song_date.month
    )
    

def handle_target_input(target_input):
    target_input = target_input.strip()
    try:
        year = int(target_input[:target_input.index("-")])
        month = int(target_input[target_input.index("-")+1:])
    except:
        raise ValueError("Failed to parse date.")

    return datetime(year, month, 1)


def filter_songs_from_csv(csv_file: Path, target_date: datetime):
    try:
        songs = pd.read_csv(csv_file)
    except pd.errors.ParserError:
        # Fall back to a more permissive parser for malformed CSV rows.
        songs = pd.read_csv(csv_file, engine="python", on_bad_lines="skip")

    required_columns = {"Release Date", "Artist Name(s)", "Track Name"}
    if not required_columns.issubset(songs.columns):
        print(f"Skipping {csv_file}: missing required columns")
        return []

    mask = songs["Release Date"].apply(lambda song: date_matches(song, target_date))
    filtered_songs = songs[mask]

    output = []
    for _, row in filtered_songs.iterrows():
        artist = row["Artist Name(s)"]
        track = row["Track Name"]
        date = row["Release Date"]
        output.append(f"{artist} - {track} ({date})")

    return output


def main():
    input_path = Path(input("Filename or directory to read songs from:\n> ").strip())

    target_input = input("Target \"YYYY-mm\":\n> ")
    target_date = handle_target_input(target_input)

    output_lines = []

    if input_path.is_dir():
        csv_files = sorted(input_path.glob("*.csv"))
        if not csv_files:
            raise ValueError(f"No CSV files found in directory: {input_path}")

        for csv_file in csv_files:
            output_lines.extend(filter_songs_from_csv(csv_file, target_date))
    else:
        output_lines.extend(filter_songs_from_csv(input_path, target_date))

    output = "\n".join(output_lines)

    filename = input("Filename to save results:\n> ")
    with open(filename, "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()
