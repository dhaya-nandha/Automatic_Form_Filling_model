"""
Fine-tuning script for Field-Label Sentence Transformer Matcher.
Demonstrates contrastive learning to align varied form labels with canonical schema keys.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

def train_field_matcher(output_dir: str = "./fine_tuned_matcher"):
    try:
        from sentence_transformers import SentenceTransformer, InputExample, losses
        from torch.utils.data import DataLoader
    except ImportError:
        print("[train_matcher] sentence-transformers / PyTorch is not installed. Install requirements first.")
        return

    print("Loading base model:", config.EMBEDDING_MODEL_NAME)
    model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)

    # Synthetic training pairs mapping messy form labels to canonical schema descriptors
    train_examples = [
        # Positive pairs (label, canonical_description, score 1.0)
        InputExample(texts=['Full Name of Applicant', 'full name'], label=1.0),
        InputExample(texts=['Your Given Name', 'first name'], label=1.0),
        InputExample(texts=['Surname / Family Name', 'last name'], label=1.0),
        InputExample(texts=['Contact Phone No.', 'phone'], label=1.0),
        InputExample(texts=['Email Address for Notifications', 'email'], label=1.0),
        InputExample(texts=['Date of Birth (DD/MM/YYYY)', 'date of birth'], label=1.0),
        InputExample(texts=['Residential Street Address', 'address'], label=1.0),
        InputExample(texts=['Passport / Govt ID Number', 'id number'], label=1.0),
        InputExample(texts=['Years of Relevant Experience', 'total experience years'], label=1.0),
        InputExample(texts=['Highest Qualification Attained', 'education degree'], label=1.0),
        
        # Negative pairs (label, non-matching canonical, score 0.0)
        InputExample(texts=['Contact Phone No.', 'email'], label=0.0),
        InputExample(texts=['Full Name of Applicant', 'address'], label=0.0),
        InputExample(texts=['Date of Birth', 'zip code'], label=0.0),
        InputExample(texts=['Passport / Govt ID Number', 'full name'], label=0.0)
    ]

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=4)
    train_loss = losses.CosineSimilarityLoss(model)

    print("Starting fine-tuning...")
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=3,
        warmup_steps=2,
        output_path=output_dir
    )

    print(f"Fine-tuning complete! Model saved to {output_dir}")

if __name__ == "__main__":
    train_field_matcher()
