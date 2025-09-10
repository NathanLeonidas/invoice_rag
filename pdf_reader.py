from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

import numpy as np
import os, shutil
import cv2
import pytesseract
from pytesseract import Output

import fitz





class PDF_extractor:
    def __init__(self, 
                 rx=0.45, 
                 ry=0.8,
                 avgsx=120,
                 avgsy=120):
        
        """
        rx, ry : scale of the output
        avgsx, avgsy : strengh of fontsize fix
        """

        self.rx = rx
        self.ry = ry
        self.avgsx = avgsx 
        self.avgsy = avgsy
        self.pages=[]
    

    def write_at_position(self, lines, x, y, txt):
        while len(lines) <= y:
            lines.append('') 

        line = lines[y]

        if len(line) < x:
            line += ' ' * (x - len(line))

        line = line[:x] + txt + line[x + len(txt):]

        lines[y] = line 
        return lines


    def clean_empty_lines(self, lines):
        s=''
        for i in lines:
            if i!='':
                s+=i+'\n'
        return s


    def load_file(self, input_path):
        try:
            ## Check if a textbox exists within the pdf file
            self.check_if_found_txt = True
            self.unprocessed_pages = extract_pages(input_path)
            for i,page_layout in enumerate(extract_pages(input_path)):
                print(i, page_layout)
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        self.check_if_found_txt = False
                        break
                    else:
                        continue
                break


            ## Else we cast onto a png
            if self.check_if_found_txt:
                # We need to change hyperparams cuz the latent space is bigger :pretentious_emoji:
                self.rx = 0.1
                self.ry = 0.01
                self.avgsx = 2000
                self.avgsy = 20000

                pdf_document = fitz.open(input_path)
                self.processed_pages = []


                for page_num in range(pdf_document.page_count):
                    page_boxes=[]
                    png_file_path = f"./page_{page_num}.png"

                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap(dpi=300)
                    pix.save(png_file_path)
                    
                    image = cv2.imread(png_file_path) 
                    ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT)

                    try:
                        if os.path.isfile(png_file_path) or os.path.islink(png_file_path):
                            os.unlink(png_file_path)
                        elif os.path.isdir(png_file_path):
                            shutil.rmtree(png_file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (png_file_path, e))
                    


                    for i in range(len(ocr_data['text'])):
                        text = ocr_data['text'][i]
                        if text.strip(): 
                            x0 = ocr_data['left'][i]
                            y0 = ocr_data['top'][i]
                            x1 = x0 + ocr_data['width'][i]
                            y1 = y0 + ocr_data['height'][i]
                            rect = (x0, y0, x1, y1)
                            page_boxes.append([text, rect])

                    self.processed_pages.append(page_boxes)
            
            ## Case if texboxes were detected
            else:
                self.processed_pages = []
                for i,page_layout in enumerate(self.unprocessed_pages):
                    page_boxes=[]
                    for element in page_layout:
                        if isinstance(element, LTTextContainer):
                            for text_line in element:
                                if isinstance(text_line, LTTextLine):
                                    line_text = text_line.get_text().strip()
                                    page_boxes.append([line_text, text_line.bbox])
                    self.processed_pages.append(page_boxes)


        except Exception as e:
            print(f"An error occured : {e}")
            self.processed_pages = []
                    
        

    def process_file(self):
        self.pages = []
        for i,page_layout in enumerate(self.processed_pages):
            page_text = []
            for textbox in page_layout:
                            line_text = textbox[0]
                            (x0, y0, x1, y1) = textbox[1]


                            y_scale_indicator = np.exp(- (y1 - y0) / self.avgsy)
                            x_scale_indicator = np.exp(- (x1 - x0) / (self.avgsx * len(line_text)))


                            x_repositioned = x0 * x_scale_indicator + (1 - x_scale_indicator) * (x0+x1)/2
                            y_repositioned = y0 * y_scale_indicator + (1 - y_scale_indicator) * (y0+y1)/2
                            x = int(self.rx * x_repositioned)
                            y = int(self.ry * y_repositioned)

                            page_text = self.write_at_position(page_text, x, y, txt=line_text)
            if not(self.check_if_found_txt):
                page_text = page_text[::-1]
            output_text = self.clean_empty_lines(page_text)
            self.pages.append(output_text)



    def write_file(self, output_path):
        for i,page_text in enumerate(self.pages):
            with open(f"{output_path}/output_{i}.txt", "w", encoding="utf-8") as f:
                f.write(page_text)

    def pipeline(self, input_path, output_path):
        self.clean_output_path(output_path)
        self.load_file(input_path)
        self.process_file()
        self.write_file(output_path)
        
    def clean_output_path(self, output_path):
        for filename in os.listdir(output_path):
            file_path = os.path.join(output_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        ## add an empty page for good measure
        with open(f"{output_path}/output_0.txt", "w", encoding="utf-8") as f:
            pass




list_pdf = os.listdir("./data")
pdf_path = "./data/" + list_pdf[0]
output_path = "./outputs"
print(pdf_path)
img_path = "./ocr_data/img_pdf.pdf"

PDF_extractor = PDF_extractor()
PDF_extractor.pipeline(pdf_path, output_path)




