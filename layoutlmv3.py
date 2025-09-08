import os
from transformers import AutoModel

list_files = os.listdir('./data/')
file_path = './data/' +  list_files[0]


model = AutoModel.from_pretrained("microsoft/layoutlmv3-base", torch_dtype="auto")





'''
import pymupdf4llm

print(file_path)
md_text = pymupdf4llm.to_markdown(file_path)
print(md_text)

'''