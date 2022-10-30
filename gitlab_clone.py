#!/usr/bin/env python3

# Author: Ryan Tierney
# Purpose: git clone a local copy of every repo out of Gitlab & ensure its up to date
# Requirements: requests
# Manual steps: Create a read_api Access token using an admin user account on Gitlab if you want all repo's

import os
import requests
import subprocess


class Gitlab:
    def __init__(self, access_token: str, url: str) -> None:
        self.url = url
        self.access_token = access_token
        self.headers = {'PRIVATE-TOKEN': self.access_token}

    def api_get_max_pages(self, per_page=100) -> int:
        r = requests.head(url=self.url, headers=self.headers, params={"per_page": per_page})
        r.raise_for_status()
        return int(r.headers['X-Total-Pages'])

    def api_get(self, per_page=100, page_num=1, sort="asc") -> requests.Response():
        r = requests.get(url=self.url, headers=self.headers, params={"per_page": per_page, "page": page_num, "sort": sort})
        r.raise_for_status()
        return r


def clone(repo_name: str, clone_url: str) -> None:
    if not os.path.isdir(repo_name):
        print(f"{repo_name} Doesn't exist locally, cloning.")
        subprocess.run(["git", "clone", clone_url], capture_output=True, check=True)
    else:
        print(f"{repo_name} already exists, updating.")
        os.chdir(repo_name)
        subprocess.run(["git", "pull"], capture_output=True, check=True)
        os.chdir("..")


def main() -> int:
    gitlab_projects = Gitlab(access_token=os.environ.get("GITLAB_READ_API_TOKEN"), url="https://your-gitlab-domain.com/api/v4/projects")
    total_pages = gitlab_projects.api_get_max_pages()

    for page_num in range(1, total_pages+1):
        r = gitlab_projects.api_get(page_num=page_num)
        for repository in r.json()[1:]:  # Skipping the first internal Gitlab project called "Monitoring"
            repository_name = repository["ssh_url_to_repo"].split("/")[1].split(".")[0]
            clone_url = repository["ssh_url_to_repo"]
            clone(repository_name, clone_url)


if __name__ == "__main__":
    raise SystemExit(main())
