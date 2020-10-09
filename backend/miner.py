import os
from io import StringIO
from pathlib import Path

# from ansiblemetrics import metrics_extractor
from pydriller.repository_mining import RepositoryMining, GitRepository
from repositoryminer.repository import RepositoryMiner

from apis.models import FixingCommit, FixingFile, Repositories
from apis.serializers import RepositorySerializer

from django.core import serializers


def is_ansible_file(path: str) -> bool:
    """
    Check whether the path is an Ansible file
    :param path: a path
    :return: True if the path link to an Ansible file. False, otherwise
    """
    return path and ('test' not in path) \
           and (
                   'ansible' in path or 'playbooks' in path or 'meta' in path or 'tasks' in path or 'handlers' in path or 'roles' in path) \
           and path.endswith('.yml')


def get_file_content(path: str) -> str:
    """
    Return the content of a file
    :param path: the path to the file
    :return: the content of the file, if exists; None, otherwise.
    """
    if not os.path.isfile(path):
        return ''

    with open(path, 'r') as f:
        return f.read()


class BackendRepositoryMiner:

    def __init__(self, access_token: str, path_to_repo: str, repo_id: str, labels: list = None, regex: str = None):
        """
        :param access_token:
        :param path_to_repo:
        :param repo_id:
        :param labels:
        :param regex:
        """
        self.access_token = access_token
        self.path_to_repo = str(Path(path_to_repo))
        self.repository = Repositories.objects.get(pk=repo_id)
        self.repository_data = RepositorySerializer(self.repository).data
        self.labels = labels if labels else None
        self.regex = regex if regex else None

    def get_files(self) -> set:
        """
        Return all the files in the repository
        :return: a set of strings representing the path of the files in the repository
        """

        files = set()

        for root, _, filenames in os.walk(self.path_to_repo):
            if '.git' in root:
                continue
            for filename in filenames:
                path = os.path.join(root, filename)
                path = path.replace(self.path_to_repo, '')
                if path.startswith('/'):
                    path = path[1:]

                files.add(path)

        return files

    def mine(self):
        miner = RepositoryMiner(
            access_token=self.access_token,
            path_to_repo=self.path_to_repo,
            repo_owner=self.repository_data['owner'],
            repo_name=self.repository_data['name'],
            branch=self.repository_data['default_branch']
        )

        exclude_commits = [commit.sha for commit in FixingCommit.objects.all() if commit.is_false_positive]
        miner.exclude_commits = set(exclude_commits)

        # miner.get_fixing_commits_from_closed_issues(self.labels) (currently only supported for Github)
        miner.get_fixing_commits_from_commit_messages(self.regex)

        # Save fixing-commits that are not false-positive
        for commit in RepositoryMining(path_to_repo=self.path_to_repo,
                                       only_commits=list(miner.fixing_commits),
                                       order='reverse').traverse_commits():

            # Filter-out false positive previously discarded by the user
            if commit.hash in miner.fixing_commits:
                try:
                    fixing_commit = FixingCommit.objects.get(sha=commit.hash)
                    if fixing_commit.is_false_positive:
                        miner.fixing_commits.remove(commit.hash)

                except FixingCommit.DoesNotExist:
                    # Save fixing-commits in DB
                    FixingCommit.objects.create(sha=commit.hash,
                                                msg=commit.msg,
                                                date=commit.committer_date.strftime("%d/%m/%Y %H:%M"),
                                                is_false_positive=False,
                                                repository=self.repository)

        # Filter-out false positive fixing-files previously discarded by the user
        for file in miner.get_fixing_files():
            try:
                fixing_file = FixingFile.objects.get(filepath=file.filepath,
                                                     bug_inducing_commit=file.bic,
                                                     fixing_commit=file.fic)

                if fixing_file.is_false_positive:
                    miner.fixing_files.remove(file)

            except FixingFile.DoesNotExist:
                fixing_commit = FixingCommit.objects.get(sha=file.fic)
                # Save fixing-file in DB
                FixingFile.objects.create(filepath=file.filepath,
                                          is_false_positive=False,
                                          bug_inducing_commit=file.bic,
                                          fixing_commit=fixing_commit)
        # Get all fixing files from the db about this repository: MOVE in training.data_extraction/preparation
        # miner.fixing_files = [FixingFile for file in db.fixing_files]
        # miner.label()

        return len(miner.fixing_commits), len(miner.fixing_files)
