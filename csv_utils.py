import csv
import datetime


def csv_writer_list_of_dict(data):
    # Open the CSV file
    now = datetime.datetime.now()

    # Format the date and time as a string
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # Append the timestamp to the file path
    file_path = "output_" + timestamp + ".csv"

    with open(file_path, "w", newline="") as f:
        # Create a DictWriter object
        writer = csv.DictWriter(f, fieldnames=["Company Name", "Industry", "Location", "Followers", "Employees",
                                               "Description", "Website", "Industries", "Company size", "Headquarters",
                                               "Type", "Founded", "Specialties", "Similar Pages", "Stock Details Link",
                                               "Ticker", "Time", "Exchange", "Delay", "Current Price", "Price Change",
                                               "Open Price", "Low Price", "High Price", "Provider", "Jobs",
                                               "All Jobs Link"])

        # Write the header row
        writer.writeheader()

        # Iterate over the list of dictionaries and write each one to the CSV
        for dictionary in data:
            row = {}
            for key in dictionary.keys():
                try:
                    # Set the value of the cell to the value in the dictionary
                    row[key] = dictionary[key]
                except KeyError:
                    # Set the value of the cell to an empty string if the key does not exist in the dictionary
                    row[key] = ""
            writer.writerow(row)


def csv_writer_dict(data):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    file_path = "output_" + timestamp + ".csv"
    with open(file_path, 'w', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)

        # Write the first row (column names)
        writer.writerow(data.keys())

        # Write the data row
        writer.writerow(data.values())
