# research/retrievers/brave.py

import os
import requests


class BraveSearch:
    """
    Brave API Retriever
    """

    def __init__(self, query, headers=None, topic="general", query_domains=None, count=10):
        """
        Initializes the BraveSearch object.

        Args:
            query (str): The search query string.
            headers (dict, optional): Extra headers. Defaults to None.
            count (int, optional): Number of results. Defaults to 10.
        """
        self.query = query
        self.count = count
        self.headers = headers or {}
        self.topic = topic
        self.query_domains = query_domains or None
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = self.get_api_key()
        self.headers.update({
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        })

    def get_api_key(self):
        """
        Gets the Brave API key
        """
        api_key = self.headers.get("brave_api_key")
        if not api_key:
            try:
                api_key = os.environ["BRAVE_API_KEY"]
            except KeyError:
                print(
                    "Brave API key not found. Please set BRAVE_API_KEY environment variable."
                )
                return ""
        return api_key

    def _search(self, query: str, count: int = 10) -> dict:
        """
        Internal search method to send the request to the Brave API.
        """
        params = {"q": query, "count": count}
        response = requests.get(
            self.base_url, headers=self.headers, params=params, timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def search(self, max_results=10):
        """
        Searches the query
        """
        try:
            results = self._search(self.query, count=max_results)
            sources = results.get("web", {}).get("results", [])
            if not sources:
                raise Exception("No results found with Brave API search.")
            # Return results like Tavily does
            search_response = [
                {"href": obj["url"], "body": obj.get("description", "")}
                for obj in sources
            ]
        except Exception as e:
            print(f"Error: {e}. Failed fetching sources. Returning empty response.")
            search_response = []
        return search_response
