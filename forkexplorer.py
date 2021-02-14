import glob
import shutil
from os.path import join
from time import sleep
from urllib.parse import urljoin

import geckodriver_autoinstaller
import requests
import typer
from arrow import Arrow
from bs4 import BeautifulSoup
from dateutil.parser import parse
from diskcache import Index
from fake_headers import Headers
from requests_html import HTMLSession
from rich import traceback
from rich.progress import track
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tenacity import RetryError

traceback.install(
    show_locals=True,
)

header = Headers(
    browser="firefox",  # Generate only Chrome UA
    os="win",  # Generate ony Windows platform
    headers=True,  # generate misc headers
).generate()

cache = Index('./cache')
session = HTMLSession()


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


def get_last_commit_date(fork_url: str, driver: webdriver.Firefox, timeout: float):
    cached_date = cache.get(fork_url)
    if cached_date:
        return cached_date
    driver.get(fork_url)
    sleep(1)
    time_tag = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "relative-time"))
    )
    date = parse(time_tag.get_attribute('datetime'))
    cache[fork_url] = date
    return date


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
):
    driver = setup_driver(headless)
    fork_page = normalize_link(url)
    forks = get_fork_links(fork_page)
    latest = None
    for fork in track(forks, description=f'Searching {len(forks)} forks...'):
        try:
            date = get_last_commit_date(fork, driver, timeout)
            print_friendly_date = date
            if humanize:
                print_friendly_date = Arrow.fromdate(date).humanize()
            if not latest:
                latest = (fork, date)
                print('First date found:', fork, print_friendly_date)
            elif latest[1] < date:
                latest = (fork, date)
                print('A more recent fork found:', fork, print_friendly_date)
        except RetryError:
            print("Couldn't find date for", fork)


if __name__ == '__main__':
    typer.run(cli)
