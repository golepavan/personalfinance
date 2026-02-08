"""
Gemini AI Categorizer
Uses Google's Gemini API for smart expense categorization
Optimized for minimal token usage to stay within quota limits
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import re


class GeminiCategorizer:
    """AI categorizer using Gemini API with token optimization"""
    
    # Compact category codes for token efficiency
    CATEGORY_CODES = {
        'F': 'Food',
        'G': 'Grocery',
        'T': 'Transport',
        'D': 'Daily Essentials',
        'S': 'Shopping',
        'E': 'Entertainment',
        'U': 'Utilities',
        'R': 'Rent',
        'V': 'Travel',
        'H': 'Healthcare',
        'B': 'Subscriptions',
        'L': 'Education',
        'P': 'Personal Care',
        'W': 'Work',
        'C': 'Cravings',
        'Y': 'Cylinder',
        'O': 'Other'
    }
    
    # Reverse mapping
    CODE_TO_CATEGORY = {v: v for v in CATEGORY_CODES.values()}
    
    # Category keywords for fallback local categorization
    KEYWORD_CATEGORIES = {
        'Food': ['restaurant', 'food', 'lunch', 'dinner', 'breakfast', 'cafe', 'pizza', 
                 'burger', 'biryani', 'dosa', 'meal', 'snack', 'eat', 'swiggy', 'zomato',
                 'thali', 'paratha', 'chai', 'coffee', 'canteen', 'mess', 'tiffin'],
        'Grocery': ['grocery', 'vegetables', 'fruits', 'mart', 'supermarket', 'store',
                    'kirana', 'dmart', 'bigbasket', 'blinkit', 'zepto', 'instamart',
                    'reliance fresh', 'more', 'spar', 'nature basket'],
        'Transport': ['uber', 'ola', 'auto', 'cab', 'taxi', 'petrol', 'fuel', 'diesel',
                      'metro', 'bus', 'train', 'parking', 'toll', 'rapido', 'bike taxi'],
        'Daily Essentials': ['milk', 'bread', 'eggs', 'water', 'daily', 'essentials',
                             'soap', 'toothpaste', 'household', 'detergent', 'tissue',
                             'toilet paper', 'cleaning', 'mop', 'broom'],
        'Shopping': ['amazon', 'flipkart', 'myntra', 'shopping', 'clothes', 'shoes',
                     'electronics', 'gadget', 'purchase', 'meesho', 'ajio', 'nykaa'],
        'Entertainment': ['movie', 'netflix', 'prime', 'hotstar', 'spotify', 'game',
                          'concert', 'event', 'party', 'fun', 'outing', 'pub', 'bar'],
        'Utilities': ['electricity', 'electric bill', 'gas', 'water bill', 'internet', 
                      'wifi', 'broadband', 'phone', 'recharge', 'bill', 'postpaid',
                      'prepaid', 'mobile recharge', 'airtel', 'jio', 'vi', 'bsnl',
                      'act fibernet', 'tata sky', 'dth'],
        'Rent': ['rent', 'house rent', 'room rent', 'pg', 'accommodation', 'lease',
                 'maintenance', 'society'],
        'Travel': ['flight', 'hotel', 'trip', 'vacation', 'holiday', 'booking',
                   'airbnb', 'makemytrip', 'goibibo', 'travel', 'oyo', 'treebo'],
        'Healthcare': ['doctor', 'medicine', 'hospital', 'pharmacy', 'medical',
                       'health', 'clinic', 'checkup', 'test', 'lab', 'apollo',
                       'pharmeasy', 'netmeds', '1mg', 'practo'],
        'Subscriptions': ['subscription', 'membership', 'premium', 'annual', 'monthly',
                          'youtube premium', 'apple music', 'icloud', 'google one'],
        'Education': ['course', 'book', 'education', 'class', 'tuition', 'fees',
                      'udemy', 'coursera', 'learning', 'exam', 'certificate', 'notes'],
        'Personal Care': ['salon', 'haircut', 'spa', 'gym', 'fitness', 'grooming',
                          'beauty', 'skincare', 'parlour', 'facial', 'massage'],
        'Work': ['office', 'work', 'stationery', 'notebook', 'pen', 'printer', 
                 'laptop', 'mouse', 'keyboard', 'desk', 'chair', 'monitor',
                 'headphones', 'webcam', 'usb', 'cable', 'charger'],
        'Cravings': ['ice cream', 'chocolate', 'sweet', 'dessert', 'cake', 'pastry',
                     'cookie', 'brownie', 'kulfi', 'falooda', 'shake', 'smoothie',
                     'chips', 'namkeen', 'bhujia', 'wafer', 'candy', 'mithai'],
        'Cylinder': ['cylinder', 'lpg', 'gas cylinder', 'cooking gas', 'hp gas',
                     'indane', 'bharat gas', 'refill']
    }
    
    def __init__(self, api_key: str, model: str = 'gemini-2.0-flash'):
        """Initialize Gemini client with API key"""
        self.api_key = api_key
        self.model_name = model
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client"""
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
    
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key and self.model)
    
    def _compact_description(self, description: str) -> str:
        """Compact description for minimal tokens"""
        # Remove extra whitespace
        desc = ' '.join(description.split())
        # Remove common noise words
        noise = ['payment', 'for', 'the', 'at', 'to', 'from', 'and', 'or', 'in', 'on', 'a', 'an']
        words = desc.lower().split()
        words = [w for w in words if w not in noise and len(w) > 1]
        # Keep first 5 meaningful words max
        return ' '.join(words[:5])
    
    def categorize_local(self, description: str) -> Optional[str]:
        """
        Categorize using local keyword matching (no API call).
        Use this as fallback or to reduce API usage.
        """
        desc_lower = description.lower()
        
        for category, keywords in self.KEYWORD_CATEGORIES.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return category
        
        return None
    
    def categorize_batch(
        self,
        expenses: List[Dict],
        batch_size: int = 20,
        use_local_fallback: bool = True
    ) -> List[Dict]:
        """
        Categorize expenses in batches with minimal API calls.
        
        Args:
            expenses: List of {'id': ..., 'description': ...}
            batch_size: Number of items per API call
            use_local_fallback: Try local categorization first
        
        Returns:
            List of {'id': ..., 'category': ...}
        """
        results = []
        to_categorize_api = []
        
        # First pass: try local categorization
        for expense in expenses:
            exp_id = expense.get('splitwise_id') or expense.get('id')
            description = expense.get('description', '')
            
            if use_local_fallback:
                local_category = self.categorize_local(description)
                if local_category:
                    results.append({'splitwise_id': exp_id, 'category': local_category})
                    continue
            
            to_categorize_api.append(expense)
        
        # If no API client or no items left, return
        if not self.is_configured() or not to_categorize_api:
            # Assign 'Other' to remaining
            for expense in to_categorize_api:
                exp_id = expense.get('splitwise_id') or expense.get('id')
                results.append({'splitwise_id': exp_id, 'category': 'Other'})
            return results
        
        # Second pass: batch API categorization
        for i in range(0, len(to_categorize_api), batch_size):
            batch = to_categorize_api[i:i + batch_size]
            batch_results = self._categorize_with_api(batch)
            results.extend(batch_results)
        
        return results
    
    def _categorize_with_api(self, expenses: List[Dict]) -> List[Dict]:
        """Call Gemini API to categorize a batch of expenses"""
        if not expenses:
            return []
        
        # Build compact prompt
        # Format: "Categorize:desc1|desc2|desc3"
        descriptions = []
        id_map = {}
        
        for idx, expense in enumerate(expenses):
            exp_id = expense.get('splitwise_id') or expense.get('id')
            desc = self._compact_description(expense.get('description', ''))
            descriptions.append(desc)
            id_map[idx] = exp_id
        
        # Build ultra-compact prompt
        prompt = f"""Cat:{"|".join(descriptions)}
Reply idx:cat (F=Food,G=Grocery,T=Transport,D=DailyEss,S=Shop,E=Ent,U=Util,R=Rent,V=Travel,H=Health,B=Sub,L=Edu,P=Personal,W=Work,C=Cravings,Y=Cylinder,O=Other)
Only idx:cat pairs, no explanation"""
        
        # DEBUG: Log the request
        print("\n" + "="*60)
        print("🤖 GEMINI API REQUEST")
        print("="*60)
        print(f"Prompt:\n{prompt}")
        print("="*60)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': 100,
                    'temperature': 0.1
                }
            )
            
            # DEBUG: Log the response
            print("\n" + "="*60)
            print("✅ GEMINI API RESPONSE")
            print("="*60)
            print(f"Response: {response.text}")
            print("="*60 + "\n")
            
            return self._parse_api_response(response.text, id_map, len(expenses))
            
        except Exception as e:
            print(f"\n❌ Gemini API error: {e}\n")
            # Return 'Other' for all on error
            return [{'splitwise_id': id_map[i], 'category': 'Other'} for i in range(len(expenses))]
    
    def _parse_api_response(self, response: str, id_map: Dict[int, int], count: int) -> List[Dict]:
        """Parse the compact API response"""
        results = []
        
        # Parse patterns like "0:F" or "0:F,1:G" or "0:F 1:G"
        pattern = r'(\d+)\s*:\s*([FGTDSEURVHBLPWCYO])'
        matches = re.findall(pattern, response.upper())
        
        found_indices = set()
        for idx_str, code in matches:
            idx = int(idx_str)
            if idx in id_map and idx not in found_indices:
                category = self.CATEGORY_CODES.get(code, 'Other')
                results.append({'splitwise_id': id_map[idx], 'category': category})
                found_indices.add(idx)
        
        # Fill missing with 'Other'
        for i in range(count):
            if i not in found_indices and i in id_map:
                results.append({'splitwise_id': id_map[i], 'category': 'Other'})
        
        return results
    
    def categorize_single(self, description: str) -> str:
        """Categorize a single expense (tries local first)"""
        local = self.categorize_local(description)
        if local:
            return local
        
        if not self.is_configured():
            return 'Other'
        
        # Single item API call (expensive, avoid if possible)
        result = self._categorize_with_api([{'id': 0, 'description': description}])
        return result[0]['category'] if result else 'Other'
