import traceback

import requests
import github



def create_bug_report(token: str, repo_name: str, given_info: str = '') -> None:
    """Use Github Issues to create a bug report about 
    the current raised exception. given_info can be anything 
    extra needed to help debug later.
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
        error.append('Info from Response:')
        error.append(extra_info)
        error.append('\n')

    if given_info:
        error.append('Additional Info:')
        error.append(given_info)

    body = '\n'.join(error)

    g = github.Github(token)
    repo = g.get_repo('clothingshoponline/' + repo_name)
    issue = repo.create_issue(title=title, body=f'<pre>{body}</pre>')
    issue.edit(labels=['bug'])