from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer

from unsloth import FastLanguageModel


BASE_MODEL = "microsoft/Phi-4-mini-instruct"
MAX_SEQ_LENGTH = 4096
OUTPUT_DIR = "artifacts/lora"
DATA_FILE = "data/daily/latest.jsonl"  # symlink/copy to the newest jsonl


def load_model_and_tokenizer():
    model, tokenizer = FastLanguageModel.from_pretrained(
        BASE_MODEL,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_4bit=True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules="all-linear",
    )
    return model, tokenizer


def main() -> None:
    model, tokenizer = load_model_and_tokenizer()

    ds = load_dataset("json", data_files=DATA_FILE, split="train")

    def format_example(example):
        return {
            "text": tokenizer.apply_chat_template(
                example["messages"], tokenize=False
            )
        }

    ds = ds.map(format_example, remove_columns=ds.column_names)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=ds,
        dataset_text_field="text",
        args=TrainingArguments(
            output_dir=OUTPUT_DIR,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            num_train_epochs=1,
            learning_rate=1e-4,
            logging_steps=10,
            save_strategy="epoch",
            bf16=True,
        ),
        max_seq_length=MAX_SEQ_LENGTH,
    )

    trainer.train()
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)


if __name__ == "__main__":
    main()



