import requests
import pyourls3

# Annotation imports
from typing import (
    Any,
    Optional,
    Dict,
    List,
    Union
)

wax_precision = 100000000

class RequestException(Exception):
    """ Exception raised for errors when requesting URL.

    Attributes:
        url --- the requested url
        message --- explanation of error
    """

    def init(self, url, message="Request did not return status code 200"):
        self.url = url
        self.message = message
        super().__init__(self.message)

class API():

    def __init__(self, bot=None, url: str = "", secret: str = "") -> None:
        if bot:
            self.config = bot.config
            url = self.config["yourls"]["url"]
            secret = self.config["yourls"]["secret"]
        self.yourls: pyourls3.Yourls = pyourls3.Yourls(
            addr=url,
            key=secret)

    def get_listings(self, building: str, page_nr: int, amount: int = 1
                     ) -> Optional[Dict[Union[str, int], Any]]:
        '''
        Get AtomicHub marketplace listings

        Parameters:
            building (str): name of the building

        Returns:
            None or json object containing data from request response
        '''

        listings = None
        url = f"https://wax.api.atomicassets.io/atomicmarket/v2/" + \
              f"sales?state=1&collection_name=onmars&schema_name=land.plots" + \
              f"&mutable_data.{building}={amount}&page={page_nr}&limit=10" + \
              f"&order=asc&sort=price"
        r = requests.get(url)
        try:
            if r.status_code != 200:
                raise RequestException
            else:
                listings = r.json()['data']
                if listings:
                    # listings = extract_data(listings,"sale_id")
                    links: Dict[Union[str, int], Any] = {}
                    try:
                        for count, item in enumerate(listings):
                            links.setdefault(count, {})
                            links[count]["link"] = self.yourls.shorten(
                                f"https://wax.atomichub.io/market/sale/" +
                                f"{item['sale_id']}")["shorturl"]
                            links[count]["price"] = int(
                                round(int(item["price"]["amount"]) /
                                      wax_precision, 0))
                            symbol = item["price"]["token_symbol"]
                            links[count]["token_symbol"] = symbol
                            if len(item["assets"]) > 1:
                                links[count]["land"] = []
                                for land in item["assets"]:
                                    try:
                                        links[count]["land"].append(
                                            {"rarity": land["data"]["rarity"]})
                                    except KeyError:
                                        pass
                            else:
                                links[count]["land"] = {}
                                rarity = item["assets"][0]["data"]["rarity"]
                                links[count]["land"]["rarity"] = rarity
                        return links
                    except KeyError as e:
                        print(e)
                        return None
                else:
                    return None
        except KeyError:
            return None

    def get_buildings(self) -> Optional[Dict[str, Any]]:
        '''
        Get onmars land.plots buildings

        Returns:
            None or json object containing data from request response
        '''

        data = None
        url = "https://wax.api.atomicassets.io/atomicassets/v1/schemas/" + \
              "onmars/land.plots"
        r = requests.get(url)
        try:
            if r.status_code != 200:
                raise RequestException
            else:
                data = r.json()['data']['format']
                # print(data)
                return data
        except KeyError:
            return None

    def extract_data(self, json: Dict[str, Any], d: Any) -> List[Any]:
        data = []
        for item in json:
            data.append(item[d])
        return data
