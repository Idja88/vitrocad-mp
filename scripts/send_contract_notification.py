from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from api.vitro_cad_api import VitroCADAPIClient

load_dotenv()

def send_contract_notification():
    """Send notifications for contracts ending within 15 days."""
    
    # Configuration
    contract_list_id = os.getenv('VITRO_CAD_CONTRACT_LIST_ID')
    contract_type_id_list = os.getenv('VITRO_CAD_CONTRACT_TYPE_ID_LIST')
    email_template_id = os.getenv('VITRO_CAD_CONTRACT_EMAIL_TEMPLATE_ID')
    days_until_expiry = int(os.getenv('VITRO_CAD_CONTRACT_DAYS_UNTIL_EXPIRY'))

    if contract_type_id_list:
        contract_type_id_list = [ctid.strip() for ctid in contract_type_id_list.split(',') if ctid.strip()]
    else:
        contract_type_id_list = []
    
    contract_type_id_list_str = ', '.join([f'Guid(\"{id}\")' for id in contract_type_id_list])

    # Initialize client
    client = VitroCADAPIClient()
    
    try:
        # Get today in server timezone (UTC+5)
        local_tz = datetime.now().astimezone().tzinfo
        today_local = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        expiry_date_local = today_local + timedelta(days=days_until_expiry)
        expiry_date_utc = expiry_date_local.astimezone(timezone.utc)
    
        # Build query with UTC dates and DateTimeKind.Utc
        query = f"item => new Guid[] {{ {contract_type_id_list_str} }}.Contains(item.ContentTypeId) &&  \
            item.GetLookupId(\"contract_holder\") != null && \
            item.GetValueAsDateTime(\"vitro_base_contract_finish_date\") == \
            DateTime({expiry_date_utc.year}, {expiry_date_utc.month}, {expiry_date_utc.day}, {expiry_date_utc.hour}, {expiry_date_utc.minute}, {expiry_date_utc.second}, DateTimeKind.Utc)"
        
        # Get filtered contracts from server
        contracts = client.get_recursive_mp_list(contract_list_id, query=query)

        if not contracts:
            print("No contracts found or error retrieving contracts")
            return
        
        for contract in contracts:
            # Get contract details
            contract_id = contract.get('fieldValueMap', {}).get('id')
            contract_holder = client.get_mp_item(contract.get('fieldValueMap', {}).get('contract_holder').get('id'))
            contract_holder_email = contract_holder.get('fieldValueMap', {}).get('email')
            
            if not contract_holder_email:
                print(f"No email found for contract holder of contract {contract_id}")
                continue
            
            # Send email
            result = client.send_email(
                template_id=email_template_id,
                to_email=contract_holder_email,
                item_id=contract_id
            )
            
            if result:
                print(f"Email sent to {contract_holder_email} for contract {contract_id}")
            else:
                print(f"Failed to send email to {contract_holder_email} for contract {contract_id}")
        
    finally:
        client.close()

if __name__ == "__main__":
    send_contract_notification()
