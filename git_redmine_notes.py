#!/usr/bin/env python

"""
Use git notes to add issue metadata to commits that reference issues.
"""

import csv
import re
import subprocess


hash_re = re.compile(r'[0-9a-z]{40}')
issue_ref_re = re.compile(r'#(\d+)')


def get_issues(export):
    """
    Parses a redmine issue export in csv format and returns a dictionary
    of (ticket id, ticket infos). `export` is the filepath.
    """
    issues = {}

    with open(export, 'rb') as f:
        reader = csv.DictReader(f, delimiter=';')
        issues = dict((int(row['#']), row) for row in reader)

    return issues


def get_commits(repo):
    """
    Find all commits that have a reference to a ticket number.
    """
    proc = subprocess.Popen(['git', '--no-pager', 'log',
                             '--grep=#[[:digit:]]+', '--extended-regexp',
                             '--pretty=format:%H%n%B', '--all'],
                            env={'GIT_DIR': repo}, stdout=subprocess.PIPE)
    output = proc.communicate()[0].splitlines()

    it = iter(output)
    commits = []

    try:
        while True:
            commit_hash = it.next()
            while not hash_re.match(commit_hash):
                commit_hash = it.next()

            issues = issue_ref_re.findall(it.next())
            while not issues:
                issues = issue_ref_re.findall(it.next())

            commits.append((commit_hash, issues))
    except StopIteration:
        return commits


def git_add_note(repo, commit, note):
    proc = subprocess.Popen(['git', 'notes', 'add',
                             '-F', '-', commit],
                            env={'GIT_DIR': repo}, stdin=subprocess.PIPE)

    proc.communicate(note)


REPO = 'path to .git directory of repository'
REDMINE_EXPORT = 'path to issue csv export of redmine'

issues = get_issues(REDMINE_EXPORT)
commits = get_commits(REPO)


for commit_hash, refs in commits:
    r = refs[0] # TODO handle multiple issue references
    try:
        issue = issues[int(r)]
        note = issue['Thema'] + '\n\n'
        note += issue['Beschreibung']
        # TODO don't include tracebacks right now..
        if 'Traceback' in note:
            continue

        git_add_note(REPO, commit_hash, note)
    except KeyError:
        print '%s: unknown ticket reference %s' % (commit_hash, r)
