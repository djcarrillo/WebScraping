import argparse
import logging
import re
import job_sites_po as jobs
from common import config
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _fetch_vacancy(job_sites_uid, host, link):
    job_ = None
    try:
        job_ = jobs.Jobvacancy(job_sites_uid, host + link)
    except (HTTPError, MaxRetryError) as e:
        logger.warning(f"Error fetching data {e}")
    return job_


def job_sites_scraper(job_sites_uid):
    host = config()['job_sites'][job_sites_uid]['url']
    logging.info(f'Iniciando Scraper para {host}')
    homepage = jobs.HomePage(job_sites_uid, host)

    data_fetch = []
    for link in homepage.job_links:
        #host_primary = host.replace('/crabi', '')
        job_ = _fetch_vacancy(job_sites_uid, host, link)
        if job_:
            logger.info("a vacancy successfully filled")
            data_fetch.append(job_)
            print(job_.vacancy)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    job_sites = list(config()['job_sites'].keys())

    parser.add_argument('--job_sites',
                        help='web scraping job sites',
                        type=str,
                        choices=job_sites,
                        default='crabi')

    args = parser.parse_args()

    job_sites_scraper(args.job_sites)
