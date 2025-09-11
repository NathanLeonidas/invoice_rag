import torch
from transformers import pipeline

pipeline = pipeline(
    task="text2text-generation",
    model="google-t5/t5-base",
    dtype=torch.float16,
    device=0
)
print(pipeline("translate English to French: The weather is nice today."))