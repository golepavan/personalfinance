"""
Smart Local Categorizer
Uses enhanced pattern matching and optional Groq/Ollama for AI categorization
No Gemini quota limits - completely local or uses free tier APIs
"""

import re
import os
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


class SmartCategorizer:
    """Smart expense categorizer with local-first approach"""
    
    # Extended category patterns with regex support
    CATEGORY_PATTERNS = {
        'Food': {
            'keywords': [
                'food', 'lunch', 'dinner', 'breakfast', 'meal', 'eat', 'snack',
                'restaurant', 'cafe', 'hotel', 'dhaba', 'canteen', 'mess', 'tiffin',
                'pizza', 'burger', 'biryani', 'dosa', 'idli', 'thali', 'paratha',
                'noodles', 'momos', 'chaat', 'samosa', 'pav bhaji', 'chole', 
                'pani puri', 'vada pav', 'sandwich', 'roll', 'wrap', 'pasta',
                'chai', 'coffee', 'tea', 'juice', 'lassi', 'shake',
                'swiggy', 'zomato', 'ubereats', 'foodpanda', 'dunzo'
            ],
            'patterns': [r'.*order.*food', r'.*ordered.*', r'.*eating.*out']
        },
        'Grocery': {
            'keywords': [
                'grocery', 'groceries', 'vegetables', 'vegetable', 'fruits', 'fruit',
                'mart', 'supermarket', 'store', 'kirana', 'bazaar', 'market',
                'dmart', 'bigbasket', 'blinkit', 'zepto', 'instamart', 'jiomart',
                'reliance', 'spar', 'more', 'spencers', 'star bazaar',
                'onion', 'potato', 'tomato', 'rice', 'dal', 'atta', 'flour',
                'oil', 'ghee', 'masala', 'spices', 'salt', 'sugar',
                'banana', 'apple', 'mango', 'orange', 'grapes', 'papaya',
                'mirchi', 'kothimbir', 'coriander', 'methi', 'palak', 'bhindi'
            ],
            'patterns': [r'.*sabzi.*', r'.*ration.*', r'.*provisions.*']
        },
        'Transport': {
            'keywords': [
                'uber', 'ola', 'auto', 'cab', 'taxi', 'ride', 'rapido',
                'petrol', 'fuel', 'diesel', 'cng', 'gas station', 'pump',
                'metro', 'bus', 'train', 'railway', 'irctc', 'local',
                'parking', 'toll', 'fastag', 'challan',
                'car', 'bike', 'scooter', 'vehicle', 'service', 'repair'
            ],
            'patterns': [r'.*ride.*to.*', r'.*trip.*to.*', r'.*office.*commute']
        },
        'Daily Essentials': {
            'keywords': [
                'milk', 'bread', 'eggs', 'egg', 'butter', 'cheese', 'curd', 'paneer',
                'water', 'bisleri', 'kinley', 'aquafina',
                'soap', 'shampoo', 'toothpaste', 'toothbrush', 'detergent',
                'tissue', 'toilet paper', 'cleaning', 'mop', 'broom', 'phenyl',
                'dish wash', 'vim', 'surf', 'harpic', 'lizol', 'colin',
                'matchbox', 'candle', 'agarbatti'
            ],
            'patterns': [r'.*daily.*need', r'.*essential.*', r'.*household.*']
        },
        'Shopping': {
            'keywords': [
                'amazon', 'flipkart', 'myntra', 'meesho', 'ajio', 'nykaa',
                'shopping', 'shop', 'purchase', 'bought', 'buy',
                'clothes', 'clothing', 'shirt', 'pant', 'jeans', 't-shirt', 'kurta',
                'shoes', 'footwear', 'sandals', 'slippers', 'sneakers',
                'electronics', 'gadget', 'phone', 'mobile', 'watch', 'bag'
            ],
            'patterns': [r'.*online.*order', r'.*delivered.*', r'.*parcel.*']
        },
        'Entertainment': {
            'keywords': [
                'movie', 'cinema', 'theatre', 'pvr', 'inox', 'multiplex',
                'netflix', 'prime', 'hotstar', 'disney', 'zee5', 'sony liv',
                'spotify', 'music', 'concert', 'show', 'event', 'ticket',
                'game', 'gaming', 'playstation', 'xbox', 'steam',
                'party', 'celebration', 'birthday', 'anniversary',
                'pub', 'bar', 'club', 'lounge', 'drinks', 'beer', 'whisky',
                'outing', 'fun', 'picnic', 'trek', 'adventure'
            ],
            'patterns': [r'.*night.*out', r'.*hangout.*', r'.*chill.*']
        },
        'Utilities': {
            'keywords': [
                'electricity', 'electric', 'power', 'mseb', 'tata power', 'adani',
                'bill', 'payment', 'emi', 'installment',
                'internet', 'wifi', 'broadband', 'fiber', 'act fibernet',
                'tata sky', 'dth', 'dish tv', 'd2h', 'cable'
            ],
            'patterns': [r'.*utility.*bill', r'.*monthly.*bill']
        },
        'Mobile Recharges': {
            'keywords': [
                'recharge', 'mobile recharge', 'prepaid', 'postpaid',
                'airtel', 'jio', 'vi', 'vodafone', 'idea', 'bsnl', 'mtnl',
                'data pack', 'validity', 'talktime', 'top up', 'topup'
            ],
            'patterns': [r'.*mobile.*plan', r'.*phone.*recharge']
        },
        'WiFi': {
            'keywords': [
                'wifi', 'wi-fi', 'internet bill', 'broadband bill',
                'act fibernet', 'airtel xstream', 'jiofiber', 'hathway',
                'you broadband', 'tikona', 'spectra net', 'local cable'
            ],
            'patterns': [r'.*internet.*payment', r'.*broadband.*']
        },
        'Electricity': {
            'keywords': [
                'electricity bill', 'electric bill', 'power bill', 'bijli',
                'mseb', 'msedcl', 'tata power', 'adani electricity', 'torrent power',
                'bses', 'brpl', 'ndpl', 'bescom', 'tneb', 'pspcl'
            ],
            'patterns': [r'.*light.*bill', r'.*power.*payment']
        },
        'Cylinder': {
            'keywords': [
                'cylinder', 'lpg', 'gas cylinder', 'cooking gas', 'gas refill',
                'hp gas', 'indane', 'bharat gas', 'bharat petroleum',
                'hindustan petroleum', 'iocl', 'gas booking', 'lpg refill'
            ],
            'patterns': [r'.*gas.*refill', r'.*lpg.*booking']
        },
        'Rent': {
            'keywords': [
                'rent', 'house rent', 'room rent', 'flat rent', 'apartment',
                'pg', 'paying guest', 'hostel', 'accommodation',
                'lease', 'deposit', 'security deposit', 'advance',
                'maintenance', 'society', 'association', 'hoa'
            ],
            'patterns': [r'.*monthly.*rent', r'.*room.*payment']
        },
        'Travel': {
            'keywords': [
                'flight', 'airplane', 'air ticket', 'indigo', 'spicejet', 'vistara',
                'hotel', 'resort', 'stay', 'booking', 'reservation',
                'trip', 'vacation', 'holiday', 'tour', 'travel',
                'airbnb', 'oyo', 'treebo', 'fabhotel', 'zostel',
                'makemytrip', 'goibibo', 'yatra', 'cleartrip', 'ixigo',
                'redbus', 'abhibus', 'volvo', 'sleeper', 'railways'
            ],
            'patterns': [r'.*holiday.*trip', r'.*vacation.*booking']
        },
        'Healthcare': {
            'keywords': [
                'doctor', 'hospital', 'clinic', 'medical', 'health',
                'medicine', 'pharmacy', 'chemist', 'tablets', 'syrup', 'capsule',
                'test', 'lab', 'diagnostic', 'pathology', 'blood test', 'xray',
                'checkup', 'consultation', 'appointment', 'opd',
                'apollo', 'fortis', 'max', 'medanta', 'narayana',
                'pharmeasy', 'netmeds', '1mg', 'medplus', 'practo',
                'insurance', 'premium', 'health insurance', 'mediclaim'
            ],
            'patterns': [r'.*medical.*expense', r'.*health.*care']
        },
        'Subscriptions': {
            'keywords': [
                'subscription', 'subscribe', 'membership', 'premium', 'pro',
                'annual', 'yearly', 'monthly subscription',
                'youtube premium', 'yt premium', 'apple music', 'amazon prime',
                'icloud', 'google one', 'dropbox', 'notion', 'slack',
                'linkedin', 'canva', 'grammarly', 'microsoft 365', 'office 365'
            ],
            'patterns': [r'.*recurring.*payment', r'.*auto.*renewal']
        },
        'Education': {
            'keywords': [
                'course', 'class', 'tuition', 'coaching', 'tutorial',
                'book', 'notebook', 'textbook', 'stationery', 'notes',
                'fees', 'college', 'school', 'university', 'institute',
                'udemy', 'coursera', 'skillshare', 'linkedin learning',
                'unacademy', 'byjus', 'testbook', 'upgrad', 'emeritus',
                'exam', 'test', 'certificate', 'diploma', 'degree'
            ],
            'patterns': [r'.*learning.*', r'.*study.*material']
        },
        'Personal Care': {
            'keywords': [
                'salon', 'haircut', 'hair', 'barber', 'shave', 'trim',
                'spa', 'massage', 'facial', 'beauty', 'parlour', 'parlor',
                'gym', 'fitness', 'workout', 'yoga', 'zumba',
                'grooming', 'skincare', 'cream', 'lotion', 'moisturizer',
                'makeup', 'cosmetics', 'lipstick', 'kajal', 'foundation'
            ],
            'patterns': [r'.*self.*care', r'.*wellness.*']
        },
        'Work': {
            'keywords': [
                'office', 'work', 'professional', 'business',
                'stationery', 'pen', 'pencil', 'marker', 'highlighter',
                'notebook', 'file', 'folder', 'stapler', 'tape',
                'laptop', 'computer', 'pc', 'monitor', 'keyboard', 'mouse',
                'desk', 'chair', 'table', 'lamp', 'stand',
                'headphones', 'earphones', 'webcam', 'mic', 'microphone',
                'usb', 'cable', 'charger', 'adapter', 'hub', 'dock'
            ],
            'patterns': [r'.*office.*supply', r'.*work.*from.*home']
        },
        'Cravings': {
            'keywords': [
                'ice cream', 'icecream', 'gelato', 'kulfi', 'sundae',
                'chocolate', 'cadbury', 'kitkat', 'oreo', 'ferrero',
                'sweet', 'dessert', 'mithai', 'ladoo', 'barfi', 'jalebi', 'gulab jamun',
                'cake', 'pastry', 'brownie', 'cookie', 'donut', 'cupcake',
                'chips', 'namkeen', 'bhujia', 'mixture', 'wafer', 'kurkure',
                'falooda', 'shake', 'milkshake', 'smoothie', 'frappe',
                'candy', 'toffee', 'lollipop', 'gummy'
            ],
            'patterns': [r'.*late.*night.*snack', r'.*treat.*']
        }
    }
    
    def __init__(self, use_groq: bool = True):
        """Initialize categorizer"""
        self.use_groq = use_groq
        self.groq_client = None
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        
        if self.use_groq and self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                print("✅ Groq client initialized (free Llama API)")
            except ImportError:
                print("⚠️ Groq not installed. Run: pip install groq")
            except Exception as e:
                print(f"⚠️ Groq init error: {e}")
    
    def is_groq_available(self) -> bool:
        """Check if Groq API is available"""
        return self.groq_client is not None
    
    def _normalize(self, text: str) -> str:
        """Normalize text for matching"""
        text = text.lower().strip()
        # Remove special chars but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _local_categorize(self, description: str) -> Optional[str]:
        """Categorize using local pattern matching"""
        normalized = self._normalize(description)
        
        # Score each category
        scores = {}
        for category, data in self.CATEGORY_PATTERNS.items():
            score = 0
            
            # Check keywords (fuzzy matching)
            # Multi-word keywords get higher score
            for keyword in data['keywords']:
                if keyword in normalized:
                    # Multi-word keywords get bonus (ice cream vs cream)
                    word_count = len(keyword.split())
                    score += 2 * word_count  # Multi-word match bonus
                elif len(keyword) > 3 and any(word.startswith(keyword[:4]) for word in normalized.split()):
                    score += 1  # Partial match
            
            # Check regex patterns
            for pattern in data.get('patterns', []):
                if re.search(pattern, normalized):
                    score += 3  # Pattern match
            
            if score > 0:
                scores[category] = score
        
        if scores:
            # Return highest scoring category
            return max(scores, key=scores.get)
        
        return None
    
    def _groq_categorize(self, descriptions: List[str]) -> Dict[int, str]:
        """Use Groq (free Llama) for categorization"""
        if not self.groq_client:
            return {}
        
        categories_list = list(self.CATEGORY_PATTERNS.keys()) + ['Other']
        
        prompt = f"""Categorize these expenses into one of: {', '.join(categories_list)}

Expenses:
{chr(10).join(f'{i}: {d}' for i, d in enumerate(descriptions))}

Reply with ONLY the format "id:category" for each, one per line. Example:
0:Food
1:Transport
2:Grocery"""
        
        print("\n" + "="*60)
        print("🦙 GROQ (LLAMA) API REQUEST")
        print("="*60)
        print(f"Prompt:\n{prompt[:500]}...")
        print("="*60)
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Free, fast model
                messages=[
                    {"role": "system", "content": "You are an expense categorizer. Reply only with id:category pairs."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content
            
            print("\n" + "="*60)
            print("✅ GROQ API RESPONSE")
            print("="*60)
            print(f"Response: {response_text}")
            print("="*60 + "\n")
            
            # Parse response
            result = {}
            for line in response_text.strip().split('\n'):
                match = re.match(r'(\d+)\s*:\s*(.+)', line.strip())
                if match:
                    idx = int(match.group(1))
                    cat = match.group(2).strip()
                    # Validate category
                    if cat in categories_list:
                        result[idx] = cat
                    else:
                        # Find closest match
                        for valid_cat in categories_list:
                            if valid_cat.lower() in cat.lower() or cat.lower() in valid_cat.lower():
                                result[idx] = valid_cat
                                break
            
            return result
            
        except Exception as e:
            print(f"\n❌ Groq API error: {e}\n")
            return {}
    
    def categorize_batch(self, expenses: List[Dict], batch_size: int = 15) -> List[Dict]:
        """Categorize a batch of expenses"""
        results = []
        to_categorize_api = []
        
        # First pass: local categorization
        for expense in expenses:
            exp_id = expense.get('splitwise_id') or expense.get('id')
            description = expense.get('description', '')
            
            category = self._local_categorize(description)
            
            if category:
                results.append({'splitwise_id': exp_id, 'category': category})
            else:
                to_categorize_api.append((exp_id, description))
        
        # Second pass: API categorization for unknowns
        if to_categorize_api and self.is_groq_available():
            for i in range(0, len(to_categorize_api), batch_size):
                batch = to_categorize_api[i:i + batch_size]
                descriptions = [d for _, d in batch]
                
                api_results = self._groq_categorize(descriptions)
                
                for batch_idx, (exp_id, _) in enumerate(batch):
                    category = api_results.get(batch_idx, 'Other')
                    results.append({'splitwise_id': exp_id, 'category': category})
        else:
            # No API available, default to 'Other'
            for exp_id, _ in to_categorize_api:
                results.append({'splitwise_id': exp_id, 'category': 'Other'})
        
        return results
    
    def categorize_single(self, description: str) -> str:
        """Categorize a single expense"""
        category = self._local_categorize(description)
        return category or 'Other'
