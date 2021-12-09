import bs4
import requests
from common import config


class New_site:

    def __init__(self, job_sites_uid, url):
        self._config = config()['job_sites'][job_sites_uid]
        self._queries = self._config['query']
        self._html = None
        self._visit(url)

    def _select(self, queries_string):
        return self._html.select(queries_string)

    def _visit(self, url):
        response = requests.get(url)
        response.raise_for_status()
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')


class HomePage(New_site):

    def __init__(self, job_sites_uid, url):
        self._job_sites_uid = job_sites_uid
        super().__init__(job_sites_uid, url)

    @property
    def job_links(self):
        link_list = []
        for link in self._select(self._queries):
            if link and link.a.has_attr('href'):
                link_list.append(link)



        return set([link.a['href'].replace('/'+self._job_sites_uid, '') for link in link_list])


class Jobvacancy(New_site):

    def __init__(self, job_sites_uid, url):
        super().__init__(job_sites_uid, url)

    @property
    def vacancy(self):
        result = self._select(self._queries['vacancy'])
        return result[0].text.strip() if len(result) else ''

    def location(self):
        pass

    def description(self):
        pass

    def link(self):
        pass
