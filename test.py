import pdfplumber
import json
import re
import logging
from tempfile import NamedTemporaryFile

logging.basicConfig(level=logging.INFO)


class PDFTableExtractor:
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        text_data = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_data.append({"page": page_num + 1, "text": text})
        except Exception as e:
            logging.error(f"Error extracting text: {e}")
        return text_data

    @staticmethod
    def save_text_to_file(text_data, output_text_path):
        try:
            with open(output_text_path, 'w', encoding='UTF-8') as file:
                for page_data in text_data:
                    page_text = page_data['text']
                    file.write(page_text + "\n")
        except Exception as e:
            logging.error(f"Error saving text: {e}")

    # @staticmethod
    # def find_first_keyword(text_data, keywords, header_file_path):
    #     try:
    #         found_keyword = False
    #         for page_data in text_data:
    #             page_text = page_data['text']
    #             if any(re.search(keyword, page_text, re.IGNORECASE) for keyword in keywords):
    #                 with open(header_file_path, 'w', encoding='UTF-8') as f:
    #                     f.write(page_text.strip())
    #                 found_keyword = True
    #                 break
    #         if not found_keyword:
    #             logging.info("No keywords found in the text.")
    #     except Exception as e:
    #         logging.error(f"Error finding first keyword: {e}")

    @staticmethod
    def process_file(input_file, output_file):
        keywords = ["Article / item", "Taille / Size", "Qty"]
        separator = "=" * 40
        found_sections = []
        collected_data = ""
        found_keyword = False

        try:
            with open(input_file, 'r', encoding='UTF-8') as f:
                lines = f.readlines()
                for line in lines:
                    if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
                        found_keyword = True
                        break
                    collected_data += line

            if found_keyword:
                with open('header_data.txt', 'w', encoding='UTF-8') as f:
                    f.write(collected_data.strip())
            else:
                logging.info("No keywords found in the file.")

            sections = ''.join(lines).split(separator)
            for section in sections:
                section_text = section.strip()
                if any(re.search(keyword, section_text, re.IGNORECASE) for keyword in keywords):
                    found_sections.append(section_text.strip())

            with open(output_file, 'w', encoding='UTF-8') as f_out:
                for section in found_sections:
                    f_out.write(section + "\n" + separator + "\n")
        except Exception as e:
            logging.error(f"Error processing file: {e}")

    @staticmethod
    def replace_newlines(input_file, output_file):
        try:
            with open(input_file, 'r', encoding='UTF-8') as f:
                content = f.read()

            modified_content = content.replace('\t', ' ').replace('='*40, ' ')
            output_json = {"data": modified_content}

            with open(output_file, 'w', encoding='UTF-8') as f:
                json.dump(output_json["data"], f, indent=4)
        except Exception as e:
            logging.error(f"Error replacing newlines: {e}")

    @classmethod
    def execute(cls, pdf_file_path):
        output_text_path = 'pdf_to_text.txt'
        temp_output = NamedTemporaryFile(delete=False, mode='w', encoding='UTF-8').name
        final_output = 'output.txt'
        header_file_path = 'header_data.txt'

        text_data = cls.extract_text_from_pdf(pdf_file_path)
        cls.save_text_to_file(text_data, output_text_path)
        # cls.find_first_keyword(text_data, ["Article / item", "Taille / Size", "Qty"], header_file_path)
        cls.process_file(output_text_path, temp_output)
        cls.replace_newlines(temp_output, final_output)

        # Read the final output and return it
        try:
            with open(final_output, 'r', encoding='UTF-8') as f:
                output_data = f.read()
        except Exception as e:
            logging.error(f"Error reading final output: {e}")
            output_data = "Error reading output."

        return output_data


if __name__ == "__main__":
    pdf_file_path = "hello-test.pdf"
    result = PDFTableExtractor.execute(pdf_file_path)
    logging.info(result)
