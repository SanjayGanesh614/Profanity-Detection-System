import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class ToxicityClassifier:
    def __init__(self):
        print("Loading Toxicity Classifier Model...")
        model_name = 'textdetox/xlmr-large-toxicity-classifier-v2'
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        print("Model loaded successfully.")

    def analyze(self, text: str) -> int:
        # Returns 0 for neutral, 1 for toxic
        batch = self.tokenizer.encode(text, return_tensors="pt")
        with torch.no_grad():
            output = self.model(batch)
        
        logits = output.logits
        prediction = torch.argmax(logits, dim=1).item()
        return prediction

classifier = ToxicityClassifier()
