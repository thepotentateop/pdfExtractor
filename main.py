# To Be Modified


# import pdfplumber
# import json
# import re
# import logging
# from tempfile import NamedTemporaryFile
#
# logging.basicConfig(level=logging.INFO)
#
#
# class PDFTableExtractor:
#     @staticmethod
#     def extract_tables_from_pdf(pdf_path):
#         tables_data = []
#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page_num, page in enumerate(pdf.pages):
#                     tables = page.extract_tables()
#                     for table in tables:
#                         if table and any(cell is not None for cell in table[0]):
#                             tables_data.append({"page": page_num + 1, "table": table})
#         except Exception as e:
#             logging.error(f"Error extracting tables: {e}")
#         return tables_data
#
#     @staticmethod
#     def save_tables_to_text(tables_data, output_text_path):
#         try:
#             with open(output_text_path, 'w', encoding='UTF-8') as file:
#                 for table_data in tables_data:
#                     table = table_data['table']
#                     headers = table[0]
#                     file.write("\t".join(str(cell) if cell is not None else "" for cell in headers) + "\n")
#                     for row in table[1:]:
#                         file.write("\t".join(str(cell) if cell is not None else "" for cell in row) + "\n")
#                     file.write("\n" + "=" * 40 + "\n\n")
#         except Exception as e:
#             logging.error(f"Error saving tables: {e}")
#
#     @staticmethod
#     def replace_newlines(input_file, output_file):
#         try:
#             with open(input_file, 'r', encoding='UTF-8') as f:
#                 content = f.read()
#
#             modified_content = content.replace('\t', ' ').replace('='*40, ' ')
#             output_json = {"data": modified_content}
#
#             with open(output_file, 'w', encoding='UTF-8') as f:
#                 json.dump(output_json, f, indent=4)
#         except Exception as e:
#             logging.error(f"Error replacing newlines: {e}")
#
#     @staticmethod
#     def process_file(input_file, output_file):
#         keywords = ["Article / item", "Taille / Size", "Qty"]
#         separator = "=" * 40
#         found_sections = []
#         collected_data = ""
#         found_keyword = False
#
#         try:
#             with open(input_file, 'r', encoding='UTF-8') as f:
#                 lines = f.readlines()
#                 for line in lines:
#                     if any(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
#                         found_keyword = True
#                         break
#                     collected_data += line
#
#             if found_keyword:
#                 with open('header_data.txt', 'w', encoding='UTF-8') as f:
#                     f.write(collected_data.strip())
#             else:
#                 logging.info("No keywords found in the file.")
#
#             sections = ''.join(lines).split(separator)
#             for section in sections:
#                 section_text = section.strip()
#                 if any(re.search(keyword, section_text, re.IGNORECASE) for keyword in keywords):
#                     found_sections.append(section_text.strip())
#
#             with open(output_file, 'w', encoding='UTF-8') as f_out:
#                 for section in found_sections:
#                     f_out.write(section + "\n" + separator + "\n")
#         except Exception as e:
#             logging.error(f"Error processing file: {e}")
#
#     @staticmethod
#     def convert_pdf_to_text(pdf_path, output_text_path):
#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 with open(output_text_path, 'w', encoding='UTF-8') as file:
#                     for page in pdf.pages:
#                         file.write(page.extract_text() + "\n")
#         except Exception as e:
#             logging.error(f"Error converting PDF to text: {e}")
#
#     @classmethod
#     def execute(cls, pdf_file_path, usr_prompt="Hello GPT..."):
#         with NamedTemporaryFile(delete=False, mode='w', encoding='UTF-8') as temp_file:
#             temp_output = temp_file.name
#
#         output_text_path = 'pdf_to_text.txt'
#         final_output = 'output.txt'
#
#         tables_data = cls.extract_tables_from_pdf(pdf_file_path)
#         cls.save_tables_to_text(tables_data, output_text_path)
#         cls.process_file(output_text_path, temp_output)
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
#
# if __name__ == "__main__":
#     pdf_file_path = "hello-test.pdf"
#     result = PDFTableExtractor.execute(pdf_file_path)
#     logging.info(result)
