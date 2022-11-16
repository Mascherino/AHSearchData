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

    def __init__(self, yourls_secret: str) -> None:
        self.yourls: pyourls3.Yourls = pyourls3.Yourls("https://link.keedosuul.de/", key=yourls_secret)

    def get_listings(self, building: str, page_nr: int, amount: int = 1) -> Optional[Dict[Union[str, int], Any]]:
        '''
        Get AtomicHub marketplace listings

        Parameters:
            building (str): name of the building

        Returns:
            None or json object containing data from request response
        '''

        listings = None
        r = requests.get(f"https://wax.api.atomicassets.io/atomicmarket/v2/sales?state=1&collection_name=onmars&schema_name=land.plots&mutable_data.{building}={amount}&page={page_nr}&limit=10&order=asc&sort=price")
        try:
            if r.status_code != 200:
                raise RequestException
            else:
                listings = r.json()['data']
                if listings:
                    #listings = extract_data(listings,"sale_id")
                    links: Dict[Union[str, int], Any] = {}
                    try:
                        for count, item in enumerate(listings):
                            links.setdefault(count, {})
                            links[count]["link"] = self.yourls.shorten(f"https://wax.atomichub.io/market/sale/{item['sale_id']}")["shorturl"]
                            links[count]["price"] = int(round(int(item["price"]["amount"]) / wax_precision, 0))
                            links[count]["token_symbol"] = item["price"]["token_symbol"]
                            if len(item["assets"]) > 1:
                                links[count]["land"] = []
                                for land in item["assets"]:
                                    try:
                                        links[count]["land"].append({"rarity": land["data"]["rarity"]})
                                    except KeyError:
                                        pass
                            else:
                                links[count]["land"] = {}
                                links[count]["land"]["rarity"] = item["assets"][0]["data"]["rarity"]
                                links[count]["land"]["available_space"] = item["assets"][0]["data"]["available_space"]
                                # links[count]["land"]["buildings"] = {}
                                # for building in item["assets"][0]["mutable_data"]:
                                # 	if not building in ["total_space", "available_space"]:
                                # 		links[count]["land"]["buildings"][building] = item["assets"][0]["mutable_data"][building]
                        return links
                    except KeyError as e:
                        print(e)
                        return None
                else:
                    return None
        except KeyError:
            # raise RequestException("Key data not found in request response text")
            return None

    def get_buildings(self) -> Union[Any, None]:
        '''
        Get onmars land.plots buildings

        Returns:
            None or json object containing data from request response
        '''

        data = None
        r = requests.get("https://wax.api.atomicassets.io/atomicassets/v1/schemas/onmars/land.plots")
        try:
            if r.status_code != 200:
                raise RequestException
            else:
                data = r.json()['data']['format']
                # print(data)
                return data
        except KeyError:
            # raise RequestException("Key data not found in request response text")
            return None

    def extract_data(self, json: Dict[str, Any], d: Any) -> List[Any]:
        data = []
        for item in json:
            data.append(item[d])
        return data
