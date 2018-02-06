import argparse
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote_plus


anti_throttle_delay = 0.1  # seconds
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"


def search_url(search_term):
    return (f'https://www.google.com/search?q={quote_plus(search_term)}&espv=2&biw=1366&bih=667&site=webhp&source=lnms&'
            f'tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg')


def download_page_as_str(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': user_agent})
        resp = urllib.request.urlopen(req)
        return str(resp.read())
    except Exception as e:
        print(str(e))


def next_image_url_from_page(page):
    start_line = page.find('rg_di')
    # No links have been found
    if start_line == -1:
        return None, None

    start_line = page.find('"class="rg_meta"')
    start_content = page.find('"ou"', start_line + 1)
    end_content = page.find(',"ow"', start_content + 1)
    image_url = str(page[start_content + 6:end_content - 1])
    return image_url, page[end_content:]


def find_image_urls(page):
    image_urls = []
    image_url, remaining_page = next_image_url_from_page(page)
    while image_url is not None:
        image_urls.append(image_url)
        image_url, remaining_page = next_image_url_from_page(remaining_page)
    return image_urls


def main(search_keywords):
    minimum_version = (3, 0)
    cur_version = sys.version_info
    if cur_version < minimum_version:
        raise Exception("Unsupported Python version, please upgrade to Python 3")

    error_count = 0
    start_time = time.time()
    for search_keyword in search_keywords:
        print(f'Downloading results for: {search_keyword}')
        url = search_url(search_keyword)
        raw_html = download_page_as_str(url)
        time.sleep(anti_throttle_delay)
        image_urls = find_image_urls(raw_html)

        print(f"""
Total image links: {str(len(image_urls))}.
Total time taken: {str(time.time() - start_time)} seconds.
Starting download...
        """)

        os.makedirs(search_keyword)

        k = 0
        for image_url in image_urls:
            try:
                req = urllib.request.Request(image_url, headers={"User-Agent": user_agent})
                response = urllib.request.urlopen(req, None, 5)
                output_file = open(f'{search_keyword}/{search_keyword}-{str(k)}.jpg', 'wb')

                data = response.read()
                output_file.write(data)
                response.close()

                print(f'completed ====> {url}')
            except (IOError, urllib.error.HTTPError, urllib.error.URLError) as err:
                error_count += 1
                print(f'Failed for {url} with error:{str(err)}')
            k += 1

    print(f"""
Finished
Total Errors: {str(error_count)}
    """)


parser = argparse.ArgumentParser()
parser.add_argument(
    'keywords',
    nargs='+',
    help="""
        This list is used to search keywords. You can edit this list to search for google images of your choice. You can
        simply add and remove elements of the list.
        Usage:
        google-images-download cat dog
    """
)

args = parser.parse_args()

main(args.keywords)
