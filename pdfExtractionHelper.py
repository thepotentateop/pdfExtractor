import json
import re
import logging
import requests
import pdfplumber
from typing import List
from datetime import timedelta, datetime, timezone

logging.basicConfig(level=logging.INFO)


def load_config(config_file: str) -> dict:
    """Load configuration from a JSON file."""
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
            logging.info("Configuration loaded successfully.")
            return config
    except FileNotFoundError:
        logging.error(f"Configuration file '{config_file}' not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from the configuration file: {e}")
        raise


def save_config(config: dict, config_file: str) -> None:
    """Save configuration to a JSON file."""
    try:
        with open(config_file, 'w') as file:
            json.dump(config, file, indent=4)
            logging.info("Configuration saved successfully.")
    except IOError as e:
        logging.error(f"Error saving configuration file: {e}")
        raise


class PDFExtractor:
    def __init__(self, config_file: str = 'config.json'):
        """Initialize PDFExtractor with API configuration from a JSON file."""
        self.config_file = config_file
        self.config = load_config(config_file)
        self.client_id = self.config['client_id']
        self.client_secret = self.config['client_secret']
        self.url_auth = self.config['url_auth']
        self.api_url = self.config['api_url']

    def get_access_token(self) -> str:
        """Obtain access token for API requests, use cached token if valid."""
        current_time = datetime.now(timezone.utc)

        # Check if token is cached and valid
        if 'access_token' in self.config and 'expires_at' in self.config:
            try:
                expires_at = datetime.fromisoformat(self.config['expires_at'])
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError) as e:
                logging.error(f"Error parsing 'expires_at' from configuration: {e}")
                expires_at = datetime.min.replace(tzinfo=timezone.utc)  # Force token refresh

            if current_time < expires_at:
                logging.info("Using cached access token.")
                return self.config['access_token']

        # Token is either not present or expired, request a new one
        try:
            response = requests.post(self.url_auth, data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            })
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)  # Default to 3600 seconds if not provided
            expires_at = current_time + timedelta(seconds=expires_in)

            # Update config with new token and expiration
            self.config['access_token'] = access_token
            self.config['expires_at'] = expires_at.isoformat()
            save_config(self.config, self.config_file)

            return access_token
        except requests.RequestException as e:
            logging.error(f"Error obtaining access token: {e}")
            raise

    def call_api(self, json_object: dict) -> dict:
        """Call API with the given JSON payload."""
        try:
            headers = {
                "Authorization": f"Bearer {self.get_access_token()}",
                "AI-Resource-Group": "default"
            }
            response = requests.post(self.api_url, json=json_object, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error calling API: {e}")
            raise

    def extract_text_from_first_page(self, pdf_file: str, keywords: List[str]) -> str:
        """Extract text from the first page of the PDF until a keyword is found."""
        pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\b', re.IGNORECASE)
        try:
            with pdfplumber.open(pdf_file) as pdf:
                page1 = pdf.pages[0]
                text = page1.extract_text()
                lines = text.splitlines()
                concatenated_text = ""

                for line in lines:
                    if pattern.search(line):
                        break
                    concatenated_text += line + "\n"

            return concatenated_text
        except Exception as e:
            logging.error(f"Error extracting text from the first page: {e}")
            raise

    def extract_header_from_pdf(self, keywords: List[str], prompt: str, pdf_file: str) -> str:
        """Extract header information from the PDF, format the result, and save it in a well-formatted text file."""
        try:
            # Extract text from the first page of the PDF based on keywords
            concatenated_text = self.extract_text_from_first_page(pdf_file, keywords)

            # Prepare JSON object for the API request
            json_object = {
                "model": "meta--llama3-70b-instruct",
                "messages": [{"role": "user", "content": prompt + concatenated_text}],
                "max_tokens": 4096
            }

            # Call API to process the extracted text
            data = self.call_api(json_object)
            content = data['choices'][0]['message']['content']

            # Format the content to make it user-friendly
            try:
                # Assuming the content is JSON, format it nicely
                formatted_data = json.dumps(json.loads(content), indent=4)
                formatted_content = f"Extracted Header Information:\n\n{formatted_data}"
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON content: {e}")
                formatted_content = f"Error: Unable to format content due to JSON decoding error.\nOriginal Content:\n{content}"

            return formatted_content

        except Exception as e:
            logging.error(f"Error extracting header from PDF: {e}")



    def extract_item_from_pdf(self, keywords: List[str], prompt: str, pdf_file: str) -> str:
        """Extract item information from the PDF."""
        try:
            response_item_text = ""
            with pdfplumber.open(pdf_file) as pdf:
                num_chunks = -(-len(pdf.pages) // 3)

                for i in range(num_chunks):
                    chunks_pages = pdf.pages[i*3:(i+1)*3]
                    concatenated_item_text = ""

                    for page in chunks_pages:
                        concatenated_item_text += page.extract_text()

                    json_object = {
                        "model": "meta--llama3-70b-instruct",
                        "messages": [{"role": "user", "content": prompt + concatenated_item_text}],
                        "max_tokens": 4096
                    }
                    data = self.call_api(json_object)
                    response_item_text += data['choices'][0]['message']['content']

            return response_item_text

        except Exception as e:
            logging.error(f"Error extracting item from PDF: {e}")
