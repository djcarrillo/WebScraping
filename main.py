import routes
import uvicorn
from fastapi import FastAPI
import datetime
import os
import pandas as pd
import csv
import argparse
import logging
import job_sites_po as jobs
import settings
from common import config
from sqlalchemy import create_engine
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
base_path = os.path.join(os.path.dirname(__file__))


@app.get('/')
def help():
    return "Este microservicio scrapea las principales paginas de busqueda de trabajo," \
           "en el momento, tenemos habilitadas: Crabi, Cabify, Murbanos, Nubank.\n Escoge una :)"


@app.post(routes.scraping)
def scraping(page):
    parser = argparse.ArgumentParser()
    job_sites = list(config()['job_sites'].keys())
    parser.add_argument('--job_sites',
                        help='web scraping job sites',
                        type=str,
                        choices=job_sites,
                        default=page)
    args = parser.parse_args()
    job_sites_scraper(args.job_sites)

    return 'Scraping successful, you can go to see the database'


def _connection_db(driver, user, password, host, db):
    engine = create_engine(f'{driver}://{user}:{password}@{host}/{db}')
    logging.info('engine created successfully')
    return engine


def _insert_feth_jobs(name_file):
    engine = _connection_db(settings.driver, settings.user, settings.password, settings.host, settings.db)
    connect = engine.connect()
    df = pd.read_csv(name_file, parse_dates=['fecha_carga'])

    df = df.set_index(list(df.columns))
    df.to_sql(settings.table, engine, if_exists="append")
    logging.info("successful insert")
    connect.close()


def _save_data_fetch(job_sites_uid, data_fetch):
    now = datetime.datetime.now()
    out_file_name = '{job_sites_uid}_{datetime}_jobs.csv'.format(job_sites_uid=job_sites_uid,
                                                                 datetime=now.strftime('%Y%m%d'))

    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(data_fetch[0])))
    with open(out_file_name, mode='w+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for job in data_fetch:
            row = [str(getattr(job, prop)) for prop in csv_headers]
            writer.writerow(row)
    return out_file_name


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
        job_vante = _fetch_vacancy(job_sites_uid, host, link)
        if job_vante:
            logger.info("a vacancy successfully filled")
            data_fetch.append(job_vante)

    name_file = _save_data_fetch(job_sites_uid, data_fetch)
    _insert_feth_jobs(name_file)
    os.remove(name_file)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8080)
