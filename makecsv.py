import pandas as pd
import csv

def makecsvfile(pull_requests_info):
    df = pd.DataFrame(pull_requests_info)

    df.transpose()
    # Assuming the code for extracting pull request information is already executed

    # Check if pull_requests_info is not empty
    if not pull_requests_info:
        print("No pull request information found.")
    else:
        # Get keys from the first pull request (if available)
        first_pr_data = next(iter(pull_requests_info.values()), None)
        if first_pr_data:
            csv_fields = list(first_pr_data.keys())

            # Writing the extracted information to a CSV file
            csv_filename = 'pull_requests_info.csv'

            with open(csv_filename, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
                writer.writeheader()
                for pr_data in pull_requests_info.values():
                    writer.writerow(pr_data)

            print(f'Information from pull requests has been stored in {csv_filename}.')
        else:
            print("No pull request data found.")
