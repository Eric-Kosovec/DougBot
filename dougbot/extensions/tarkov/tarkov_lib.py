import aiohttp

# https://api.tarkov.dev/

_API_URL = 'https://api.tarkov.dev/graphql'


class TarkovLib:

    @staticmethod
    async def get_items(item: str) -> list:
        query = """
            query GetItems($name: String) {
              items(name: $name) {
                id
                name
              }
            }
        """
        result = await TarkovLib._run_query(query, {"name": item})
        return result['data']['items']

    @staticmethod
    async def get_item(item_id: str) -> dict:
        query = """
            query GetItem($id: ID!) {
              item(id: $id) {
                id
                name
                image8xLink
                sellFor {
                  vendor {
                    name
                  }
                  price
                  currency
                }
              }
            }
        """
        result = await TarkovLib._run_query(query, {"id": item_id})
        return result['data']['item']

    @staticmethod
    async def _run_query(query: str, variables: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(_API_URL, json={'query': query, 'variables': variables}) as response:
                if response.status != 200:
                    raise Exception(f"Tarkov API query failed with status {response.status}")

                body = await response.json()
                if 'errors' in body:
                    raise Exception(f"Tarkov API returned errors: {body['errors']}")

                return body