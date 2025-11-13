from flask import Blueprint, request, jsonify
from datetime import datetime
import time
from middleware.auth import auth_required

payment_bp = Blueprint('payment', __name__)

# Mock transaction storage
mock_transactions = {}

@payment_bp.route('/process', methods=['POST'])
@auth_required
def process_payment():
    """Process payment (Mock payment gateway)"""
    try:
        data = request.get_json()

        # Extract payment data
        amount = data.get('amount')
        currency = data.get('currency', 'USD')
        payment_method = data.get('paymentMethod', 'card')
        card_details = data.get('cardDetails', {})

        # Validate input
        if not amount or amount <= 0:
            return jsonify({
                'success': False,
                'error': 'Valid amount is required'
            }), 400

        if payment_method == 'card':
            card_number = card_details.get('number', '')
            if not card_number or len(card_number) < 13:
                return jsonify({
                    'success': False,
                    'error': 'Valid card number is required'
                }), 400

        # Generate transaction ID
        transaction_id = f"TXN{int(time.time() * 1000)}"

        # Mock payment processing (always succeeds)
        transaction = {
            'transactionId': transaction_id,
            'status': 'success',
            'amount': amount,
            'currency': currency,
            'timestamp': datetime.utcnow().isoformat(),
            'paymentMethod': payment_method
        }

        # Store mock transaction
        mock_transactions[transaction_id] = transaction

        return jsonify({
            'success': True,
            'transaction': transaction
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Payment processing failed',
            'message': str(e)
        }), 500

@payment_bp.route('/verify/<transaction_id>', methods=['GET'])
@auth_required
def verify_payment(transaction_id):
    """Verify payment transaction"""
    try:
        # Get transaction from mock storage
        transaction = mock_transactions.get(transaction_id)

        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404

        # Add verified flag
        transaction['verified'] = True

        return jsonify({
            'success': True,
            'transaction': transaction
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Payment verification failed',
            'message': str(e)
        }), 500
