# import pdfplumber
# import json
# import re
# import logging
# from tempfile import NamedTemporaryFile
#
# logging.basicConfig(level=logging.INFO)
#
# class PDFTableExtractor:
#     @staticmethod
#     def extract_text_from_pdf(pdf_path):
#         """Extract all text from the PDF and return as a list of page texts."""
#         text_data = []
#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page in pdf.pages:
#                     text = page.extract_text()
#                     if text:
#                         text_data.append(text)
#         except Exception as e:
#             logging.error(f"Error extracting text: {e}")
#         return text_data
#
#     @staticmethod
#     def save_text_to_file(text_data, output_text_path):
#         """Save the extracted text to a file."""
#         try:
#             with open(output_text_path, 'w', encoding='UTF-8') as file:
#                 for page_text in text_data:
#                     file.write(page_text + "\n")
#         except Exception as e:
#             logging.error(f"Error saving text: {e}")
#
#     @staticmethod
#     def process_header(text_data, keywords, header_file_path):
#         """Process text to find and save header information."""
#         try:
#             full_text = "\n".join(text_data)
#             pages = full_text.split('\n\n')  # Assuming double newlines separate pages
#             temp = ""
#             for page_num, page_text in enumerate(pages):
#                 if page_num == 0:  # Process only the first page
#                     lines = page_text.splitlines()
#                     for line in lines:
#                         temp += line + "\n"
#                         if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
#                             with open(header_file_path, 'w', encoding='UTF-8') as f:
#                                 f.write(temp.strip())
#                             return  # Exit after finding keywords in the first page
#             logging.info("No keywords found in the first page.")
#         except Exception as e:
#             logging.error(f"Error processing header: {e}")
#
#     @staticmethod
#     def process_items(input_file, keywords, output_file):
#         """Process file to find and save pages containing keywords."""
#         separator = "=" * 40
#         found_sections = []
#         temp = ""
#         flag = False
#
#         try:
#             with open(input_file, 'r', encoding='UTF-8') as f:
#                 content = f.read()
#                 pages = content.split(separator)  # Split content based on separator
#                 for page in pages:
#                     lines = page.strip().splitlines()
#                     for line in lines:
#                         temp += line + "\n"
#                         if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
#                             flag = True
#                     if flag:  # If keyword found on the page
#                         found_sections.append(temp.strip())
#                     temp = ""
#                     flag = False  # Reset flag
#             with open(output_file, 'w', encoding='UTF-8') as f_out:
#                 for section in found_sections:
#                     f_out.write(section + "\n" + separator + "\n")
#         except Exception as e:
#             logging.error(f"Error processing items: {e}")
#
#     @staticmethod
#     def replace_newlines(input_file, output_file):
#         """Replace newlines and tabs with spaces and save as JSON."""
#         try:
#             with open(input_file, 'r', encoding='UTF-8') as f:
#                 content = f.read()
#
#             modified_content = content.replace('\t', ' ').replace('=' * 40, ' ')
#             output_json = {"data": modified_content}
#
#             with open(output_file, 'w', encoding='UTF-8') as f:
#                 json.dump(output_json, f, indent=4)
#         except Exception as e:
#             logging.error(f"Error replacing newlines: {e}")
#
#     @classmethod
#     def execute(cls, pdf_file_path, usr_prompt="Hello GPT..."):
#         output_text_path = 'pdf_to_text.txt'
#         temp_output = NamedTemporaryFile(delete=False, mode='w', encoding='UTF-8').name
#         final_output = 'output.txt'
#         header_file_path = 'header_data.txt'
#
#         keywords = ["Article / item", "Taille / Size", "Qty"]
#
#         # Extract text and save to file
#         text_data = cls.extract_text_from_pdf(pdf_file_path)
#         cls.save_text_to_file(text_data, output_text_path)
#
#         # Process header and save if keywords are found
#         cls.process_header(text_data, keywords, header_file_path)
#
#         # Process items and save
#         cls.process_items(output_text_path, keywords, temp_output)
#
#         # Replace newlines and save final output
#         cls.replace_newlines(temp_output, final_output)
#
#         # Read the final output and return it
#         try:
#             with open(final_output, 'r', encoding='UTF-8') as f:
#                 output_data = f.read()
#         except Exception as e:
#             logging.error(f"Error reading final output: {e}")
#             output_data = "Error reading output."
#
#         return output_data
#
# if __name__ == "__main__":
#     pdf_file_path = "hello-test.pdf"
#     result = PDFTableExtractor.execute(pdf_file_path)
#     logging.info(result)


