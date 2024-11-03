import torch
from transformers import pipeline


def emotion_analyzer(sentences):
    device = 0 if torch.cuda.is_available() else -1

    classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base",
                          return_all_scores=True, device=device)

    output = []
    for text in sentences:
        output.append(classifier(text))

    return output

