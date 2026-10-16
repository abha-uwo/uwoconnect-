import os
import sys
import django

sys.path.append('/Users/gurumukhpahuja/Desktop/uwoconnect_app/UWO-CONNECT_B')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from api.models import Client, Contact, Template, Automation, Product, Order, SalesDocument, Task

User = get_user_model()

def run_all_generation_tests():
    print("=== STARTING COMPREHENSIVE GENERATION / CREATION ENDPOINT TESTS ===")
    user = User.objects.first()
    if not user:
        print("ERROR: No user found.")
        return
    
    client_org = getattr(user, 'client', None)
    if not client_org:
        client_org = Client.objects.first()
        if client_org:
            user.client = client_org
            user.save()
            
    api = APIClient()
    api.force_authenticate(user=user)

    results = []

    # 1. Test PROPOSAL generation
    proposal_res = api.post('/api/sales-documents/', {
        'customer_name': 'Test Client Corp',
        'document_type': 'PROPOSAL',
        'items': [
            {'name': 'Enterprise CRM Setup', 'unit_price': '25000', 'quantity': 1, 'tax_rate': 18}
        ],
        'customer_notes': 'Valid for 30 days.'
    }, format='json')
    results.append(('PROPOSAL Generation', proposal_res.status_code, proposal_res.data if proposal_res.status_code != 201 else f"ID: {proposal_res.data.get('id')} - {proposal_res.data.get('document_number')}"))

    doc_id = proposal_res.data.get('id') if proposal_res.status_code == 201 else None

    # 2. Test QUOTATION generation
    quote_res = api.post('/api/sales-documents/', {
        'customer_name': 'Acme Industries',
        'document_type': 'QUOTATION',
        'items': [
            {'name': 'WhatsApp Marketing Package', 'unit_price': '10000', 'quantity': 2, 'tax_rate': 18}
        ]
    }, format='json')
    results.append(('QUOTATION Generation', quote_res.status_code, quote_res.data if quote_res.status_code != 201 else f"ID: {quote_res.data.get('id')} - {quote_res.data.get('document_number')}"))

    # 3. Test INVOICE generation
    inv_res = api.post('/api/sales-documents/', {
        'customer_name': 'Global Tech Solutions',
        'document_type': 'INVOICE',
        'items': [
            {'name': 'Dedicated Server Hosting', 'unit_price': '5000', 'quantity': 1, 'tax_rate': 18}
        ]
    }, format='json')
    results.append(('INVOICE Generation', inv_res.status_code, inv_res.data if inv_res.status_code != 201 else f"ID: {inv_res.data.get('id')} - {inv_res.data.get('document_number')}"))

    # 4. Test PDF generation for document
    if doc_id:
        pdf_res = api.get(f'/api/sales-documents/{doc_id}/pdf/')
        results.append(('PDF Document Generation', pdf_res.status_code, f"PDF bytes: {len(pdf_res.content)}" if pdf_res.status_code == 200 else pdf_res.data))

        # 5. Test Send Document action
        send_res = api.post(f'/api/sales-documents/{doc_id}/send/', {'channel': 'EMAIL', 'recipient': 'client@example.com'}, format='json')
        results.append(('Send Document Action', send_res.status_code, send_res.data))

    # 6. Test CRM Contact creation
    contact_res = api.post('/api/contacts/', {
        'name': 'Rahul Sharma',
        'phone': '+919876543210',
        'email': 'rahul@example.com',
        'company': 'Sharma Enterprises'
    }, format='json')
    results.append(('CRM Contact Creation', contact_res.status_code, contact_res.data if contact_res.status_code != 201 else f"ID: {contact_res.data.get('id')}"))

    # 7. Test Product creation
    product_res = api.post('/api/products/', {
        'name': 'Cloud Automation Suite v2',
        'description': 'End-to-end automation software',
        'price': '14999.00',
        'stock': 50,
        'currency': 'INR',
        'status': 'ACTIVE'
    }, format='json')
    results.append(('Product Creation', product_res.status_code, product_res.data if product_res.status_code != 201 else f"ID: {product_res.data.get('id')}"))

    # 8. Test Template creation
    template_res = api.post('/api/templates/', {
        'name': f'reminder_temp_{os.urandom(3).hex()}',
        'category': 'UTILITY',
        'language': 'en',
        'content': 'Hello {{1}}, your invoice #{{2}} is due.'
    }, format='json')
    results.append(('Template Creation', template_res.status_code, template_res.data if template_res.status_code != 201 else f"ID: {template_res.data.get('id')}"))

    # 9. Test Automation creation
    auto_res = api.post('/api/automations/', {
        'name': 'Auto Welcome Message',
        'trigger_type': 'NEW_LEAD',
        'action_type': 'SEND_WHATSAPP',
        'is_active': True
    }, format='json')
    results.append(('Automation Creation', auto_res.status_code, auto_res.data if auto_res.status_code != 201 else f"ID: {auto_res.data.get('id')}"))

    # 10. Test Wallet Recharge create
    wallet_res = api.post('/api/wallet/recharge/create/', {
        'amount': 500
    }, format='json')
    results.append(('Wallet Recharge Create', wallet_res.status_code, wallet_res.data if wallet_res.status_code == 200 else wallet_res.data))

    print("\n=== SUMMARY OF ALL GENERATION / CREATION ENDPOINTS ===")
    all_success = True
    for name, status, detail in results:
        status_symbol = "✅ PASSED" if status in (200, 201) else "❌ FAILED"
        if status not in (200, 201):
            all_success = False
        print(f"[{status_symbol}] ({status}) {name}: {detail}")

    if all_success:
        print("\n🎉 ALL GENERATION AND CREATION ENDPOINTS ARE 100% OPERATIONAL WITH 0 ERRORS!")
    else:
        print("\n⚠️ SOME ENDPOINTS REPORTED ISSUES.")

if __name__ == '__main__':
    run_all_generation_tests()
