def display_pull_request_info(pull_request_info):
    pr_number = pull_request_info['Pull_Request_Number']
    pr_author = pull_request_info['Pull_Request_Author']
    pr_state = pull_request_info['Pull_Request_State']
    pr_closed_at = pull_request_info['Time_Stamps']
    commits_data = pull_request_info['Commits_Data']

    print(f"Pull Request (PR) #{pr_number}")
    print(f"├── Authored by: {pr_author}")
    print(f"├── Pull Request State: {pr_state}")

    # Display Associated Commits
    print("├── Associated Commits")
    for commit_info in commits_data:
        commit_id = commit_info['Commit_ID'][:7]
        commit_message = commit_info['Commit_Message']

        print(f"│   ├── Commit ID: {commit_id}")
        print(f"│   │   ├── Commit Message: {commit_message}")

        # Check if 'Commits_Files_Data' exists before trying to access it
        if 'Commits_Files_Data' in commit_info:
            files_changed = commit_info['Commits_Files_Data']

            # Display Commit Data
            print("│   │   └── Commit Data")
            for file_data in files_changed:
                file_name = file_data['Name']
                lines_added = file_data['Line Additions']
                lines_deleted = file_data['Line Deletions']

                print(f"│   │       ├── Files changed: {file_name}")
                print(f"│   │       ├── Lines added: {lines_added}")
                print(f"│   │       └── Lines deleted: {lines_deleted}")

    # Display Timestamps
    print("└── Timestamps")
    print(f"    └── Closed at: {pr_closed_at}")
