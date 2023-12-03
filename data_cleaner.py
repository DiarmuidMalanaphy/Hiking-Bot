import csv
import sys

def main(filename):
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as infile, \
             open('clean.txt', 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            first_row = True

            for row in reader:
                if first_row:
                    # Modify and write the header row
                    if len(row) >= 23:  # Check if there are enough columns
                        row[3] = 'forename'
                        row[4] = 'lastname'
                        row[22] = 'username'
                    selected_columns = [row[3], row[4], row[22]]
                    writer.writerow(selected_columns)
                    first_row = False  # Set to False after processing the header
                else:
                    # Process and write data rows
                    if len(row) >= 23:
                        selected_columns = [row[3], row[4], row[22]]
                        writer.writerow(selected_columns)

    except FileNotFoundError:
        print(f"File not found: {input_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
    


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        main(input_filename)
    else:
        print("Please provide a filename.")