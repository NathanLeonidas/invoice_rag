from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
import numpy as np
import os, shutil

class PDF_extractor:
    def __init__(self, 
                 tau=1,
                 rx=0.5, 
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


        # S'assurer qu'il y a assez de lignes
        while len(lines) <= y:
            lines.append('')  # ajouter des lignes vides

        line = lines[y]

        # S'assurer que la ligne est assez longue
        if len(line) < x:
            line += ' ' * (x - len(line))

        # Écrire le texte à la position x
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
        self.unprocessed_pages = extract_pages(input_path)



    def process_file(self):
        self.pages = []
        for i,page_layout in enumerate(self.unprocessed_pages):
            page_text=[]
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if isinstance(text_line, LTTextLine):
                            line_text = text_line.get_text().strip()
                            (x0, y0, x1, y1) = text_line.bbox
                            #print(f"Texte : '{line_text}'")
                            #print(f"BBox : x0={x0:.2f}, y0={y0:.2f}, x1={x1:.2f}, y1={y1:.2f}")


                            y_scale_indicator = np.exp(- (y1 - y0) / self.avgsy)
                            x_scale_indicator = np.exp(- (x1 - x0) / (self.avgsx * len(line_text)))


                            x_repositioned = x0 * x_scale_indicator + (1 - x_scale_indicator) * (x0+x1)/2
                            y_repositioned = y0 * y_scale_indicator + (1 - y_scale_indicator) * (y0+y1)/2
                            x = int(self.rx * x_repositioned)
                            y = int(self.ry * y_repositioned)

                            page_text = self.write_at_position(page_text, x, y, txt=line_text)
            page_text = page_text[::-1]
            output_text = self.clean_empty_lines(page_text)
            self.pages.append(output_text)



    def write_file(self, output):
        for i,page_text in enumerate(self.pages):
            with open(f"{output}/output_{i}.txt", "w", encoding="utf-8") as f:
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


PDF_extractor = PDF_extractor()

list_pdf = os.listdir("./data")
pdf_path = "./data/" + list_pdf[1]
output_path = "./outputs"
print(pdf_path)
PDF_extractor.pipeline(pdf_path, output_path)







