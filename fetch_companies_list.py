import time
from bs4 import BeautifulSoup
from login import login_with_credentials
from constants import linkedin_it_companies_list_url


def fetch_companies_dict():
    driver = login_with_credentials()
    companies_map = {}
    page_count = fetch_pages_count(driver=driver)
    while page_count > 0:
        url = linkedin_it_companies_list_url.format(page_count)
        driver.get(url)
        add_delay(driver=driver)
        src = driver.page_source
        soup = BeautifulSoup(src, 'html.parser')
        # intro = soup.find('div', {'class': 'search-results-container'})
        # data = intro.find('ul')
        #
        # res = ''
        # for li in data.find_all("li"):
        #     res += li.text
        #
        # res_list = (res.rstrip().split('\n'))
        # res_list = [x.strip() for x in res_list if x.strip()]
        #
        # for item in res_list:
        #     res = [ele for ele in list_of_ignored_keywords_in_company_list if (ele in item)]
        #     if not bool(res):
        #         companies_list.append(item)

        outer = soup.find('ul', {'class': 'reusable-search__entity-result-list'})
        inner = outer.find_all('li', {'class': 'reusable-search__result-container'})
        for item in inner:
            company = item.find('span', {'class': 'entity-result__title-text'})
            companies_map[company.text.replace('\n', '')] = company.find('a')['href']
        page_count -= 1

    return companies_map


def fetch_pages_count(driver):
    url = linkedin_it_companies_list_url.format(1)
    driver.get(url)
    add_delay(driver=driver)

    src = driver.page_source
    soup = BeautifulSoup(src, 'html.parser')

    # Get count of pages
    # Find the pagination element
    pagination = soup.find('div', {'class': 'artdeco-pagination__page-state'})

    # If there is no pagination element, we have reached the last page
    if not pagination:
        return 0
    return int(pagination.decode_contents().strip().split()[-1])


def add_delay(driver):
    start = time.time()
    initial_scroll = 0
    final_scroll = 1000
    while True:
        driver.execute_script(f"window.scrollTo({initial_scroll},{final_scroll})")
        initial_scroll = final_scroll
        final_scroll += 1000
        time.sleep(5)
        end = time.time()
        if round(end - start) >= 5:
            break


if __name__ == '__main__':
    fetch_companies_dict()