import pdfplumber
import json
import re
import logging

logging.basicConfig(level=logging.INFO)


class PDFTableExtractor:
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """
        Extract all text from the PDF and return as a list of page texts.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            list: List of strings where each string represents the text of a page.
        """
        text_data = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_data.append(text)
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
        return text_data

    @staticmethod
    def save_text_to_file(text_data, output_text_path):
        """
        Save the extracted text data to a file.

        Args:
            text_data (list): List of strings containing the text data to save.
            output_text_path (str): Path to the output text file.
        """
        try:
            with open(output_text_path, 'w', encoding='UTF-8') as file:
                for page_text in text_data:
                    file.write(page_text + "\n\n")  # Use double newlines to separate pages
        except Exception as e:
            logging.error(f"Error saving text to file: {e}")

    # @staticmethod
    # def process_header(text_data, keywords, header_file_path):
    #     """
    #     Process text data to find and save header information containing specified keywords.
    #
    #     Args:
    #         text_data (list): List of strings containing the extracted text data.
    #         keywords (list): List of keywords to search for in the text.
    #         header_file_path (str): Path to the file where header information will be saved.
    #     """
    #     try:
    #         full_text = "\n".join(text_data)
    #         pages = full_text.split('\n\n')
    #
    #         # Check only the first page for headers
    #         if pages:
    #             first_page_text = pages[0]
    #             temp = ""
    #             for line in first_page_text.splitlines():
    #                 temp += line + "\n"
    #                 if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
    #                     with open(header_file_path, 'w', encoding='UTF-8') as f:
    #                         f.write(temp.strip())
    #                     return
    #         logging.info("No keywords found in the first page.")
    #     except Exception as e:
    #         logging.error(f"Error processing header: {e}")

    @staticmethod
    def process_header(text_data, keywords, header_file_path):
        """
        Process text data to find header information containing specified keywords
        and save it in a JSON format.

        Args:
            text_data (list): List of strings containing the extracted text data.
            keywords (list): List of keywords to search for in the text.
            header_file_path (str): Path to the file where header information in JSON format will be saved.
        """
        try:
            full_text = "\n".join(text_data)
            pages = full_text.split('\n\n')

            if pages:
                first_page_text = pages[0]
                temp = ""
                for line in first_page_text.splitlines():
                    temp += line + "\n"
                    if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
                        # Create the JSON object for the header data
                        json_object = {
                            "custom_id": "header-001",
                            "method": "POST",
                            "url": "/v1/chat/completions",
                            "body": {
                                "model": "gpt-3.5-turbo-0125",
                                "messages": [
                                    {"role": "system", "content": "You are a helpful assistant."},
                                    {"role": "user", "content": temp.strip()}
                                ],
                                "max_tokens": 4096
                            }
                        }
                        # Write the JSON object to a file
                        with open(header_file_path, 'w', encoding='UTF-8') as f:
                            json.dump(json_object, f, indent=4)
                        return
            logging.info("No keywords found in the first page.")
        except Exception as e:
            logging.error(f"Error processing header: {e}")

    # @staticmethod
    # def process_items(input_file, keywords, output_file):
    #     """
    #     Process the input file to find pages containing keywords and save them in a JSON format.
    #
    #     Args:
    #         input_file (str): Path to the input text file.
    #         keywords (list): List of keywords to search for in the text.
    #         output_file (str): Path to the output JSON file.
    #     """
    #     custom_id_counter = 1
    #     json_data = []
    #
    #     try:
    #         with open(input_file, 'r', encoding='UTF-8') as f:
    #             content = f.read()
    #             pages = content.split('\n\n')
    #             for page in pages:
    #                 temp = ""
    #                 flag = False
    #                 lines = page.strip().splitlines()
    #                 for line in lines:
    #                     temp += line + "\n"
    #                     if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
    #                         flag = True
    #                 if flag:
    #                     json_object = {
    #                         "custom_id": f"request-{custom_id_counter}",
    #                         "method": "POST",
    #                         "url": "/v1/chat/completions",
    #                         "body": {
    #                             "model": "gpt-3.5-turbo-0125",
    #                             "messages": [
    #                                 {"role": "system", "content": "You are a helpful assistant."},
    #                                 {"role": "user", "content": temp.strip()}
    #                             ],
    #                             "max_tokens": 4096
    #                         }
    #                     }
    #                     json_data.append(json_object)
    #                     custom_id_counter += 1
    #
    #         with open(output_file, 'w', encoding='UTF-8') as f_out:
    #             json.dump(json_data, f_out, indent=4)
    #
    #     except Exception as e:
    #         logging.error(f"Error processing items: {e}")

    @staticmethod
    def process_items(input_file, keywords, output_file):
        """
        Process the input file to find pages containing keywords and save each page's content
        after the first occurrence of a keyword in a JSON format.

        Args:
            input_file (str): Path to the input text file.
            keywords (list): List of keywords to search for in the text.
            output_file (str): Path to the output JSON file.
        """
        json_data = []
        custom_id_counter = 1

        try:
            with open(input_file, 'r', encoding='UTF-8') as f:
                content = f.read()
                pages = content.split('\n\n')

                for page_number, page in enumerate(pages):
                    lines = page.strip().splitlines()

                    temp = ""
                    recording = False
                    keyword_found = False

                    for line in lines:
                        # Check if the line contains any of the keywords
                        if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
                            recording = True
                            keyword_found = True
                            temp += line + "\n"
                        elif recording:
                            temp += line + "\n"

                    # Create a JSON object if a keyword was found and content is available
                    if keyword_found and temp.strip():
                        json_object = {
                            "custom_id": f"request-{custom_id_counter}",
                            "method": "POST",
                            "url": "/v1/chat/completions",
                            "body": {
                                "model": "gpt-3.5-turbo-0125",
                                "messages": [
                                    {"role": "system", "content": "You are a helpful assistant."},
                                    {"role": "user", "content": temp.strip()}
                                ],
                                "max_tokens": 4096
                            }
                        }
                        json_data.append(json_object)
                        custom_id_counter += 1

            # Save the collected JSON data to the output file
            with open(output_file, 'w', encoding='UTF-8') as f_out:
                json.dump(json_data, f_out, indent=4)

        except Exception as e:
            logging.error(f"Error processing items: {e}")

    @classmethod
    def execute(cls, pdf_file_path):
        """
        Main method to execute the PDF extraction and processing pipeline.

        Args:
            pdf_file_path (str): Path to the input PDF file.

        Returns:
            str: Content of the final output file or an error message.
        """
        output_text_path = 'pdf_to_text.txt'
        final_output = 'output.json'
        header_file_path = 'header_data.json'
        keywords = ["Article / item", "Taille / Size", "Qty"]

        # Extract text from the PDF
        text_data = cls.extract_text_from_pdf(pdf_file_path)

        if not text_data:
            logging.error("No text data extracted from the PDF.")
            return "No text data extracted."

        # Save extracted text to a file
        cls.save_text_to_file(text_data, output_text_path)

        # Process header information
        cls.process_header(text_data, keywords, header_file_path)

        # Process items and save to output file
        cls.process_items(output_text_path, keywords, final_output)

        # Read and return the final output
        try:
            with open(final_output, 'r', encoding='UTF-8') as f:
                output_data = f.read()
        except Exception as e:
            logging.error(f"Error reading final output file: {e}")
            output_data = "Error reading output."

        return output_data


if __name__ == "__main__":
    main_pdf_path = "hello-test.pdf"
    result = PDFTableExtractor.execute(main_pdf_path)
    logging.info("Done!!")
