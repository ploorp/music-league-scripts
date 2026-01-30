import csv

def count_letters(text):
    target_letters = {'c', 'o', 'r', 'n', 'i', 's', 'h'}
    found_letters = set()
    for char in text.lower():
        if char in target_letters:
            found_letters.add(char)
    return len(found_letters)

def main():
    filename = input("enter csv filename to check: ")
    sort_length = True # sort by title length (otherwise alphabetically)
    output_filename = filename.replace('.csv', '.txt')
    matches = []
    
    with open(filename, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            track_name = row['Track Name']
            artist_name = row['Artist Name(s)']
            if count_letters(track_name) >= 6:
                matches.append((track_name, artist_name))
    
    if sort_length:
        unique_matches = sorted(list(set(matches)), key=lambda x: len(x[0]))
    else:
        unique_matches = sorted(list(set(matches)), key=lambda x: x[0].lower())

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for song, artist in unique_matches:
            line = f"{song} - {artist}"
            print(line)
            outfile.write(line + '\n')
    
    print(f"Output saved to {output_filename}")


main()
