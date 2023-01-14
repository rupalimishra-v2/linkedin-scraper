import re
import urllib.request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import constants
import test
from csv_utils import csv_writer_list_of_dict
from fetch_companies_list import fetch_companies_dict, add_delay
from login import login


def fetch_company_data(URL, scraped_data):
    try:
        # response = requests.get(URL, headers=headers, proxies=proxies)
        # print(response.text)

        # driver = login()
        # driver.get(URL)
        # add_delay(driver=driver)
        # src = driver.page_source
        # soup = BeautifulSoup(src, 'html.parser')

        entry = ('giK5XZZFO4RG25pP3bdf:RNW78Fm5@185.130.105.109:10000')
        query = urllib.request.ProxyHandler({
            'http': entry,
            'https': entry,
        })
        execute = urllib.request.build_opener(query)
        src = execute.open(URL).read().decode('utf-8')
        soup = BeautifulSoup(src, 'html.parser')

        company_data = {}
        headers = soup.find('div', class_='top-card-layout__entity-info')

        company_name, industry, location, followers = [''] * 4
        if headers:
            company_element = headers.find("h1", class_="top-card-layout__title")
            company_name = company_element.text.strip() if company_element is not None else ''

            industry_element = headers.find("h2", class_="top-card-layout__headline")
            industry = industry_element.text.strip() if industry_element is not None else ''

            location_and_followers_element = headers.find("h3", class_="top-card-layout__first-subline")
            location_and_followers = location_and_followers_element.text if location_and_followers_element is not None else ''

            if len(location_and_followers) > 0:
                location_and_followers_strip = location_and_followers.rstrip().split('\n')
                location_and_followers_list = [x.strip() for x in location_and_followers_strip if x.strip()]
                location_and_followers_list[0] = location_and_followers_list[0].replace(',', '')
                location_and_followers_values = re.findall(r'\d+|\D+', location_and_followers_list[0])
                location = location_and_followers_values[0].strip()
                followers = location_and_followers_values[1].strip()

        company_data["Company Name"] = company_name
        company_data["Industry"] = industry
        company_data["Location"] = location
        company_data["Followers"] = followers

        employees = ''
        employees_element = soup.find("div", class_="face-pile")
        employees_text = employees_element.find('a').text.strip() if employees_element is not None else ''
        if len(employees_text) > 0:
            employees_text = employees_text.replace(',', '')
            employees_values = re.findall(r'\d+|\D+', employees_text)
            employees = employees_values[1] if len(employees_values) > 1 else ''

        company_data["Employees"] = employees

        description_element = soup.find("p", attrs={"data-test-id": "about-us__description"})
        description = description_element.text if description_element is not None else ''
        company_data["Description"] = description

        dt_elements = soup.find("dl").find_all("dt")
        dd_elements = soup.find("dl").find_all("dd")

        details = {}

        # Extract the text content of each dt and dd element, and add it to the dictionary
        for dt, dd in zip(dt_elements, dd_elements):
            key = dt.text.strip()
            value = dd.text.strip()
            details[key] = value

        company_data.update(details)

        # Get the similar pages
        similar_pages = soup.find("section", attrs={"data-test-id": "similar-pages"})
        pages = similar_pages.find('div', class_='show-more-less')
        ul = pages.find('ul')
        lis = ul.find_all('li')

        similar_pages_list = []
        for li in lis:
            a = li.find('a')

            href_element = a.get('href')
            href = href_element.strip() if href_element is not None else ''

            title_element = a.find('h3')
            title = title_element.text.strip() if title_element is not None else ''

            subtitle_element = a.find('p', class_='base-aside-card__subtitle')
            subtitle = subtitle_element.text.strip() if subtitle_element is not None else ''

            second_subtitle_element = a.find('p', class_='base-aside-card__second-subtitle')
            second_subtitle = second_subtitle_element.text.strip() if second_subtitle_element is not None else ''

            similar_page = {'Link': href, 'Title': title, 'Subtitle': subtitle, 'Second Subtitle': second_subtitle}
            similar_pages_list.append(similar_page)

        company_data["Similar Pages"] = similar_pages_list

        stock_section = soup.find('section', class_='aside-section-container', attrs={'data-test-id': 'stock'})
        href, ticker, time, exchange, delay, current_price, price_change, open_price, low_price, high_price, provider = [
                                                                                                                            ''] * 11
        if stock_section:
            # Find the ticker element
            ticker_element = stock_section.find('p', class_='mb-0.5 flex-[0_0_50%] font-bold')
            ticker = ticker_element.text.strip() if ticker_element is not None else ''

            # Find the time element
            time_element = stock_section.find('time')
            time = time_element.text.strip() if time_element is not None else ''

            # Find the exchange element
            exchange_element = stock_section.find('p', class_='mb-0.5 flex-[0_0_50%] text-color-text-secondary text-sm')
            exchange = exchange_element.text.strip() if exchange_element is not None else ''

            # Find the delay element
            delay_element = stock_section.find('p',
                                               class_='mb-0.5 flex-[0_0_50%] text-color-text-secondary text-sm text-right')
            delay = delay_element.text.strip() if delay_element is not None else ''

            # Find the current price element
            current_price_element = stock_section.find('p', class_='text-display-lg mb-0.5')
            current_price = current_price_element.text.strip() if current_price_element is not None else ''

            # Find the price change element
            price_change_element = stock_section.find('p', class_='text-color-text-positive')
            price_change = price_change_element.text.strip() if price_change_element is not None else ''

            # Find the daily price elements
            dl = stock_section.find('dl', class_='mb-2 flex flex-wrap')
            open_price_element = dl.find('dd', class_='ml-1')
            open_price = open_price_element.text.strip() if open_price_element is not None else ''

            low_price_element = dl.find_all('dd', class_='ml-1')[1]
            low_price = low_price_element.text.strip() if low_price_element is not None else ''

            high_price_element = dl.find_all('dd', class_='ml-1')[2]
            high_price = high_price_element.text.strip() if high_price_element is not None else ''

            # Find the provider element
            provider_element = stock_section.find('p', class_='stock__provider')
            provider = provider_element.text.strip() if provider_element is not None else ''
            # Find the link element
            link = stock_section.find('a')
            href = link.get('href') if link.get('href') is not None else ''

        company_data["Stock Details Link"] = href
        company_data["Ticker"] = ticker
        company_data["Time"] = time
        company_data["Exchange"] = exchange
        company_data["Delay"] = delay
        company_data["Current Price"] = current_price
        company_data["Price Change"] = price_change
        company_data["Open Price"] = open_price
        company_data["Low Price"] = low_price
        company_data["High Price"] = high_price
        company_data["Provider"] = provider

        company_data.update(fetch_job_data(url=URL))
        scraped_data.put(company_data)
    except Exception as e:
        print(e)


