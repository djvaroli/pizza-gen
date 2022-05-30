import os
import typing
from argparse import ArgumentParser
import json

from serpapi import GoogleSearch
from tqdm import tqdm

from data_utils import download_image


def search_images(
    query: str, 
    page_number: int,
    google_domain: str = "google.com",
    tbm: str = "isch"
) -> typing.List[typing.Dict]:
    """Performs Google search for images matching the specified query.

    Args:
        query (str): google search query.
        page_number (int, optional): search results page number.
        google_domain (str, optional): google domain to use for search.
        tbm (str, optional): type of search to perform. Defaults to 'isch' (image search). See https://serpapi.com/search-api for more options.
    """
    
    api_key = os.environ.get("SERPAPI_KEY", None)
    if api_key is None:
        raise RuntimeError("Serp API key is not set. Please set the key and re-try search.")
    
    params = {
        "api_key": api_key,
        "engine": "google",
        "ijn": str(page_number),
        "google_domain": google_domain,
        "tbm": tbm,
        "q": query
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    return results["images_results"]


def download_search_results(
    search_results: typing.List[typing.Dict],
    directory: str
):
    """Downloads images from a google given a search query.

    Args:
        search_results (str): google search query.
    """
    
    for blob_idx, search_blob in enumerate(search_results):
        img_url = search_blob["original"]
        title = search_blob["title"]
        download_image(img_url, f"{directory}/{title}.png")
    
    return



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-q", "--query", help="Search query.", type=str, required=True)
    parser.add_argument("--start_page", help="First page to fetch results from.", type=int, default=0)
    parser.add_argument("--n_pages", help="Number of pages to search through.", type=int, default=10)
    
    args = parser.parse_args()
    
    query = args.query    
    start_page = args.start_page
    n_pages = args.n_pages
    directory = "_".join(query.split(" "))
    
    search_config = args.__dict__
    with tqdm(range(start_page, start_page + n_pages), total=n_pages) as pbar:
        for page_number in pbar:
            search_results = search_images(query, page_number)
            download_search_results(search_results, directory)

    config_fp = f"{directory}/search_config.json"
    with open(config_fp, "w+") as f:
        json.dump(search_config, f)

    