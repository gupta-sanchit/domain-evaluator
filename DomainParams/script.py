import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class DomainParams:
    def __init__(self):
        self.res = {}
        self.TOKEN = '280b72406590b0e60762a3f2b6916034450949c3'
        self.BASE_URL = ''
        self.refURL = ''
        self.ratingURL = ''
        self.positionMetricsURL = ''

        self.refDomain = -1
        self.domainRating = -1
        self.organicKeyword = -1
        self.organicTraffic = -1

    def RefDomain(self):
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=2, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(self.refURL)

        if response.status_code != 200:
            print("ERROR")
            print(self.refURL)
            print(response.text)
            return
        r = response.json()

        self.refDomain = r['stats']['refdomains']

    def DomainRating(self):
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=2, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(self.ratingURL)
        if response.status_code != 200:
            print("ERROR")
            print(self.ratingURL)
            print(response.text)
            return
        r = response.json()
        self.domainRating = r['domain']['domain_rating']

    def OrganicThings(self):
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=2, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(self.positionMetricsURL)
        if response.status_code != 200:
            print("ERROR")
            print(self.positionMetricsURL)
            print(response.text)
            return
        r = response.json()

        self.organicKeyword = r['metrics']['positions']
        self.organicTraffic = round(r['metrics']['traffic'], 2)

    def getParams(self, domain):
        self.BASE_URL = f'https://apiv2.ahrefs.com?token={self.TOKEN}&target={domain}&limit=1000&output=json&mode=domain'
        self.refURL = self.BASE_URL + '&from=refdomains'
        self.ratingURL = self.BASE_URL + '&from=domain_rating'
        self.positionMetricsURL = self.BASE_URL + '&from=positions_metrics'

        self.RefDomain()
        self.DomainRating()
        self.OrganicThings()

        self.res['domain'] = domain
        self.res['ref-domains'] = self.refDomain
        self.res['domain-rating'] = self.domainRating
        self.res['organic-keywords'] = self.organicKeyword
        self.res['organic-traffic'] = self.organicTraffic

        return self.res


if __name__ == '__main__':
    p = DomainParams()
    params = p.getParams(domain='ahrefs.com')
    print(params)
