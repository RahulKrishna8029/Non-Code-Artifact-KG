from github import Github

from makecsv import makecsvfile

from pull_Request_structure import display_pull_request_info

from Knowledge_Graph import KG_Pull_Requests

# access token initialisation
g = Github()


def pull_graph(repo):
    # Get closed pull requests
    pull_requests = repo.get_pulls(state='closed', sort='created', base='master')

    # Define a dictionary to store pull request information
    pull_requests_info = {}

    # Counter for indexing pull requests
    k = 0

    # Iterate through the first 10 closed pull requests (you can adjust the range)
    for pr in pull_requests[:20]:
        if pr.is_merged():
            # Extracting the description of a pull request
            pr_description = pr.body

            # Extracting the labels attached to a pull request and storing it in a list
            pr_labels = [label.name for label in pr.labels]

            # Extracting files changes made by a pull request and associated metadata and storing it in a list of
            # dictionaries
            files = pr.get_files()
            changed_files_list = []
            for file in files:
                changed_files_list.append({
                    'Name': file.filename,
                    'Line Additions': file.additions,
                    'Line Deletions': file.deletions,
                    'Patch': file.patch
                })

            # Extracting comments from the pull requests
            pull_comments = pr.get_comments()
            pr_comments = [comment.body for comment in pull_comments]

            # Extracting commits of the pull requests
            pull_commits_list = []
            pr_commits = pr.get_commits()
            for commit in pr_commits:
                pull_commits_list.append({
                    'Commit_ID': commit.sha,
                    'Commit_Message': commit.commit.message,
                    'Commit_Timestamp': commit.commit.committer.date
                })

            # Aggregating all the extracted data of a pull request into a dictionary named: temp_pr
            temp_pr = {
                'Pull_Request_Number': pr.number,
                'Pull_Request_State': pr.state,
                'Pull_Request_Author': pr.user.login,
                'Pull_Request_Body': pr.body,
                'Number_of_Files_changed': pr.changed_files,
                'File_Names': [file.filename for file in files],
                'Number_of_commits': pr.commits,
                'Commits_Data': pull_commits_list,
                'Commits_Files_Data': changed_files_list,
                'Time_Stamps': pr.closed_at
            }

            k = k + 1

            # Storing data of each pull request that has changed files in the README.md
            if "README.md" in temp_pr['File_Names']:
                pull_requests_info[k] = temp_pr

    makecsvfile(pull_requests_info)
    for _, pr_info in pull_requests_info.items():
        display_pull_request_info(pr_info)
        print("\n" + "=" * 50 + "\n")  # Separate each pull request with a line of '=' characters
    KG_Pull_Requests(pull_requests_info)


if __name__ == "__main__":
    user_input = input("Enter Repository : ")
    # github username/repo_name
    repo = g.get_repo(user_input)
    pull_graph(repo)
