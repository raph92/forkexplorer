import glob
import shutil
from datetime import datetime
from os.path import join
from time import sleep
from urllib.parse import urljoin

import geckodriver_autoinstaller
import requests
import typer
import re

from appdirs import user_cache_dir
from arrow import Arrow
from bs4 import BeautifulSoup
from dateutil.parser import parse
from diskcache import Index
from fake_headers import Headers
from rich import traceback
from rich.console import Console
from rich.progress import track
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

traceback.install(
    show_locals=True,
)

header = Headers(
    browser="firefox",  # Generate only Chrome UA
    os="win",  # Generate ony Windows platform
    headers=True,  # generate misc headers
).generate()

cache = Index(join(user_cache_dir('forkexplorer', '1.0.0'), 'data'))
console = Console()
print = console.print


def setup_driver(headless: bool):
    gecko_path = shutil.which("geckodriver") or shutil.which("geckodriver.exe")
    if not gecko_path:
        try:
            gecko_path = glob.glob('*/*geckodriver')[0]
        except IndexError:
            print('Installing geckodriver...')
            gecko_path = geckodriver_autoinstaller.install(True)
            print('Installed geckodriver to', gecko_path)
    options = Options()
    options.headless = headless
    driver = webdriver.Firefox(options=options, executable_path=gecko_path)
    return driver


def get_fork_links(url: str):
    incomplete_urls = []
    res = requests.get(url, headers=header)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    fork_tags = soup.select('.repo')
    for fork_html in fork_tags:
        incomplete_urls.append([a.get('href') for a in fork_html.select('a')][2])
    return [urljoin('https://github.com', iu) for iu in incomplete_urls]


def get_fork_date_and_commits(
    fork_url: str, driver: webdriver.Firefox, timeout
) -> tuple[datetime, int]:
    if fork_url in cache:
        return cache.get(fork_url)
    driver.get(fork_url)
    sleep(1)

    # date does first because it utilizes EC wait
    date = get_last_commit_date(driver, timeout)
    commits = get_fork_commits(driver)

    assert commits is not None
    assert date is not None

    cache[fork_url] = date, commits
    return date, commits


def get_fork_commits(driver: webdriver.Firefox, url=None) -> int:
    # Use this so that this can be individually tested

    if url:
        driver.get(url)

    ahead_pattern = re.compile(r'This branch is (\d+) commits? ahead of \w+'), 1
    even_pattern = re.compile(r'This branch is even with \w+'), 0
    behind_pattern = re.compile(r'This branch is (\d+) commits? behind \w+'), -1

    # return positive numbers for commits ahead, negative for behind, 0 for even
    for pattern, positivity in ahead_pattern, even_pattern, behind_pattern:
        findall = pattern.findall(driver.page_source)
        if findall:
            return (int(findall[0]) * positivity) if positivity else 0

    return 0


def get_last_commit_date(driver: webdriver.Firefox, timeout: float, url=None):
    if url:
        driver.get(url)

    time_tag = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "relative-time"))
    )
    date = parse(time_tag.get_attribute('datetime'))
    return date


def get_print_friendly_commits(commits_no: int):
    commit_str = 'commit'
    if commits_no < -1 or commits_no > 1:
        commit_str += 's'
    if commits_no == 0:
        return 'even commits'
    if commits_no > 0:
        return f'{commits_no} {commit_str} ahead of original'
    if commits_no < 0:
        return f'{abs(commits_no)} {commit_str} behind original'


def normalize_link(url: str):
    normalized_url = url
    if 'network/members' not in url.lower():
        normalized_url = join(url, 'network/members')
    return normalized_url


def cli(
    url: str = typer.Argument(..., help='The Github repo or the fork page URL'),
    timeout: float = typer.Option(
        5, help='How long to wait on a page to finish loading'
    ),
    humanize: bool = typer.Option(
        False,
        '-h',
        '--humanize',
        help='If passed, program will display dates as "3 months ago"',
    ),
    headless: bool = typer.Option(
        True, help='If passed, the program will run selenium in headless mode'
    ),
    show_all: bool = typer.Option(
        False,
        '-s',
        '--show-all',
        help='Show all forks whether or not it is the most recent.',
    ),
):
    driver = setup_driver(headless)
    fork_page = normalize_link(url)
    forks = get_fork_links(fork_page)
    latest = None
    for fork_url in track(
        forks, description=f'Searching {len(forks)} forks...', console=console
    ):
        date, commits = get_fork_date_and_commits(fork_url, driver, timeout)
        print_friendly_date = date
        if humanize:
            print_friendly_date = Arrow.fromdate(date).humanize()
        if not latest:
            latest = (fork_url, date)
            print('Original repo and date:', fork_url, print_friendly_date)
        elif latest[1] < date:
            latest = (fork_url, date)
            if not show_all:
                print(
                    'A more recent fork found:',
                    fork_url,
                    print_friendly_date,
                    get_print_friendly_commits(commits),
                )
        if latest and show_all:
            print('A fork found:', fork_url, print_friendly_date)
    print('\nMost recent fork:', *latest)


def main():
    typer.run(cli)


if __name__ == '__main__':
    main()
