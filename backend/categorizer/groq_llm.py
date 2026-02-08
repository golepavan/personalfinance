"""
Groq LLM Categorizer
Uses Groq's free Llama API for intelligent expense categorization
Categories aligned with Indian household expense patterns
"""

import os
import re
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


class GroqCategorizer:
    """Pure LLM-based expense categorizer using Groq (free Llama API)"""
    
    # Available categories for expense classification - aligned with tested results
    CATEGORIES = [
        'Grocery',           # General grocery shopping, supermarket
        'Dairy',             # Milk, curd, paneer, ghee, butter
        'Vegetables',        # All vegetables - palak, onion, tomato, potato, etc.
        'Fruits',            # Banana, apple, mango, etc.
        'Staples',           # Atta, rice, poha, suji - basic cooking staples
        'Cooking Oil',       # Sunflower oil, soybean oil, ghee for cooking
        'Spices',            # Jeera, haldi, mirchi, ginger, garlic
        'Pulses/Dals',       # Moong dal, toor dal, chana, urad dal
        'Food & Dining',     # Restaurants, food delivery, prepared meals
        'Snacks',            # Wada pav, samosa, biscuits, chips, namkeen
        'Household',         # Cleaning supplies, detergent, household items
        'Transport',         # Uber, Ola, auto, petrol, bus, train
        'Utilities',         # Electricity, water, gas bills
        'Mobile & Internet', # Mobile recharge, WiFi, broadband
        'Healthcare',        # Doctor, medicine, hospital
        'Shopping',          # Amazon, Flipkart, clothes, electronics
        'Entertainment',     # Movies, Netflix, parties
        'Personal Care',     # Salon, gym, grooming
        'Other'              # Uncategorized
    ]
    
    def __init__(self):
        """Initialize Groq client"""
        self.api_key = os.environ.get('GROQ_API_KEY')
        self.client = None
        self.model = "llama-3.3-70b-versatile"  # Larger, more accurate model
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                print(f"✅ Groq LLM Categorizer initialized (model: {self.model})")
            except ImportError:
                print("❌ Groq package not installed. Run: pip install groq")
            except Exception as e:
                print(f"❌ Groq init error: {e}")
        else:
            print("❌ GROQ_API_KEY not found in environment")
    
    def is_configured(self) -> bool:
        """Check if Groq is properly configured"""
        return self.client is not None
    
    def _build_prompt(self, descriptions: List[str]) -> str:
        """Build the categorization prompt optimized for Indian household expenses"""
        
        # Build numbered list of expenses
        expenses_list = "\n".join(f"{i}: {desc}" for i, desc in enumerate(descriptions))
        
        prompt = f"""You are an expense categorizer for an Indian household. Categorize each expense into exactly ONE category.

CATEGORIES AND EXAMPLES:

Grocery - General grocery shopping from stores/supermarkets, mixed items
  Examples: Grocery, Dmart, Zepto order

Dairy - Milk and milk products
  Examples: Milk, Dudh, Doodh, Curd, Dahi, Paneer, Ghee, Butter

Vegetables - Raw vegetables for cooking
  Examples: Palak, Kanda/Onion, Tomato, Aalu/Potato, Bhendi, Gobi, Mirchi, Methi, Gawar, Vange/Brinjal, Kobi

Fruits - Fresh fruits
  Examples: Keli/Banana, Apple, Anjeer, Orange, Mango

Staples - Basic cooking essentials stored for long time
  Examples: Atta, Rice, Poha, Suji, Besan

Cooking Oil - Oils used for cooking
  Examples: Sunflower oil, Soybean oil, Tel, Refined oil

Spices - Spices and condiments
  Examples: Jeera, Haldi, Mirchi powder, Ginger/Adrak, Garlic, Shengdana/Peanuts, Coriander powder

Pulses/Dals - Lentils and pulses
  Examples: Moong dal, Toor dal, Urad dal, Chana, Matki, Masoor

Food & Dining - Restaurant meals, prepared food, food delivery
  Examples: Shidori, Nashta, Chai, Coffee, Idli wada, Restaurant, Zomato, Swiggy

Snacks - Snack items, ready-to-eat treats
  Examples: Wada pav, Bhel, Biscuits, Parle, Chips, Namkeen

Household - Cleaning and home supplies
  Examples: Nirma, Detergent, Vim bar, Cloth rack, Washing powder

Transport - Travel and commute
  Examples: Uber, Ola, Auto, Petrol, Car expenses, Bus, Train, Metro

Other - Only if it truly doesn't fit any above category

RULES:
1. Mixed items with vegetables = Vegetables (e.g., "Palak+banana+tomato" = Vegetables)
2. Mixed items with dairy = Dairy (e.g., "Milk + biscuit" = Dairy)
3. Generic "Grocery" entries = Grocery
4. Cooked/prepared food = Food & Dining
5. NEVER use "General" - use the most specific category

Expenses to categorize:
{expenses_list}

Reply ONLY with: index:category (one per line). NO explanations."""
        
        return prompt
    
    def categorize_with_llm(self, descriptions: List[str], debug: bool = True) -> Dict:
        """
        Categorize expenses using Groq LLM.
        Returns both the raw response and parsed results.
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Groq not configured',
                'results': []
            }
        
        prompt = self._build_prompt(descriptions)
        
        if debug:
            print("\n" + "="*70)
            print("🦙 GROQ LLM REQUEST (Llama 3.1 8B)")
            print("="*70)
            print(f"Categorizing {len(descriptions)} expenses...")
            print("="*70)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expense categorizer. Only reply with id:category pairs, nothing else. Never use 'General' as a category."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent categorization
            )
            
            response_text = response.choices[0].message.content
            
            if debug:
                print("\n" + "="*70)
                print("✅ GROQ LLM RESPONSE")
                print("="*70)
                print(f"Raw Response:\n{response_text}")
                print("="*70 + "\n")
            
            # Parse the response
            results = self._parse_response(response_text, descriptions)
            
            return {
                'success': True,
                'raw_response': response_text,
                'prompt': prompt,
                'results': results
            }
            
        except Exception as e:
            error_msg = str(e)
            if debug:
                print(f"\n❌ Groq API error: {error_msg}\n")
            
            return {
                'success': False,
                'error': error_msg,
                'results': []
            }
    
    def _parse_response(self, response: str, descriptions: List[str]) -> List[Dict]:
        """Parse LLM response into structured results"""
        results = []
        parsed_indices = set()
        
        # Parse patterns like "0:Food" or "0: Food" or "0 - Food"
        pattern = r'(\d+)\s*[:\-]\s*([A-Za-z &/]+)'
        matches = re.findall(pattern, response)
        
        for idx_str, category in matches:
            idx = int(idx_str)
            category = category.strip()
            
            # Validate category - find matching category
            valid_category = None
            for cat in self.CATEGORIES:
                if cat.lower() == category.lower():
                    valid_category = cat
                    break
                # Partial match
                if category.lower() in cat.lower() or cat.lower() in category.lower():
                    valid_category = cat
                    break
            
            # Map "General" to "Other" if it somehow appears
            if category.lower() == 'general':
                valid_category = 'Other'
            
            if valid_category and idx < len(descriptions):
                results.append({
                    'index': idx,
                    'description': descriptions[idx],
                    'category': valid_category
                })
                parsed_indices.add(idx)
        
        # Add 'Other' for any unparsed descriptions
        for i, desc in enumerate(descriptions):
            if i not in parsed_indices:
                results.append({
                    'index': i,
                    'description': desc,
                    'category': 'Other'
                })
        
        # Sort by index
        results.sort(key=lambda x: x['index'])
        
        return results
    
    def categorize_batch(self, expenses: List[Dict], batch_size: int = 20) -> List[Dict]:
        """Categorize a batch of expenses for database update"""
        all_results = []
        
        for i in range(0, len(expenses), batch_size):
            batch = expenses[i:i + batch_size]
            descriptions = [e.get('description', '') for e in batch]
            ids = [e.get('splitwise_id') or e.get('id') for e in batch]
            
            response = self.categorize_with_llm(descriptions, debug=True)
            
            if response['success']:
                for result in response['results']:
                    idx = result['index']
                    if idx < len(ids):
                        all_results.append({
                            'splitwise_id': ids[idx],
                            'category': result['category']
                        })
            else:
                # On error, assign 'Other' to all in batch
                for exp_id in ids:
                    all_results.append({
                        'splitwise_id': exp_id,
                        'category': 'Other'
                    })
        
        return all_results
    
    def categorize_single(self, description: str) -> str:
        """Categorize a single expense"""
        response = self.categorize_with_llm([description], debug=False)
        
        if response['success'] and response['results']:
            return response['results'][0]['category']
        return 'Other'
