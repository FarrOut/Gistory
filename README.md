# Gistory

A script that uses the Github API to query a user’s publicly available gists.

When the script is first run, it should display a listing of all the user’s publicly available gists. On subsequent runs the script should list any gists that have been published since the last run.

## Prequisites

- [Install Python](https://www.python.org/downloads/)
- [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) to GitHub account


## Setup
### Configuring Authentication
Many REST API endpoints require authentication or return additional information if you are authenticated. Additionally, you can make more requests per hour when you are authenticated.

*Gistory* [authenticates](https://docs.github.com/en/rest/overview/authenticating-to-the-rest-api?apiVersion=2022-11-28#authenticating-with-a-personal-access-token) to Gist's REST API with a personal access token. If you want to use the GitHub REST API for personal use, you can create a personal access token. 

If possible, GitHub recommends that you use a fine-grained personal access token instead of a personal access token (classic). For more information about creating a personal access token, see [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). 
If you are using a fine-grained personal access token, your fine-grained personal access token requires specific permissions in order to access each REST API endpoint. For more information about the permissions that are required for each endpoint, see [Permissions required for fine-grained personal access tokens](https://docs.github.com/en/rest/overview/permissions-required-for-fine-grained-personal-access-tokens).


### Creating a virtualenv
To avoid conflicts by installing packages system-wide, feel free to install packages in an isolated *virtualenv*. To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, one can use the following step to activate one's virtualenv.

```
$ source .venv/bin/activate
```

On a Windows platform, one would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

### Installing Dependencies
Either in an activated *virtualenv* or system-wide (if desired), one can install the required dependencies.

```
$ pip install -r requirements.txt
```

## Usage

Executing *gistory* will display a list of Gists for the authenticated user. To authenticate requests, we need to pass our personal access token via the ```access_token``` argument.

*Example:*
```
python.exe .\gistory.py --access_token github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Upon executing, *Gistory* will first check if a ```gistory.config.json``` file exists which is expected to contain a value of the last time an operation was executed. If present, only the Gists that have been updated *since* that timestamp will be returned. In the absense of this file, it will be presumed to be the first-time run and *all* Gists will be returned.

### Example output

#### First-Time Run
```
INFO:root:Access token received.
INFO:root:Didn't find last access timestamp - presuming this is first-time run..
Gist #0:
Id: 223e16840a2b8bxxxxxxxxxxxxxxxxxxxxx
Created at:2023-09-20T14:45:40Z
Description:An updated gist description
Owner:FarrOut

Gist #1:
Id: 4fef11b3422fxxxxxxxxxxxxxxxxxxx
Created at:2023-09-17T10:08:15Z
Description:Test Gist
Owner:FarrOut

Gist #2:
Id: 58fa05a7844f19xxxxxxxxxxx
Created at:2022-02-01T05:48:02Z
Description:Atom Settings Backup by https://atom.io/packages/sync-settings
Owner:FarrOut

...truncated
```

#### No Gists Found
```
INFO:root:Access token received.
INFO:root:No Gists found to list.
```

#### Some Recently Updated Gists Found
```
INFO:root:Access token received.
Gist #0:
Id: 223e16840a2xxxxxxxxxxxxxxxxxx
Created at:2023-09-20T14:45:40Z
Description:An updated gist description
Owner:FarrOut

Gist #1:
Id: 4fef11b3422fxxxxxxxxxxxxxxx
Created at:2023-09-17T10:08:15Z
Description:Test Gist
Owner:FarrOut
```

### Future Work
Although already impressive, this project still has a long way to go to being even better! Below are some of the next actions to work on:

* [Listing unauthenticated users](https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28#list-gists-for-a-user)
* Allow *creating*, *updating* and *deleting* of Gists via command-line argument
* Improve secure storage and handling of personal access token
* Enable debug mode via flag