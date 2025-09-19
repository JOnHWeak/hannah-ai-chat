import os
import subprocess
import sys

from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer


LORA_DIR = "artifacts/lora"
HF_MERGED_DIR = "artifacts/hf_merged"
GGUF_DIR = "artifacts/gguf"
LLAMA_CPP_DIR = os.environ.get("LLAMA_CPP_DIR", "C:/tools/llama.cpp")
QUANT = "Q4_K_M"


def merge_lora() -> None:
    os.makedirs(HF_MERGED_DIR, exist_ok=True)
    model = AutoPeftModelForCausalLM.from_pretrained(LORA_DIR, device_map="cpu")
    model = model.merge_and_unload()
    model.save_pretrained(HF_MERGED_DIR, safe_serialization=True)
    AutoTokenizer.from_pretrained(LORA_DIR).save_pretrained(HF_MERGED_DIR)


def convert_to_gguf() -> str:
    os.makedirs(GGUF_DIR, exist_ok=True)
    out_f16 = os.path.join(GGUF_DIR, "model-f16.gguf")
    convert_py = os.path.join(LLAMA_CPP_DIR, "convert_hf_to_gguf.py")
    cmd = [sys.executable, convert_py, "--outfile", out_f16, HF_MERGED_DIR]
    subprocess.check_call(cmd)
    return out_f16


def quantize(infile: str) -> str:
    quant_exe = os.path.join(LLAMA_CPP_DIR, "quantize.exe")
    out_path = os.path.join(GGUF_DIR, f"model.{QUANT}.gguf")
    subprocess.check_call([quant_exe, infile, out_path, QUANT])
    return out_path


def main() -> None:
    merge_lora()
    f16 = convert_to_gguf()
    qpath = quantize(f16)
    print("Quantized GGUF:", qpath)


if __name__ == "__main__":
    main()


