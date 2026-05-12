---
name: chinese-handwriting-ocr
version: 1.0.1
description: Chinese OCR dual-engine — PaddleOCR (document OCR) + RapidOCR (handwriting specialized), switchable on demand.
---

# Chinese OCR Dual-Engine v2.0

> Dual-engine: **PaddleOCR** for general document OCR + **RapidOCR** for handwriting specialization. Auto/manual engine switching per use case.

## Engine Selection

| Scenario | Recommended Engine | Rationale |
|----------|:------------------:|-----------|
| **Printed documents**, contracts, reports | `--engine paddle` | PaddleOCR best for Chinese printed text |
| **Handwriting**, dates, signatures, IDs | `--engine rapid` | RapidOCR more accurate for handwritten digits/text |
| **Mixed documents** (print + handwriting) | `--engine auto` | Auto-detect content type and switch |
| Not sure which to use | `--engine both` | Dual-engine cross-validate, take high-confidence result |

## Quick Start

```bash
# Handwritten date extraction (default: RapidOCR)
python scripts/ocr_date_extractor.py document.pdf

# Specify engine
python scripts/ocr_date_extractor.py document.pdf --engine rapid
python scripts/ocr_date_extractor.py document.pdf --engine paddle
python scripts/ocr_date_extractor.py document.pdf --engine both

# Extract region-specific handwriting
python scripts/ocr_rapid.py document.pdf --date-mode
python scripts/ocr_rapid.py document.pdf --signature-mode
```

## Core Scripts

### ocr_date_extractor.py — Date Extraction Engine

```
python scripts/ocr_date_extractor.py document.pdf [--engine rapid|paddle|both|auto]
```

Four-layer pipeline:
1. Dynamic date line location
2. Selected engine OCR
3. Smart value range validation
4. Document batch context inference

### ocr_rapid.py — Handwriting Region Extraction

```bash
python scripts/ocr_rapid.py document.pdf --date-mode --engine paddle
python scripts/ocr_rapid.py document.pdf --region 0.1 0.4 0.9 0.6 --engine both
```

### ocr_batch.py — Batch Processing

```bash
# Batch process all PDFs in directory
python scripts/ocr_batch.py --batch-dir ./pdfs --engine auto

# Dual-engine cross-validation
python scripts/ocr_batch.py --batch-dir ./pdfs --engine both --json -o results.json
```

## Engine Comparison

| Metric | PaddleOCR 2.8 | RapidOCR 1.4 |
|--------|:-------------:|:------------:|
| Printed Chinese | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Handwritten digits | ⭐⭐ | ⭐⭐⭐⭐ |
| Handwritten date exact match | 20% | 60% |
| Handwritten date partial match | 60% | 90%+ |
| First load | Slow (download models) | Fast (cached) |
| Speed | 3-5s/page | 2-3s/page |
| Package size | ~200MB+model | ~55MB |

## Auto Engine Selection (`--engine auto`)

```
1. Quick low-res OCR to analyze content type
2. Date keywords detected (year/month/day etc.) → RapidOCR
3. Large amount of printed text detected → PaddleOCR
4. Mixed content → both (dual-engine cross-validation)
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--engine rapid|paddle|both|auto` | OCR engine selection |
| `--json` | JSON format output |
| `-p, --pages` | Page range (1-based) |
| `--region X1 Y1 X2 Y2` | Custom region (percentage 0-1) |
| `--batch` | Batch process directory |
| `--dpi` | OCR resolution (default 400) |

## Dependencies

```bash
pip install rapidocr-onnxruntime    # Handwriting engine (installed ✅)
pip install paddleocr paddlepaddle  # Document OCR engine (installed ✅)
```

## Known Issues

- PaddleOCR 3.x + PaddlePaddle 3.x has OneDNN compatibility issues; using 2.x versions
- First PaddleOCR startup downloads model (~18MB)
- RapidOCR may leave process residue after multiple calls; periodic cleanup recommended
