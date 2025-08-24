import io
import os
import sys
import struct
import json
import torch
import numpy as np
from pathlib import Path
from safetensors.torch import load_file

# The mapping used to convert parameter names from the Hugging Face format to the ggml format.
conv_map = {
    'self_attn.k_proj'              : 'attn.key',
    'self_attn.q_proj'              : 'attn.query',
    'self_attn.v_proj'              : 'attn.value',
    'self_attn.out_proj'            : 'attn.out',
    'self_attn_layer_norm'          : 'attn_ln',
    'encoder_attn.q_proj'           : 'cross_attn.query',
    'encoder_attn.v_proj'           : 'cross_attn.value',
    'encoder_attn.out_proj'         : 'cross_attn.out',
    'encoder_attn_layer_norm'       : 'cross_attn_ln',
    'fc1'                           : 'mlp.0',
    'fc2'                           : 'mlp.2',
    'final_layer_norm'              : 'mlp_ln',
    'encoder.layer_norm.bias'       : 'encoder.ln_post.bias',
    'encoder.layer_norm.weight'     : 'encoder.ln_post.weight',
    'encoder.embed_positions.weight': 'encoder.positional_embedding',
    'decoder.layer_norm.bias'       : 'decoder.ln.bias',
    'decoder.layer_norm.weight'     : 'decoder.ln.weight',
    'decoder.embed_positions.weight': 'decoder.positional_embedding',
    'decoder.embed_tokens.weight'   : 'decoder.token_embedding.weight',
    'proj_out.weight'               : 'decoder.proj.weight',
}

# Reference: https://github.com/openai/gpt-2/blob/master/src/encoder.py
def bytes_to_unicode():
    """
    Returns dictionary mapping each byte to a unicode string.
    This is used for reversible BPE codes.
    """
    bs = list(range(ord("!"), ord("~") + 1)) + \
         list(range(ord("¡"), ord("¬") + 1)) + \
         list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))

if len(sys.argv) < 4:
    print("Usage: convert-safetensors-to-ggml.py dir_model path-to-whisper-repo dir-output [use-f32]\n")
    sys.exit(1)

# Set up model, whisper repo and output directories.
dir_model   = Path(sys.argv[1])
dir_whisper = Path(sys.argv[2])
dir_out     = Path(sys.argv[3])

# Load tokenizer and model config files.
encoder       = json.load((dir_model / "vocab.json").open("r", encoding="utf8"))
hparams       = json.load((dir_model / "config.json").open("r", encoding="utf8"))

# Some models might be missing the 'max_length' parameter. Fall back to 'max_target_positions'.
if "max_length" not in hparams:
    hparams["max_length"] = hparams.get("max_target_positions", 448)

# Load model weights from the safetensors file.
pt_file = dir_model / "model.safetensors"
if not pt_file.exists():
    print("Error: model.safetensors not found in", pt_file)
    sys.exit(1)
# The safetensors library loads weight tensors in a dictionary.
list_vars = load_file(str(pt_file), device="cpu")

# Load mel filters based on the number of mel bins.
n_mels = hparams["num_mel_bins"]
with np.load(os.path.join(dir_whisper, "whisper/assets", "mel_filters.npz")) as f:
    filters = torch.from_numpy(f[f"mel_{n_mels}"])

# Assuming that the tokenizer is stored in the same folder as the model.
dir_tokenizer = dir_model

# Set output filename based on whether f16 or f32 conversion is used.
fname_out = dir_out / "ggml-model.bin"

tokens = json.load(open(dir_tokenizer / "vocab.json", "r", encoding="utf8"))

# Use 16-bit or 32-bit floats.
use_f16 = True
if len(sys.argv) > 4:
    use_f16 = False
    fname_out = dir_out / "ggml-model-f32.bin"

fout = open(fname_out, "wb")

# Write the header information.
fout.write(struct.pack("i", 0x67676d6c))  # magic: ggml in hex
fout.write(struct.pack("i", hparams["vocab_size"]))
fout.write(struct.pack("i", hparams["max_source_positions"]))
fout.write(struct.pack("i", hparams["d_model"]))
fout.write(struct.pack("i", hparams["encoder_attention_heads"]))
fout.write(struct.pack("i", hparams["encoder_layers"]))
fout.write(struct.pack("i", hparams["max_length"]))
fout.write(struct.pack("i", hparams["d_model"]))
fout.write(struct.pack("i", hparams["decoder_attention_heads"]))
fout.write(struct.pack("i", hparams["decoder_layers"]))
fout.write(struct.pack("i", hparams["num_mel_bins"]))
fout.write(struct.pack("i", use_f16))

# Write the mel filter dimensions and the filter data.
fout.write(struct.pack("i", filters.shape[0]))
fout.write(struct.pack("i", filters.shape[1]))
for i in range(filters.shape[0]):
    for j in range(filters.shape[1]):
        fout.write(struct.pack("f", filters[i][j]))

# Write the vocabulary information.
byte_encoder = bytes_to_unicode()
byte_decoder = {v: k for k, v in byte_encoder.items()}

fout.write(struct.pack("i", len(tokens)))
tokens = sorted(tokens.items(), key=lambda x: x[1])
for key in tokens:
    # Convert the token string to its byte representation.
    text = bytearray([byte_decoder[c] for c in key[0]])
    fout.write(struct.pack("i", len(text)))
    fout.write(text)

# Process and write each variable in the state dictionary.
for name in list_vars.keys():
    # Some variables are skipped (e.g. proj_out.weight).
    if name == "proj_out.weight":
        print("Skipping", name)
        continue

    src = name
    nn = name
    if name != "proj_out.weight":
        nn = nn.split(".")[1:]
    else:
        nn = nn.split(".")

    if nn[1] == "layers":
        nn[1] = "blocks"
        if ".".join(nn[3:-1]) == "encoder_attn.k_proj":
            mapped = "attn.key" if nn[0] == "encoder" else "cross_attn.key"
        else:
            mapped = conv_map[".".join(nn[3:-1])]
        name = ".".join(nn[:3] + [mapped] + nn[-1:])
    else:
        name = ".".join(nn)
        name = conv_map[name] if name in conv_map else name

    print(src, " -> ", name)
    # Convert the tensor to a NumPy array.
    data = list_vars[src].squeeze().numpy()
    data = data.astype(np.float16)

    # Reshape convolutional biases if needed.
    if name in ["encoder.conv1.bias", "encoder.conv2.bias"]:
        data = data.reshape(data.shape[0], 1)
        print("  Reshaped variable:", name, "to shape:", data.shape)

    n_dims = len(data.shape)
    print(name, n_dims, data.shape)

    # Determine whether to use float16 or fall back to float32 for small tensors.
    ftype = 1  # 1 -> float16, 0 -> float32
    if use_f16:
        if n_dims < 2 or \
           name in ["encoder.conv1.bias", "encoder.conv2.bias", 
                    "encoder.positional_embedding", "decoder.positional_embedding"]:
            print("  Converting to float32")
            data = data.astype(np.float32)
            ftype = 0
    else:
        data = data.astype(np.float32)
        ftype = 0

    # Write the header for this variable.
    str_ = name.encode("utf-8")
    fout.write(struct.pack("iii", n_dims, len(str_), ftype))
    for i in range(n_dims):
        fout.write(struct.pack("i", data.shape[n_dims - 1 - i]))
    fout.write(str_)

    # Write the tensor data.
    data.tofile(fout)

fout.close()

print("Done. Output file:", fname_out)
