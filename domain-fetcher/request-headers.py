URL = "https://www.webhosting.dk/cgi-bin/domainscannerview.pl"

PAYLOAD = 'language=DKK&sortby=1&showdayslimit=28'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.webhosting.dk/cgi-bin/domainscannerview.pl?language=DKK',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.webhosting.dk',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers'
}
