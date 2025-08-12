"""
Nepali T5 Data Cleaning + Preprocessing + PCA
-------------------------------------------------
This script provides a full pipeline for:
 1. Loading raw Nepali corpora (news articles with title & summary, Nepali textbooks, etc.)
 2. Text cleaning & normalization tailored to Devanagari (Nepali)
 3. Deduplication and filtering
 4. Saving cleaned text for T5 fine-tuning (optionally train SentencePiece)
 5. Dimensionality reduction / PCA analysis on TF-IDF features (or model embeddings)

Notes / Prerequisites:
  - Python 3.8+
  - pip install pandas scikit-learn matplotlib tqdm sentencepiece regex
  - Optional (for embeddings + fine-tuning): pip install transformers torch
  - This script assumes input files are CSV/JSON/TSV where each record contains `title` and `summary` fields

Usage examples (from command line):
  python nepali_t5_preprocessing.py --input-files data/news1.csv data/textbook.jsonl --outdir cleaned/ --train-spm --spm-model spm.model


Caveats:
  - Sentencepiece training and downloading transformer models require internet and may take time.
  - Customize regex or keep/remove patterns depending on how "noisy" your corpus is.

Author: ChatGPT (helper code) — adapt as needed for your environment.
"""

import os
import re
import json
import csv
import argparse
import unicodedata
from pathlib import Path
from typing import List, Iterable, Optional, Tuple

import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Optional imports for sentencepiece and transformers
try:
    import sentencepiece as spm
except Exception:
    spm = None

try:
    import torch
    from transformers import T5Tokenizer, T5ForConditionalGeneration, T5EncoderModel
except Exception:
    torch = None


# -----------------------------
# Cleaning / Normalization
# -----------------------------

# Define common regexes
URL_RE = re.compile(r"https?://\S+|www\.\S+")
EMAIL_RE = re.compile(r"\S+@\S+")
HTML_TAG_RE = re.compile(r"<[^>]+>")
NON_PRINTABLE_RE = re.compile(r"[\x00-\x1F\x7F]+")
MULTI_WS_RE = re.compile(r"\s+")

