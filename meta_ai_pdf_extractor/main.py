import pdfplumber
import json
import re
import logging
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

class PDFExtractor:

    @staticmethod
    def extract_header_from_pdf(keywords, concatenated_text, pdf_file):
        header_data = {}

        # Compile a regular expression pattern with the keywords
        pattern = re.compile(r'\b(' + '|'.join(keywords) + r')\b', re.IGNORECASE)
        try:
            with pdfplumber.open(pdf_file) as pdf:
                # Read the first page
                page1 = pdf.pages[0]
                text = page1.extract_text()

                # Split the text into lines
                lines = text.splitlines()

                # Initialize an empty string to store the concatenated text
                # concatenated_text = '"Please provide Invoice, Purchase Order, Bill to, Sales Order, Incoterm, Consignee from the following inventory data in json format\n\n'

                # Iterate over each line
                for line in lines:
                    # Check if any of the keywords are found in the line
                    if pattern.search(line):
                        break

                    # If no keywords are found, concatenate the line with a newline character
                    concatenated_text += line + "\n"
                logging.info("No keywords found in the first page.")

            # Print the concatenated text
            json_object = {
                "model": "meta--llama3-70b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": concatenated_text
                    }
                ],
                "max_tokens": 4096
            }
            # # get token
            client_id = "sb-7f14b322-7d28-4b46-93d0-e0d96bc04a40!b142513|aicore!b540"
            client_secret = "ad8a5f75-6d6d-4764-aa28-ae3a6b0f02a6$iY6bAK2tuSLQOltxgZayBIWk8h1nLxPL53QLKTgQFcM="
            url_auth = "https://dqm-wmhsrh96.authentication.eu10.hana.ondemand.com/oauth/token"

            token = requests.post(url_auth, data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            })
            final_token = token.json()["access_token"]
            # call open ai api
            url = "https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dc2e657c28c8f7f5/chat/completions"
            # #
            headers = {
                "Authorization": f"Bearer {final_token}",
                "AI-Resource-Group": "default"
            }

            print(concatenated_text)
            response = requests.post(url, json=json_object, headers=headers)
            data = response.json()
            # print(data)

            print(data['choices'][0]['message']['content'])
            content = data['choices'][0]['message']['content']

            # Write the JSON object to a file
            with open('output_file.json', 'w', encoding='UTF-8') as f_out:
                 json.dump(data['choices'][0]['message']['content'], indent=4)

        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")

    @staticmethod
    def extract_item_from_pdf(keywords, concatenated_item_text, pdf_file):

        try:
            # Open the PDF file
            with pdfplumber.open(pdf_file) as pdf:
                # Iterate over each page
                for page in pdf.pages:
                    # Check if any of the keywords are found on the page (case-insensitive)
                    if any(keyword.casefold() in page.extract_text().casefold() for keyword in keywords):
                        # If keywords are found, convert the page to text
                        page_text = page.extract_text()
                        # Add \n at every new line
                        page_text = page_text.replace('\n', '\n\n')
                        # Concatenate the page text to the variable
                        concatenated_item_text += page_text
            # Print the concatenated text
            json_object = {
                "model": "meta--llama3-70b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": concatenated_item_text
                    }
                ],
                "max_tokens": 4096
            }
            # # get token
            client_id = "sb-7f14b322-7d28-4b46-93d0-e0d96bc04a40!b142513|aicore!b540"
            client_secret = "ad8a5f75-6d6d-4764-aa28-ae3a6b0f02a6$iY6bAK2tuSLQOltxgZayBIWk8h1nLxPL53QLKTgQFcM="
            url_auth = "https://dqm-wmhsrh96.authentication.eu10.hana.ondemand.com/oauth/token"

            token = requests.post(url_auth, data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            })
            final_token = token.json()["access_token"]
            # call open ai api
            url = "https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dc2e657c28c8f7f5/chat/completions"
            # #
            headers = {
                "Authorization": f"Bearer {final_token}",
                "AI-Resource-Group": "default"
            }

            print(concatenated_item_text)
            response = requests.post(url, json=json_object, headers=headers)
            data = response.json()
            print(response)
            content = data['choices'][0]['message']['content']
            print(content)

        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
        # print(header_data)
        with open('output.txt', 'w') as txtfile:
            json.dump(content, indent=4)


if __name__ == "__main__":
    main_pdf_path = "SSENSE. PO 956321. PT 102674065. 3 CTNS. 1.pdf"
    # Define the keywords (can be multiple)
    # keywords = ['invoice', 'style', 'color', 'quantity'] #mugler
    # keywords = ["Item", "Size", "Quantity", "Color"] #ssense
    # keywords = ["PACKAGE", "DIMENSION", "Net WEIGHT"]
    # keywords = ["ARTICLE", "ITEM", "QUANTITY", "SIZES"]  #delivery-note #stella
    keywords = ["Style Id", "Color", "QUANTITY", "SIZES"]# ssense po

    #prompt for header text
    #Mugler
    # concatenated_text = "Please provide Invoice, Purchase Order, Bill to, Sales Order, Incoterm, Consignee from the following inventory data in json format\n\n"
    #delivery-note #stella
    # concatenated_text = "Please provide Customer, PO,Carrier, Incoterm from the following inventory data in json format\n\n"
    #Ssense PO
    concatenated_text = "Please provide Customer PO, Cutomer ID, Bill to, Sales Order, Ship to, Consignee from the following inventory data in json format\n\n"

    #prompt for item text
    #mugler
    # concatenated_item_text = "Please provide Invoice,color,style,quantity and sizes from the following inventory data in json format(example from the invantory data is Invoice:56105490 Style:24P5BW0045878 Color:B1919 BLACK/BLACK Size:38 Quantity:1 Size:40 Quantity:2 and so on\n\n"
    #delivery-note
    # concatenated_item_text = "Please provide Item,color,quantity and size from the following inventory data in json format\n\n"
    #stella
    # concatenated_item_text = "Please provide Item,color,quantity and size from the following inventory data in json format(example Item:680050SPB05 Color:2742 (Size:M Quantity:1, Size:L Quantity:1 and so on))\n\n"
    #ssense PO
    concatenated_item_text = "Please provide Style ID,color,quantity and size from the following inventory data in json format\n\n"

    result = PDFExtractor.extract_header_from_pdf(keywords, concatenated_text, main_pdf_path)
    result_item = PDFExtractor.extract_item_from_pdf(keywords, concatenated_item_text, main_pdf_path)
    logging.info("Done!!")