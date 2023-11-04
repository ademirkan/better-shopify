import csv
import json

# Open the CSV file
with open("innovation_catalog.csv", mode="r") as csv_file:
    # Read the CSV content
    csv_reader = csv.DictReader(csv_file)

    # Create a list to hold the JSON data
    json_data = []

    # Loop through each row in the CSV
    for row in csv_reader:
        # Add each row as a dictionary to the JSON data list
        json_data.append(row)

    # Output the JSON data to a file
    with open("output.json", mode="w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)
