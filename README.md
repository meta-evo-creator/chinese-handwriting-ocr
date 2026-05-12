# Chinese Handwriting OCR 🇨🇳⚡

> Dual-engine OCR skill — Intelligent extraction of handwritten dates, signatures, and IDs from scanned documents.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Architecture

| Engine | Role | Best for |
|--------|------|----------|
| **PaddleOCR** 🏆 | Primary | Printed documents, contracts, reports |
| **RapidOCR** | Fallback | Handwriting, dates, signatures, IDs |

## Quick Start

```bash
# Extract handwritten dates (default: RapidOCR)
python scripts/ocr_date_extractor.py document.pdf

# Specify engine
python scripts/ocr_date_extractor.py document.pdf --engine rapid
python scripts/ocr_date_extractor.py document.pdf --engine paddle
python scripts/ocr_date_extractor.py document.pdf --engine both
python scripts/ocr_date_extractor.py document.pdf --engine auto
```

## Smart Date Pipeline

```
Step 1 Dynamic location → Find date lines across full page
Step 2 High-res OCR → 450dpi extraction of date components
Step 3 Smart validation → Range checks + leading-1 inference
Step 4 Context inference → Fill missing parts from batch
```

## Installation

```bash
pip install rapidocr-onnxruntime    # Handwriting engine
pip install paddleocr paddlepaddle  # Document OCR engine
```

## Train Custom Model

```bash
# Train a handwritten digit CRNN from scratch
python scripts/train_crnn.py --samples 5000 --epochs 30
```

## License

MIT
