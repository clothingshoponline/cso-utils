# cso-utils v3.5.1

This package contains wrappers for commonly used API calls from the S&S Activewear, Github, ChannelAdvisor, and Zendesk APIs.

## Requirements

- Python <= 3.9.5
- requests <= 2.25.1
- PyGithub <= 1.55
- pytest <= 6.2.4

## Installation

```
pip install git+https://github.com/clothingshoponline/cso-utils.git@v3.5.1
```

## Usage

### S&S Activewear

#### Import

```
from cso_utils import ssactivewear
```


### Github

#### Import

```
from cso_utils import github_api
```

#### Create Bug Report

_Creates a Github Issue with the traceback. Bad requests that cause a_ `requests.exceptions.HTTPError` _exception will include the traceback and response sent back._

```
try:
    ... # code that raises an exception
except:
    github_api.create_bug_report('<token>', '<repo name>')
```


### Zendesk

#### Import

```
from cso_utils import zendesk
```


### ChannelAdvisor

#### Import

```
from cso_utils import channeladvisor
```
