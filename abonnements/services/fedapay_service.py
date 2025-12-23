# abonnements/services/fedapay_service.py
import fedapay
from django.conf import settings
from decimal import Decimal

class FedaPayService:
    """Service pour gérer les paiements via FedaPay"""
    
    def __init__(self):
        fedapay.api_key = settings.FEDAPAY_SECRET_KEY
        fedapay.environment = settings.FEDAPAY_ENVIRONMENT
    
    def creer_transaction(self, montant, description, customer_email, customer_firstname, 
                         customer_lastname, customer_phone, callback_url=None):
        """
        Créer une transaction FedaPay
        
        Args:
            montant: Montant en FCFA (int ou Decimal)
            description: Description de la transaction
            customer_email: Email du client
            customer_firstname: Prénom du client
            customer_lastname: Nom du client
            customer_phone: Téléphone du client
            callback_url: URL de callback (optionnel)
        
        Returns:
            dict: Données de la transaction avec token et URL de paiement
        """
        try:
            # Créer la transaction
            transaction = fedapay.Transaction.create({
                "description": description,
                "amount": int(montant),
                "currency": {
                    "iso": "XOF"  # Franc CFA
                },
                "callback_url": callback_url or settings.FEDAPAY_CALLBACK_URL,
                "customer": {
                    "firstname": customer_firstname,
                    "lastname": customer_lastname,
                    "email": customer_email,
                    "phone_number": {
                        "number": customer_phone,
                        "country": "bj"  # Bénin
                    }
                }
            })
            
            # Générer le token de paiement
            token = transaction.generateToken()
            
            return {
                'success': True,
                'transaction_id': transaction.id,
                'token': token.token,
                'url': token.url,
                'reference': transaction.reference
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verifier_transaction(self, transaction_id):
        """
        Vérifier le statut d'une transaction
        
        Args:
            transaction_id: ID de la transaction FedaPay
        
        Returns:
            dict: Statut de la transaction
        """
        try:
            transaction = fedapay.Transaction.retrieve(transaction_id)
            
            return {
                'success': True,
                'status': transaction.status,  # 'pending', 'approved', 'declined', 'canceled'
                'amount': transaction.amount,
                'reference': transaction.reference,
                'transaction': transaction
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def transaction_reussie(self, transaction_id):
        """Vérifier si une transaction est réussie"""
        result = self.verifier_transaction(transaction_id)
        return result.get('success') and result.get('status') == 'approved'



