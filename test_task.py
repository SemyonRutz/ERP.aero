import pdb
from PyPDF2 import PdfReader 
import pprint
import cv2
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
import os



############################# Extracting strings from pdf #################################


class PDFProcessor:
    def process_pdf(self, pdf_path, poppler_path, saving_folder):

        # Create an instance of the PdfReader class
        pdf = PdfReader(pdf_path)
        lines = []

        # Extract text from each page of the PDF
        for page in pdf.pages:
            text = page.extract_text()
            lines.extend(text.split('\n'))

        description_dict = {}


        # Extracting. Main step
        description_dict['COMPANY'] = lines[0]

        for line in lines:
            # Split the line into parts by ':'
            parts = line.split(':')
            for i in range(len(parts) - 1):
                # Split the current part into words
                words = parts[i].split()
                # If the next part has any words
                if len(parts[i + 1].split()) > 0:
                    # Form the key by joining all words that start with uppercase
                    key = ' '.join([word for word in words if word.isupper()])
                    # Form the value by taking the first word of the next part
                    value = parts[i + 1].split()[0]
                    # Store the key-value pair in the dictionary
                    description_dict[key] = value

        # Remove the keys that have values that are also keys (merged accidentally)
        for key in description_dict:
            if description_dict[key] in description_dict:
                description_dict[key] = None

        # Cleaning up the dictionary
        for line in lines:
            # Split the line into parts by ':'
            parts = line.split(':')
            for i in range(len(parts) - 1):
                # Split the current part into words
                words = parts[i].split()
                # Form the key by joining all words that start with uppercase
                key = ' '.join([word for word in words if word.isupper()])

                # Doublecheck if key is in description_dict
                if key not in description_dict:
                    description_dict[key] = None

                # Remove empty keys
                if key == '':
                    del description_dict[key]

                # Remove incorrect Notes
                if "NOTES" in key:
                    del description_dict[key]

        # Add the Notes        
        notes_flag = False
        notes_value = ""

        for line in lines:
            if "NOTES:" in line:
                notes_flag = True
                # Skip the current line as it's the key
                continue
            if notes_flag:
                # Append the line to the notes value with a space instead of a newline
                notes_value += line.strip() + " "

        # Remove the trailing space from the notes value
        notes_value = notes_value.rstrip()

        # Add the Notes to the dictionary
        description_dict["NOTES"] = notes_value

        # Add the Quantity
        clean_qty = ""
        for line in lines:
            if "Qty" in line:
                clean_qty = ''.join(filter(str.isdigit, line))

        description_dict["Qty"] = clean_qty

############################# extracting barcodes from pdf #################################

        # Extract images from pdf
        pages = convert_from_path(pdf_path=pdf_path, poppler_path=poppler_path)

        c = 0
        for page in pages:
            c += 1
            image_name = f'img-{c}.jpeg'
            page.save(os.path.join(saving_folder, image_name),'JPEG')

        # Extract barcodes from image
        img = cv2.imread(image_name)

        i = 0
        for code in decode(img):
            i += 1
            code_type = (f"barcode {i} type: " + code.type)
            code_data = (f"barcode {i} data: " + code.data.decode('utf-8'))
            description_dict[code_type] = code_data

        return description_dict

