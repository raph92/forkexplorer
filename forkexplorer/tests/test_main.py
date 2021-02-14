import re
import shutil
from datetime import datetime
from random import choice

import pytest

from forkexplorer import (
    setup_driver,
    get_fork_links,
    get_last_commit_date,
    normalize_link,
)

NETWORK_URL = 'https://github.com/emirozer/fake2db/network/members'
REPO_URL = 'https://github.com/emirozer/fake2db'

forks_list = []  # prevent unnecessary calls to github


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
        forks_list.extend(forks)

    def test_can_take_a_fork_and_return_commit_date(self, driver):
        fork = choice(forks_list)
        date = get_last_commit_date(fork, driver, 5)
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

    def teardown_class(self):
        shutil.rmtree('./cache')
