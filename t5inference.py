import torch
from transformers import pipeline
import os
pipeline = pipeline(
    task="text2text-generation",
    model="google-t5/t5-base",
    dtype=torch.float16,
    device=0
)
file =  './outputs/output_0.txt'
with open(file, 'r', encoding='utf-8') as txt:
    prompt = 'Trouve le montant à payer TTC pour le 05/25 dans cette facture : \n DEBUT DU DOCUMENT \n' + txt.read() + '\n FIN DU DOCUMENT \n Le montant à payer TTC pour le 05/25 dans cette facture est donc de :'
    print(pipeline(prompt))