import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained('textdetox/xlmr-large-toxicity-classifier-v2')
model = AutoModelForSequenceClassification.from_pretrained('textdetox/xlmr-large-toxicity-classifier-v2')

batch = tokenizer.encode("You are amazing!", return_tensors="pt")

output = model(batch)
# idx 0 for neutral, idx 1 for toxic
logits = output.logits
prediction = torch.argmax(logits, dim=1).item()
print(prediction)