def convert_queue_to_list(scraped_data):
    data_list = []
    while not scraped_data.empty():
        print(scraped_data.get())
        data_list.append(scraped_data.get())
    csv_writer_list_of_dict(data_list)


def thread_manager():
    scraped_data = Queue()
    # URLS = fetch_companies_dict(driver)
    URLS = test.test_companies_list
    with ThreadPoolExecutor() as executor:
        for url in URLS:
            executor.submit(fetch_company_data, url, scraped_data)
    convert_queue_to_list(scraped_data)

def fetch_job_data(url):
    driver = login()
    jobs_url = url + constants.jobs
    driver.get(jobs_url)
    add_delay(driver=driver)
    src = driver.page_source
    soup = BeautifulSoup(src, 'html.parser')

    jobs_data = {}
    jobs_list = []
    link_for_all_jobs = ''
    section = soup.find(class_='core-section-container my-3')
    if section:
        link_for_all_jobs = section.find('a')['href'] if section.find('a')['href'] is not None else ''
        jobs_list_element = section.find(class_='core-section-container__content break-words')

        if jobs_list_element:
            for li in jobs_list_element.find_all('li'):
                job_title_element = li.find(
                    class_='base-main-card__title font-sans text-[18px] font-bold text-color-text overflow-hidden')
                job_title = job_title_element.get_text().strip() if job_title_element is not None else ''

                company_element = li.find(class_='base-main-card__subtitle body-text text-color-text overflow-hidden')
                company = company_element.get_text().strip() if company_element is not None else ''

                location_element = li.find(
                    class_='main-job-card__location block mb-0.5 text-md leading-open font-normal text-color-text-low-emphasis')
                location = location_element.get_text().strip() if location_element is not None else ''

                date_element = li.find(
                    class_='main-job-card__listdate--new text-color-signal-positive font-bold text-sm leading-open')
                date = date_element.get_text().strip() if date_element is not None else ''

                job = {'title': job_title, 'company': company, 'location': location, 'date': date}
                jobs_list.append(job)

    jobs_data["Jobs"] = jobs_list
    jobs_data["All Jobs Link"] = link_for_all_jobs
    driver.close()
    return jobs_data


if __name__ == '__main__':
    thread_manager()
