# forkexplorer
Find the latest fork of a Github repo

## Goal
The goal of this project is to make it simple to find the latest commit of a repo. This is particularly useful for abandoned repos.

## How to use
```
Usage: forkexplorer [OPTIONS] URL

Arguments:
  URL  The Github repo or the fork page URL  [required]

Options:
  --timeout FLOAT                 How long to wait on a page to finish loading
                                  [default: 5]

  -h, --humanize                  If passed, program will display dates as "3
                                  months ago"  [default: False]

  --headless / --no-headless      If passed, the program will run selenium in
                                  headless mode  [default: True]

  -s, --show-all                  Show all forks whether or not it is the most
                                  recent.  [default: False]
```

## Example
```bash
python forkexplorer.py  https://github.com/psf/requests-html/network/members -h

```
<img alt="example of usage" src="https://i.imgur.com/qEPtgOF.png" />

## Upcoming Features
- ~~Display number of commits ahead of master~~ ✅