# Keep Devanagari letters, Latin letters, digits and common punctuation
# Devanagari block: \u0900-\u097F
DEVANAGARI_KEEP_RE = re.compile(r"[^\u0900-\u097Fa-zA-Z0-9\s\u0964\u0965\-\.,;:!?"'()\[\]{}॥—–•]", flags=re.UNICODE)
# Note: \u0964 = danda (।) and \u0965 = double danda (॥)

# Common Nepali punctuation normalization mapping
PUNCT_MAP = {
    '\u0964': '.',  # danda to period
    '\u0965': '.',  # double danda to period
    '।': '.',
    '॥': '.',
    '\u200C': '',  # remove ZWNJ
}


def normalize_unicode(text: str) -> str:
    """Normalize unicode and apply canonical composition."""
    # NFKC groups compatibility characters. NFKC or NFC may be chosen based on needs.
    text = unicodedata.normalize('NFKC', text)
    return text


def replace_punct(text: str) -> str:
    for k, v in PUNCT_MAP.items():
        text = text.replace(k, v)
    return text


def remove_urls_emails_html(text: str) -> str:
    text = URL_RE.sub(' ', text)
    text = EMAIL_RE.sub(' ', text)
    text = HTML_TAG_RE.sub(' ', text)
    return text


def remove_non_printable(text: str) -> str:
    return NON_PRINTABLE_RE.sub(' ', text)


def keep_devanagari_and_basic(text: str) -> str:
    # This will strip some characters that are not Devanagari/ASCII/punct
    return DEVANAGARI_KEEP_RE.sub(' ', text)


def clean_whitespace(text: str) -> str:
    # Collapse whitespace to single space and strip
    return MULTI_WS_RE.sub(' ', text).strip()


def basic_nepali_cleanup(text: str, keep_latin: bool = True) -> str:
    """Run a sequence of cleaning steps aimed at Nepali (Devanagari) text.
    keep_latin: if True, keep Latin words (useful for named entities / urls previously removed)
    """
    if not isinstance(text, str):
        return ''
    text = text.strip()
    text = normalize_unicode(text)
    text = replace_punct(text)
    text = remove_urls_emails_html(text)
    text = remove_non_printable(text)
    if not keep_latin:
        # remove Latin letters as well
        text = re.sub(r'[A-Za-z]', ' ', text)
    text = keep_devanagari_and_basic(text)
    text = clean_whitespace(text)
    return text


# -----------------------------
# Loading helpers
# -----------------------------

def read_csv_jsonl(filepath: Path, title_field: str = 'title', summary_field: str = 'summary') -> pd.DataFrame:
    """Try to read CSV/TSV/JSON/JSONL and return DataFrame with columns [title, summary]."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    rows = []
    if suffix in ['.csv', '.tsv']:
        sep = '\t' if suffix == '.tsv' else ','
        df = pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False)
        if title_field not in df.columns or summary_field not in df.columns:
            # try to infer
            common_titles = [c for c in df.columns if 'title' in c.lower()][:1]
            common_summ = [c for c in df.columns if any(k in c.lower() for k in ['summary','summ','desc','description'])][:1]
            t = common_titles[0] if common_titles else title_field
            s = common_summ[0] if common_summ else summary_field
            df = df.rename(columns={t: title_field, s: summary_field})
        df = df[[title_field, summary_field]].fillna('').astype(str)
        return df

    if suffix == '.json' or suffix == '.jsonl':
        # jsonl: one json per line or full json list
        with open(path, 'r', encoding='utf-8') as f:
            first = f.read(1000).lstrip()
            f.seek(0)
            if first.startswith('['):
                data = json.load(f)
            else:
                data = [json.loads(line) for line in f if line.strip()]
        # build rows
        for item in data:
            t = item.get(title_field, '')
            s = item.get(summary_field, '')
            rows.append({title_field: str(t), summary_field: str(s)})
        return pd.DataFrame(rows)

    raise ValueError(f"Unsupported file type: {suffix}")


def load_multiple(files: List[str], title_field: str = 'title', summary_field: str = 'summary') -> pd.DataFrame:
    dfs = []
    for f in files:
        try:
            df = read_csv_jsonl(Path(f), title_field=title_field, summary_field=summary_field)
            dfs.append(df)
        except Exception as e:
            print(f"Warning: couldn't read {f}: {e}")
    if not dfs:
        return pd.DataFrame(columns=[title_field, summary_field])
    out = pd.concat(dfs, ignore_index=True).fillna('')
    # ensure columns exist
    out = out[[title_field, summary_field]]
    out.columns = ['title', 'summary']
    return out


# -----------------------------
# Dedupe and filters
# -----------------------------

def dedupe_dataframe(df: pd.DataFrame, subset: List[str] = ['title', 'summary']) -> pd.DataFrame:
    # drop exact duplicates
    before = len(df)
    df = df.drop_duplicates(subset=subset).reset_index(drop=True)
    after = len(df)
    print(f"Dropped {before - after} exact duplicates.")
    return df


def filter_by_length(df: pd.DataFrame, min_tokens: int = 3, max_tokens: int = 500, field: str = 'summary') -> pd.DataFrame:
    def token_count(s: str) -> int:
        return len(s.split()) if s else 0
    mask = df[field].map(token_count).between(min_tokens, max_tokens)
    kept = mask.sum()
    print(f"Keeping {kept}/{len(df)} rows based on `{field}` length filter.")
    return df[mask].reset_index(drop=True)


# -----------------------------
# Save outputs for T5 training
# -----------------------------

def prepare_t5_text_files(df: pd.DataFrame, outdir: Path, prefix: str = 'train') -> Tuple[Path, Path]:
    """Create two text files: inputs (title / summary prompts) and targets (ground truth)
    For T5, typical format: "summarize: <text>\t<target>" or you can create separate files.
    We'll create a TSV with input \t target per row for convenience.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    tsv_path = outdir / f'{prefix}_t5.tsv'
    with open(tsv_path, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            # Example: use title as input, summary as target
            inp = row['title'].strip()
            tgt = row['summary'].strip()
            if not inp or not tgt:
                continue
            # escape tabs/newlines
            inp = inp.replace('\t', ' ').replace('\n', ' ')
            tgt = tgt.replace('\t', ' ').replace('\n', ' ')
            f.write(inp + '\t' + tgt + '\n')
    print(f"Saved T5 TSV at: {tsv_path}")
    return tsv_path


# -----------------------------
# SentencePiece training
# -----------------------------

def train_sentencepiece(clean_text_file: str, model_prefix: str = 'spm', vocab_size: int = 32000, model_type: str = 'unigram') -> None:
    if spm is None:
        raise RuntimeError('sentencepiece is not installed. pip install sentencepiece')
    # Build train command
    cmd = f"--input={clean_text_file} --model_prefix={model_prefix} --vocab_size={vocab_size} --model_type={model_type} --hard_vocab_limit=false"
    spm.SentencePieceTrainer.Train(cmd)
    print(f"Trained SentencePiece model: {model_prefix}.model")


# -----------------------------
# TF-IDF + PCA / TruncatedSVD pipeline
# -----------------------------

def tfidf_and_pca(corpus: Iterable[str], n_components: int = 50, max_features: int = 50000, use_svd: bool = True) -> Tuple[TfidfVectorizer, np.ndarray, object]:
    """Compute TF-IDF, then reduce using TruncatedSVD (recommended for sparse TF-IDF) or PCA.
    Returns (vectorizer, transformed_matrix, reducer)
    """
    vectorizer = TfidfVectorizer(max_features=max_features, analyzer='word', token_pattern=r'\S+', ngram_range=(1,2))
    X = vectorizer.fit_transform(corpus)
    print(f"TF-IDF matrix shape: {X.shape}")

    if use_svd:
        reducer = TruncatedSVD(n_components=n_components, random_state=42)
        X_reduced = reducer.fit_transform(X)
        explained = getattr(reducer, 'explained_variance_ratio_', None)
    else:
        # Dense path (may be memory heavy)
        X_dense = X.toarray()
        scaler = StandardScaler(with_mean=True)
        Xs = scaler.fit_transform(X_dense)
        reducer = PCA(n_components=n_components, random_state=42)
        X_reduced = reducer.fit_transform(Xs)
        explained = reducer.explained_variance_ratio_

    print(f"Reduced matrix shape: {X_reduced.shape}")
    if explained is not None:
        print(f"Sum explained variance (first {min(len(explained), 10)}): {explained[:10].sum():.4f}")
    return vectorizer, X_reduced, reducer


# -----------------------------
# Optional: Compute PCA on model embeddings (T5 encoder)
# -----------------------------

def compute_t5_encoder_embeddings(texts: List[str], model_name: str = 't5-small', batch_size: int = 8, device: Optional[str] = None) -> np.ndarray:
    """Compute encoder embeddings for each input text using T5 encoder's last hidden state pooled by mean.
    Requires `transformers` and `torch`. Model download required.
    Returns (N, hidden_size) numpy array.
    """
    if torch is None:
        raise RuntimeError('transformers/torch not installed. pip install transformers torch')
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Load tokenizer and encoder model
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5EncoderModel.from_pretrained(model_name).to(device)
    model.eval()

    all_embeds = []
    with torch.no_grad():
        for i in tqdm(range(0, len(texts), batch_size), desc='Embedding batches'):
            batch_texts = texts[i:i+batch_size]
            enc = tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
            input_ids = enc.input_ids.to(device)
            attention_mask = enc.attention_mask.to(device)
            outs = model(input_ids=input_ids, attention_mask=attention_mask)
            # outs.last_hidden_state: (batch, seq_len, hidden)
            last = outs.last_hidden_state
            # mean pool over non-padding tokens
            mask = attention_mask.unsqueeze(-1)
            summed = (last * mask).sum(dim=1)
            lens = mask.sum(dim=1).clamp(min=1)
            mean_pooled = (summed / lens).cpu().numpy()
            all_embeds.append(mean_pooled)
    all_embeds = np.vstack(all_embeds)
    return all_embeds


# -----------------------------
# Visualization helpers
# -----------------------------

def plot_explained_variance(reducer, outpath: Optional[Path] = None):
    if hasattr(reducer, 'explained_variance_ratio_'):
        evr = reducer.explained_variance_ratio_
    elif hasattr(reducer, 'explained_variance_ratio'):
        evr = reducer.explained_variance_ratio
    else:
        print('Reducer has no explained variance info')
        return
    cum = np.cumsum(evr)
    plt.figure(figsize=(6,4))
    plt.plot(np.arange(1, len(evr)+1), cum, marker='o')
    plt.xlabel('Number of components')
    plt.ylabel('Cumulative explained variance')
    plt.title('Explained variance by components')
    plt.grid(True)
    if outpath:
        plt.savefig(outpath, bbox_inches='tight')
        print(f"Saved explained variance plot to: {outpath}")
    else:
        plt.show()


def plot_2d_scatter(X_reduced: np.ndarray, labels: Optional[List[str]] = None, outpath: Optional[Path] = None):
    plt.figure(figsize=(6,6))
    x = X_reduced[:,0]
    y = X_reduced[:,1]
    plt.scatter(x, y, s=6, alpha=0.6)
    if labels is not None:
        # optional color by label
        pass
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title('2D PCA / SVD projection')
    plt.grid(True)
    if outpath:
        plt.savefig(outpath, bbox_inches='tight')
        print(f"Saved 2D scatter to: {outpath}")
    else:
        plt.show()


# -----------------------------
# Pipeline main
# -----------------------------

def run_pipeline(input_files: List[str], outdir: str = 'cleaned',
                 title_field: str = 'title', summary_field: str = 'summary',
                 min_tokens: int = 3, max_tokens: int = 500,
                 spm_train: bool = False, spm_prefix: str = 'spm', spm_vocab: int = 32000,
                 pca_components: int = 50, max_features: int = 50000,
                 compute_model_embeddings: bool = False, model_name: str = 't5-small'):

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print('Loading files...')
    df = load_multiple(input_files, title_field=title_field, summary_field=summary_field)
    print(f'Loaded {len(df)} rows')

    # Clean
    print('Cleaning text...')
    for col in ['title', 'summary']:
        df[col] = df[col].astype(str).map(lambda t: basic_nepali_cleanup(t, keep_latin=True))

    # Drop empty rows
    df = df[(df['title'].str.strip() != '') & (df['summary'].str.strip() != '')].reset_index(drop=True)
    print(f'After removing empty rows: {len(df)}')

    df = dedupe_dataframe(df)
    df = filter_by_length(df, min_tokens=min_tokens, max_tokens=max_tokens, field='summary')

    # Save cleaned CSV
    cleaned_csv = outdir / 'cleaned_nepali_corpus.csv'
    df.to_csv(cleaned_csv, index=False)
    print(f'Saved cleaned CSV -> {cleaned_csv}')

    # Prepare T5-friendly TSV
    tsv_path = prepare_t5_text_files(df, outdir, prefix='train')

    # For sentencepiece: create a combined plain text file of all summaries+titles
    if spm_train:
        if spm is None:
            print('sentencepiece not installed, skipping spm training')
        else:
            combined_txt = outdir / 'combined_for_spm.txt'
            with open(combined_txt, 'w', encoding='utf-8') as f:
                for txt in pd.concat([df['title'], df['summary']]).astype(str):
                    f.write(txt.replace('\n',' ') + '\n')
            train_sentencepiece(str(combined_txt), model_prefix=spm_prefix, vocab_size=spm_vocab)

    # TF-IDF + PCA/SVD
    print('Computing TF-IDF + SVD (PCA-like)...')
    corpus = (df['title'] + '. ' + df['summary']).tolist()
    vect, X_reduced, reducer = tfidf_and_pca(corpus, n_components=pca_components, max_features=max_features, use_svd=True)

    # Save reduced matrix
    np.save(outdir / 'reduced_embeddings.npy', X_reduced)
    print(f'Saved reduced embeddings to {outdir/"reduced_embeddings.npy"}')

    # Plot variance and 2D scatter
    plot_explained_variance(reducer, outpath=outdir / 'explained_variance.png')
    if X_reduced.shape[1] >= 2:
        plot_2d_scatter(X_reduced[:, :2], outpath=outdir / 'pca_scatter.png')

    # Optional: compute encoder embeddings and PCA on them
    if compute_model_embeddings:
        if torch is None:
            print('transformers/torch not installed, cannot compute model embeddings')
        else:
            texts = df['summary'].tolist()
            embeds = compute_t5_encoder_embeddings(texts, model_name=model_name)
            print(f'Embeddings shape: {embeds.shape}')
            pca = PCA(n_components=min(50, embeds.shape[1]), random_state=42)
            E_reduced = pca.fit_transform(embeds)
            np.save(outdir / 't5_encoder_reduced.npy', E_reduced)
            plot_explained_variance(pca, outpath=outdir / 't5_explained_variance.png')
            if E_reduced.shape[1] >= 2:
                plot_2d_scatter(E_reduced[:, :2], outpath=outdir / 't5_pca_scatter.png')

    print('Pipeline finished.')


# -----------------------------
# CLI
# -----------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Nepali T5 preprocessing + PCA analysis')
    parser.add_argument('--input-files', nargs='+', required=True, help='Input CSV/JSON/TSV/JSONL files')
    parser.add_argument('--outdir', default='cleaned', help='Output directory')
    parser.add_argument('--min-tokens', type=int, default=3)
    parser.add_argument('--max-tokens', type=int, default=500)
    parser.add_argument('--train-spm', action='store_true', help='Train sentencepiece model')
    parser.add_argument('--spm-prefix', default='spm')
    parser.add_argument('--spm-vocab', type=int, default=32000)
    parser.add_argument('--pca-components', type=int, default=50)
    parser.add_argument('--max-features', type=int, default=50000)
    parser.add_argument('--compute-model-embeddings', action='store_true', help='Compute T5 encoder embeddings and run PCA')
    parser.add_argument('--model-name', default='t5-small')

    args = parser.parse_args()
    run_pipeline(args.input_files, outdir=args.outdir, min_tokens=args.min_tokens, max_tokens=args.max_tokens,
                 spm_train=args.train_spm, spm_prefix=args.spm_prefix, spm_vocab=args.spm_vocab,
                 pca_components=args.pca_components, max_features=args.max_features,
                 compute_model_embeddings=args.compute_model_embeddings, model_name=args.model_name)
