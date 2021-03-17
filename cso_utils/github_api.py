import os
import traceback

import requests
import github



def create_bug_report(token: str, repo_name: str) -> None:
    """Use Github Issues to create a bug report about 
    the current raised exception.
    """
    error = traceback.format_exc().split('\n')

    title = ''
    i = -1
    while title == '':
        title = error[i]
        i -= 1
    title = '[Code Generated Issue] ' + title

    extra_info = ''

    try:
        raise
    except requests.exceptions.HTTPError as e:
        extra_info = e.response.text
    except:
        pass

    if extra_info:
        error.append('Additional Info:')
        error.append(extra_info)
    body = '\n'.join(error)

    g = github.Github(token)
    repo = g.get_repo('clothingshoponline/' + repo_name)
    label = repo.get_label('bug')
    repo.create_issue(title=title, body=body, labels=[label])