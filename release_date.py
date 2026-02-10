import pandas as pd
from datetime import datetime

target_date = "2007-01-10"

def date_matches(song_date, target_date) -> bool:
    try:
        song_date = datetime.strptime(song_date, "%Y-%m-%d")
    except ValueError:
        return False

    return target_date.year == song_date.year and target_date.month == song_date.month
    

def handle_target_input(target_input):
    target_input.strip()
    try:
        year = int(target_input[:target_input.index("-")])
        month = int(target_input[target_input.index("-")+1:])
    except:
        raise ValueError("Failed to parse date.")

    return datetime(year, month, 1)


def main():
    infile = input("Filename to read songs from:\n> ")
    songs = pd.read_csv(infile)

    target_input = input("Target \"YYYY-mm\":\n> ")
    target_date = handle_target_input(target_input)


    mask = songs["Release Date"].apply(lambda song: date_matches(song, target_date))
    filtered_songs = songs[mask]

    output = []
    for index, row in filtered_songs.iterrows():
        artist = row["Artist Name(s)"]
        track = row["Track Name"]
        date = row["Release Date"]
        
        output.append(f"{artist} - {track} ({date})")

    output = "\n".join(output)

    filename = input("Filename to save results:\n> ")
    with open(filename, "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()