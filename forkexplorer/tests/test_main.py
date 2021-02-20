import re
import shutil
from datetime import datetime
from random import choice
from time import sleep

import pytest

from forkexplorer import (
    setup_driver,
    get_fork_links,
    get_last_commit_date,
    normalize_link,
    get_fork_commits,
    get_print_friendly_commits,
)

NETWORK_URL = 'https://github.com/emirozer/fake2db/network/members'
REPO_URL = 'https://github.com/emirozer/fake2db'

fork_list = []  # prevent unnecessary calls to github


@pytest.fixture()
def driver():
    driver = setup_driver(True)
    yield driver
    driver.close()


class Test:
    def test_can_take_a_link_and_return_forks(self):
        pattern = re.compile(r'https://github.com/\w+/\w+')
        forks = get_fork_links(NETWORK_URL)
        assert isinstance(forks, list)
        assert any(pattern.findall(' '.join(forks)))
        fork_list.extend(forks)

    def test_can_get_fork_commits(self, driver):
        commit_ahead = 'https://github.com/returnWOW/requests-html'
        commit_behind = 'https://github.com/13910269811/fake2db'
        commit_even = 'https://github.com/tjj021/requests-html'

        ahead_commits = get_fork_commits(driver, url=commit_ahead)
        sleep(1)
        behind_commits = get_fork_commits(driver, url=commit_behind)
        sleep(1)
        even_commits = get_fork_commits(driver, url=commit_even)
        sleep(1)

        assert ahead_commits > 0
        assert behind_commits < 0
        assert even_commits == 0

    def test_can_take_a_fork_and_return_commit_date(self, driver):
        fork = choice(fork_list)
        date = get_last_commit_date(driver, 5, url=fork)
        assert isinstance(date, datetime)

    def test_can_normalize_repo_and_network_page_urls(self):
        url1 = normalize_link(NETWORK_URL)
        url2 = normalize_link(REPO_URL)
        url3 = normalize_link(REPO_URL + '/')
        assert (
            url1
            == url2
            == url3
            == 'https://github.com/emirozer/fake2db/network/members'
        )

    def test_can_make_positivity_number_print_friendly(self):
        assert get_print_friendly_commits(1) == '1 commit ahead of original'
        assert get_print_friendly_commits(2) == '2 commits ahead of original'
        assert get_print_friendly_commits(-1) == '1 commit behind original'
        assert get_print_friendly_commits(-2) == '2 commits behind original'
        assert get_print_friendly_commits(0) == 'even commits'
