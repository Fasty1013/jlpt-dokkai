#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Validator Module for JLPT Dokkai Master.
Validates PDF integrity, magic bytes, encryption, size, page count,
and detects whether pages contain a digital text layer or are raster scans.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple
import pypdf

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_PAGE_COUNT = 500

def compute_file_hash(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def validate_pdf_file(file_path: Path) -> Dict[str, Any]:
    """
    Validates PDF file for safety and processing feasibility.
    Returns:
      {
        "is_valid": bool,
        "error": Optional[str],
        "file_hash": str,
        "file_size_bytes": int,
        "page_count": int,
        "has_text_layer": bool,
        "is_scanned": bool,
        "ocr_available": bool
      }
    """
    if not file_path.exists() or not file_path.is_file():
        return {
            "is_valid": False,
            "error": f"Файл не найден или не является файлом: {file_path}",
            "file_hash": "",
            "file_size_bytes": 0,
            "page_count": 0,
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    size = file_path.stat().st_size
    if size == 0:
        return {
            "is_valid": False,
            "error": "Файл пуст (размер 0 байт)",
            "file_hash": "",
            "file_size_bytes": 0,
            "page_count": 0,
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    if size > MAX_FILE_SIZE_BYTES:
        return {
            "is_valid": False,
            "error": f"Размер файла превышает лимит {MAX_FILE_SIZE_BYTES // (1024*1024)} МБ (фактически: {size // (1024*1024)} МБ)",
            "file_hash": "",
            "file_size_bytes": size,
            "page_count": 0,
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    # Check magic bytes
    with open(file_path, "rb") as f:
        header = f.read(8)
    if not header.startswith(b"%PDF-") and not header.startswith(b"%PDF"):
        return {
            "is_valid": False,
            "error": "Некорректный заголовок файла (magic bytes): не является валидным PDF документом",
            "file_hash": "",
            "file_size_bytes": size,
            "page_count": 0,
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    file_hash = compute_file_hash(file_path)

    # Open with pypdf
    try:
        reader = pypdf.PdfReader(str(file_path))
    except Exception as e:
        return {
            "is_valid": False,
            "error": f"Повреждённая структура PDF или ошибка парсера: {e}",
            "file_hash": file_hash,
            "file_size_bytes": size,
            "page_count": 0,
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    if reader.is_encrypted:
        return {
            "is_valid": False,
            "error": "PDF защищен паролем или зашифрован (обработка невозможна без ключа)",
            "file_hash": file_hash,
            "file_size_bytes": size,
            "page_count": len(reader.pages),
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    page_count = len(reader.pages)
    if page_count == 0:
        return {
            "is_valid": False,
            "error": "В документе отсутствуют страницы",
            "file_hash": file_hash,
            "file_size_bytes": size,
            "page_count": 0,
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    if page_count > MAX_PAGE_COUNT:
        return {
            "is_valid": False,
            "error": f"Число страниц превышает лимит {MAX_PAGE_COUNT} (фактически: {page_count})",
            "file_hash": file_hash,
            "file_size_bytes": size,
            "page_count": page_count,
            "has_text_layer": False,
            "is_scanned": False,
            "ocr_available": False
        }

    # Inspect text layer vs raster scan
    total_text_len = 0
    sample_pages = min(page_count, 10)
    for p_idx in range(sample_pages):
        try:
            page_text = reader.pages[p_idx].extract_text() or ""
            total_text_len += len(page_text.strip())
        except Exception:
            pass

    has_text_layer = (total_text_len >= 20)
    is_scanned = not has_text_layer

    # Check OCR availability
    ocr_available = False
    try:
        import subprocess
        res = subprocess.run(["where.exe", "tesseract"], capture_output=True)
        ocr_available = (res.returncode == 0)
    except Exception:
        ocr_available = False

    return {
        "is_valid": True,
        "error": None,
        "file_hash": file_hash,
        "file_size_bytes": size,
        "page_count": page_count,
        "has_text_layer": has_text_layer,
        "is_scanned": is_scanned,
        "ocr_available": ocr_available
    }
