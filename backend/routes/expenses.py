"""
Expense API Routes
Handles expense CRUD, analytics, and sync operations
"""

from flask import Blueprint, request, jsonify, current_app
from database.db_manager import DatabaseManager
from splitwise_api.client import SplitwiseClient
from categorizer.groq_llm import GroqCategorizer
from config import Config

expenses_bp = Blueprint('expenses', __name__)


def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    db_path = current_app.config.get('DATABASE_PATH', 'splitwise_data.db')
    return DatabaseManager(db_path)


def get_splitwise_client() -> SplitwiseClient:
    """Get Splitwise client instance"""
    return SplitwiseClient(
        consumer_key=Config.SPLITWISE_CONSUMER_KEY,
        consumer_secret=Config.SPLITWISE_CONSUMER_SECRET,
        api_key=Config.SPLITWISE_API_KEY
    )


def get_categorizer() -> GroqCategorizer:
    """Get Groq LLM categorizer instance (pure LLM, no keywords)"""
    return GroqCategorizer()


@expenses_bp.route('/sync', methods=['POST'])
def sync_expenses():
    """
    Sync new expenses from Splitwise.
    Only fetches expenses not already in local database.
    """
    try:
        db = get_db_manager()
        sw_client = get_splitwise_client()
        
        if not sw_client.is_authenticated():
            return jsonify({
                'success': False,
                'error': 'Not authenticated with Splitwise. Please check API credentials.'
            }), 401
        
        # Get params
        data = request.get_json() or {}
        dated_after = data.get('dated_after')

        # Get existing expense IDs
        existing_ids = db.get_existing_expense_ids()
        
        # Fetch expenses (pass dated_after to allow re-fetch)
        new_expenses = sw_client.fetch_all_expenses(
            existing_ids=existing_ids, 
            dated_after=dated_after
        )
        
        if not new_expenses:
            return jsonify({
                'success': True,
                'message': 'No new expenses to sync',
                'synced_count': 0,
                'total_count': len(existing_ids)
            })
        
        # Insert new expenses
        inserted = db.insert_expenses(new_expenses)
        
        # Get uncategorized expenses and categorize them
        # Categorize ONLY the new expenses
        expenses_to_categorize = [
            {'splitwise_id': e['id'], 'description': e['description']}
            for e in new_expenses 
            if e.get('payment') is False and e.get('deleted_at') is None
        ]
        
        if expenses_to_categorize:
            categorizer = get_categorizer()
            categories = categorizer.categorize_batch(expenses_to_categorize)
            db.bulk_update_categories(categories)
        
        # Update sync metadata
        last_date = new_expenses[0]['date'] if new_expenses else None
        db.update_sync_meta(last_expense_date=last_date, count=inserted)
        
        return jsonify({
            'success': True,
            'message': f'Synced {inserted} new expenses',
            'synced_count': inserted,
            'categorized_count': len(expenses_to_categorize),
            'total_count': len(existing_ids) + inserted
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses with optional filters"""
    try:
        db = get_db_manager()
        
        filters = {
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
            'category': request.args.get('category'),
            'group_id': request.args.get('group_id')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v}
        
        expenses = db.get_all_expenses(filters if filters else None)
        
        return jsonify({
            'success': True,
            'expenses': expenses,
            'count': len(expenses)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    """Get monthly expense breakdown"""
    try:
        db = get_db_manager()
        year = request.args.get('year')
        monthly_data = db.get_monthly_analytics(year=year)
        
        return jsonify({
            'success': True,
            'data': monthly_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/analytics/yearly', methods=['GET'])
def get_yearly_analytics():
    """Get yearly expense breakdown"""
    try:
        db = get_db_manager()
        yearly_data = db.get_yearly_analytics()
        
        return jsonify({
            'success': True,
            'data': yearly_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/categories', methods=['GET'])
def get_category_breakdown():
    """Get expense breakdown by category"""
    try:
        db = get_db_manager()
        
        year = request.args.get('year')
        month = request.args.get('month')
        
        categories = db.get_category_breakdown(year=year, month=month)
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/sync-status', methods=['GET'])
def get_sync_status():
    """Get sync status information"""
    try:
        db = get_db_manager()
        status = db.get_sync_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/recategorize', methods=['POST'])
def recategorize_expenses():
    """Recategorize expenses. Use ?force=true to recategorize ALL expenses."""
    try:
        db = get_db_manager()
        categorizer = get_categorizer()
        
        # Check if force recategorize all
        force = request.args.get('force', 'false').lower() == 'true'
        
        # Parse filters
        filters = {
            'year': request.args.get('year'),
            'month': request.args.get('month')
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v}
        
        if force:
            # Get ALL expenses for recategorization (with optional filters)
            all_expenses = db.get_all_expenses(filters if filters else None)
            expenses_to_categorize = [
                {'splitwise_id': e['splitwise_id'], 'description': e['description']}
                for e in all_expenses
            ]
        else:
            # Get only uncategorized expenses (with optional filters)
            expenses_to_categorize = db.get_uncategorized_expenses(filters)
        
        if not expenses_to_categorize:
            return jsonify({
                'success': True,
                'message': 'No expenses to categorize',
                'categorized_count': 0
            })
        
        categories = categorizer.categorize_batch(expenses_to_categorize)
        db.bulk_update_categories(categories)
        
        return jsonify({
            'success': True,
            'message': f'Categorized {len(categories)} expenses',
            'categorized_count': len(categories)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get all dashboard data in one call"""
    try:
        db = get_db_manager()
        
        # Get all data
        monthly = db.get_monthly_analytics()
        yearly = db.get_yearly_analytics()
        categories = db.get_category_breakdown()
        
        # Get recent expenses (last 10)
        all_expenses = db.get_all_expenses()
        recent = all_expenses[:10] if all_expenses else []
        
        # Calculate totals
        total_expenses = sum(e['user_share'] for e in all_expenses)
        expense_count = len(all_expenses)
        
        # Get sync status
        sync_status = db.get_sync_status()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'total_expenses': total_expenses,
                'expense_count': expense_count,
                'monthly': monthly,
                'yearly': yearly,
                'categories': categories,
                'recent_expenses': recent,
                'sync_status': sync_status
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/data/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense (soft delete)"""
    try:
        db = get_db_manager()
        success = db.delete_expense(expense_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Expense deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/data/<int:expense_id>/category', methods=['PUT'])
def update_expense_category(expense_id):
    """Update expense category"""
    try:
        data = request.get_json()
        category = data.get('category')
        
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category is required'
            }), 400
            
        db = get_db_manager()
        success = db.update_expense_category(expense_id, category)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Category updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@expenses_bp.route('/test-gemini', methods=['POST'])
def test_gemini_categorization():
    """
    Test Gemini API categorization with sample descriptions.
    Check the server terminal for request/response debug logs.
    """
    try:
        # Sample expense descriptions to test
        sample_descriptions = request.json.get('descriptions') if request.json else None
        
        if not sample_descriptions:
            sample_descriptions = [
                "Swiggy order dinner",
                "Uber ride to office",
                "Netflix subscription",
                "Electricity bill payment",
                "DMart groceries",
                "Ice cream from Amul",
                "Mobile recharge Jio",
                "HP Gas cylinder refill"
            ]
        
        categorizer = get_categorizer()
        
        if not categorizer.is_configured():
            return jsonify({
                'success': False,
                'error': 'Gemini API not configured. Check GEMINI_API_KEY in .env'
            }), 400
        
        # Create mock expenses
        mock_expenses = [
            {'id': i, 'description': desc} 
            for i, desc in enumerate(sample_descriptions)
        ]
        
        # Force API call (skip local fallback)
        results = categorizer._categorize_with_api(mock_expenses)
        
        # Format results
        formatted = []
        for i, desc in enumerate(sample_descriptions):
            result = next((r for r in results if r.get('splitwise_id') == i), None)
            category = result['category'] if result else 'Unknown'
            formatted.append({
                'description': desc,
                'category': category
            })
        
        return jsonify({
            'success': True,
            'message': 'Check server terminal for Gemini request/response logs',
            'results': formatted
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
