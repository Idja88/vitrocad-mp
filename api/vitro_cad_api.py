import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

class VitroCADAPIClient:
    """Optimized client for Vitro-CAD API with session management."""
    
    def __init__(self):
        self.session = requests.Session()
        self.mp_url = os.getenv('VITRO_CAD_API_BASE_URL')
        self.token = None
    
    def get_token(self):
        """Authenticate and get API token."""
        mp_login = {
            "login": os.getenv('VITRO_CAD_ADMIN_USERNAME'),
            "password": os.getenv('VITRO_CAD_ADMIN_PASSWORD')
        }
        url_string = f"{self.mp_url}/api/security/login"
        try:
            response = self.session.post(url=url_string, json=mp_login)
            response.raise_for_status()
            response_json = response.json()
            self.token = response_json.get('token')
            return self.token
        except requests.exceptions.RequestException as e:
            print(f"Error getting MP token: {e}")
            return None
    
    def update_mp_list(self, data):
        """Update MP list with optimized session.
        
        Data should be a single item dict. It will be wrapped in an array
        for the API call as per Vitro-CAD API specification.
        
        Args:
            data: Dict containing item data (list_id, content_type_id, etc.)
        
        Returns:
            Response dict (first element from response array) or None if error
        """
        if not self.token:
            self.get_token()
        
        url_string = f"{self.mp_url}/api/item/update"
        
        # Wrap data in array as per API documentation
        item_array = [data]
        item_list_json = json.dumps(item_array, ensure_ascii=False)
        
        # Prepare multipart/form-data payload
        files = {
            'itemListJson': (None, item_list_json)
        }
        
        headers = {
            'Authorization': self.token
        }
        
        try:
            response = self.session.post(
                url=url_string,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            response_json = response.json()
            
            # API returns array - extract first element if it's a list
            if isinstance(response_json, list) and len(response_json) > 0:
                return response_json[0]
            elif isinstance(response_json, dict):
                return response_json
            else:
                return response_json
                
        except requests.exceptions.RequestException as e:
            print(f"Error updating MP list: {e}")
            return None
    
    def get_recursive_mp_list(self, parent_id, query=None):
        """Get recursive items  from a list.
        
        Args:
            parent_id: The ID of the list
            query: Optional query parameters
        
        Returns:
            List of contract items or None if error
        """
        if not self.token:
            self.get_token()
        
        url_string = f"{self.mp_url}/api/item/getRecursive/{parent_id}"
        
        headers = {
            'Authorization': self.token
        }

        payload = {}
        if query:
            payload["query"] = query
        
        try:
            response = self.session.post(url=url_string, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting items: {e}")
            return None
    
    def get_mp_item(self, item_id, query=None):
        """Get a specific item by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            query: Optional query parameters
        
        Returns:
            List of contract items or None if error
        """
        if not self.token:
            self.get_token()
        
        url_string = f"{self.mp_url}/api/item/get/{item_id}"
        
        headers = {
            'Authorization': self.token
        }

        payload = {}
        if query:
            payload['query'] = query
        
        try:
            response = self.session.post(url=url_string, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting items: {e}")
            return None

    def send_email(self, template_id, to_email, item_id):
        """Send email notification via Vitro-CAD API.
        
        Args:
            template_id: Email template ID
            to_email: Recipient email
            item_id: ID of the item for context
        
        Returns:
            Response dict or None if error
        """
        if not self.token:
            self.get_token()
        
        url_string = f"{self.mp_url}/mail/api/mail/send/{template_id}"
        
        headers = {
            'Authorization': self.token
        }
        
        payload = {
            "toEmailList": [
                to_email
            ],
            "id": item_id,
            "hostUrl": self.mp_url
        }
        
        try:
            response = self.session.post(
                url=url_string,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            if response.content:
                return response.json()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending email: {e}")
            return None
    
    def close(self):
        """Close the session."""
        self.session.close()
