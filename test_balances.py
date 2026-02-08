from backend.splitwise_api.client import SplitwiseClient
from backend.config import Config
import json

def test_friends_balances():
    client = SplitwiseClient(
        consumer_key=Config.SPLITWISE_CONSUMER_KEY,
        consumer_secret=Config.SPLITWISE_CONSUMER_SECRET,
        api_key=Config.SPLITWISE_API_KEY
    )
    
    if not client.is_authenticated():
        print("Not authenticated")
        return

    print("Fetching friends...")
    friends = client.client.getFriends()
    
    for friend in friends:
        print(f"Friend: {friend.getFirstName()} {friend.getLastName()}")
        balances = friend.getBalances()
        for balance in balances:
            print(f"  - Currency: {balance.getCurrencyCode()}, Amount: {balance.getAmount()}")

if __name__ == "__main__":
    test_friends_balances()
