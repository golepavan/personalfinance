"""
Splitwise API Client
Fetches expenses using API key (no OAuth required for local use)
"""

from splitwise import Splitwise
from typing import List, Dict, Optional, Set
from datetime import datetime
import os


class SplitwiseClient:
    """Client for interacting with Splitwise API"""
    
    def __init__(self, consumer_key: str, consumer_secret: str, api_key: str = None):
        """Initialize Splitwise client with API credentials"""
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_key = api_key
        self.client = None
        self.current_user = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Splitwise SDK client"""
        self.client = Splitwise(self.consumer_key, self.consumer_secret, api_key=self.api_key)
        try:
            self.current_user = self.client.getCurrentUser()
        except Exception as e:
            print(f"Warning: Could not get current user: {e}")
            self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.current_user is not None
    
    def get_current_user_info(self) -> Optional[Dict]:
        """Get current user information"""
        if not self.current_user:
            return None
        return {
            'id': self.current_user.getId(),
            'first_name': self.current_user.getFirstName(),
            'last_name': self.current_user.getLastName(),
            'email': self.current_user.getEmail()
        }
    
    def get_groups(self) -> List[Dict]:
        """Get all groups the user is part of"""
        groups = self.client.getGroups()
        return [
            {
                'id': g.getId(),
                'name': g.getName(),
                'type': g.getType()
            }
            for g in groups if g.getId() != 0  # Exclude non-group expenses
        ]
    
    def fetch_all_expenses(
        self,
        existing_ids: Set[int] = None,
        limit_per_request: int = 100,
        max_expenses: int = None,
        dated_after: str = None
    ) -> List[Dict]:
        """
        Fetch all expenses the user is involved in.
        Skips expenses that already exist in the provided set of IDs (unless dated_after is set, 
        in which case allow re-fetching to update local data).
        
        Args:
            existing_ids: Set of Splitwise expense IDs already in local DB
            limit_per_request: Number of expenses to fetch per API call
            max_expenses: Maximum total expenses to fetch (None for all)
            dated_after: ISO date string (YYYY-MM-DD) to fetch expenses after
        
        Returns:
            List of expense dictionaries (new or updated expenses)
        """
        if existing_ids is None:
            existing_ids = set()
        
        all_expenses = []
        offset = 0
        user_id = self.current_user.getId() if self.current_user else None
        
        # Build group name lookup
        groups = {g.getId(): g.getName() for g in self.client.getGroups()}
        
        while True:
            # Fetch batch of expenses
            expenses = self.client.getExpenses(offset=offset, limit=limit_per_request, dated_after=dated_after)
            
            if not expenses:
                break
            
            for expense in expenses:
                expense_id = expense.getId()
                
                # Skip if already in local DB AND we keep old behavior (no dated_after)
                # If dated_after is provided, we want to re-fetch even if ID exists (to update/undelete)
                if existing_ids and expense_id in existing_ids and not dated_after:
                   continue
                
                # Skip deleted expenses
                if expense.getDeletedAt():
                    continue
                
                # Get user's share from this expense
                user_share = self._get_user_share(expense, user_id)
                
                # Skip if user has no share
                if user_share == 0:
                    continue
                
                # Get payer info
                payer_id, payer_name = self._get_payer_info(expense)
                
                # Get group name
                group_id = expense.getGroupId()
                group_name = groups.get(group_id, 'Non-group expense')
                
                expense_data = {
                    'splitwise_id': expense_id,
                    'description': expense.getDescription() or 'No description',
                    'amount': float(expense.getCost() or 0),
                    'currency': expense.getCurrencyCode() or 'INR',
                    'date': expense.getDate()[:10] if expense.getDate() else datetime.now().strftime('%Y-%m-%d'),
                    'created_at': expense.getCreatedAt() or datetime.now().isoformat(),
                    'updated_at': expense.getUpdatedAt(),
                    'deleted_at': expense.getDeletedAt(),
                    'group_id': group_id,
                    'group_name': group_name,
                    'category': self._get_category(expense),
                    'payer_id': payer_id,
                    'payer_name': payer_name,
                    'user_share': user_share,
                    'is_payment': 1 if expense.getPayment() else 0
                }
                
                all_expenses.append(expense_data)
                
                # Check if we've reached max
                if max_expenses and len(all_expenses) >= max_expenses:
                    return all_expenses
            
            # Move to next batch
            offset += limit_per_request
            
            # If we got fewer than requested, we've reached the end
            if len(expenses) < limit_per_request:
                break
        
        return all_expenses
    
    def _get_user_share(self, expense, user_id: int) -> float:
        """Get the current user's share from an expense"""
        if not user_id:
            return 0
        
        users = expense.getUsers()
        for user in users:
            if user.getId() == user_id:
                owed = float(user.getOwedShare() or 0)
                return owed
        return 0
    
    def _get_payer_info(self, expense) -> tuple:
        """Get the payer's ID and name from an expense"""
        users = expense.getUsers()
        for user in users:
            paid = float(user.getPaidShare() or 0)
            if paid > 0:
                return user.getId(), user.getFirstName()
        return None, None
    
    def _get_category(self, expense) -> Optional[str]:
        """Get the category from an expense"""
        category = expense.getCategory()
        if category:
            return category.getName()
        return None
    
    def get_friends(self) -> List[Dict]:
        """Get list of friends with balances"""
        friends = self.client.getFriends()
        friend_data = []
        
        for f in friends:
            balances = []
            for b in f.getBalances():
                balances.append({
                    'currency': b.getCurrencyCode(),
                    'amount': float(b.getAmount())
                })
                
            friend_data.append({
                'id': f.getId(),
                'first_name': f.getFirstName(),
                'last_name': f.getLastName(),
                'email': f.getEmail(),
                'balances': balances
            })
            
        return friend_data
