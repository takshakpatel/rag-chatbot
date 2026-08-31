"""Extract images from PDFs using PyMuPDF (fitz).

Each image is saved to `extracted_images/<doc_stem>/` and a LangChain Document
is created with metadata describing the image source, page, and any caption
text found nearby on the same page.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pymupdf as fitz  # PyMuPDF
from langchain_core.documents import Document


def extract_images_from_pdf(
    pdf_path: str | Path,
    out_dir: str | Path = "extracted_images",
    min_width: int = 100,
    min_height: int = 100,
) -> list[Document]:
    """Extract visible images from a PDF and return Document objects."""
    pdf_path = Path(pdf_path)
    doc_stem = pdf_path.stem
    save_dir = Path(out_dir) / doc_stem
    save_dir.mkdir(parents=True, exist_ok=True)

    pdf = fitz.open(str(pdf_path))
    image_docs: list[Document] = []
    seen_hashes: set[str] = set()

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        images = page.get_images(full=True)

        # Collect text blocks on this page to find potential captions
        text_blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)

        for img_index, img_info in enumerate(images):
            xref = img_info[0]
            try:
                pix = fitz.Pixmap(pdf, xref)
            except Exception:
                continue

            # Skip tiny images (icons, bullets, lines)
            if pix.width < min_width or pix.height < min_height:
                continue

            # Skip duplicate images (same pixel content)
            img_bytes = pix.tobytes("png")
            img_hash = hashlib.md5(img_bytes).hexdigest()
            if img_hash in seen_hashes:
                continue
            seen_hashes.add(img_hash)

            # Save image
            img_filename = f"page{page_num + 1}_img{img_index + 1}.png"
            img_path = save_dir / img_filename
            img_path.write_bytes(img_bytes)

            # Find nearest text below the image (potential caption)
            caption = _find_caption(text_blocks, img_info, page)

            image_docs.append(
                Document(
                    page_content=f"[Image: {img_filename}] {caption}".strip(),
                    metadata={
                        "source": str(pdf_path),
                        "filename": pdf_path.name,
                        "type": "image",
                        "image_path": str(img_path),
                        "page": page_num + 1,
                        "width": pix.width,
                        "height": pix.height,
                        "caption": caption,
                        "chunk_index": len(image_docs),
                    },
                )
            )

    pdf.close()
    return image_docs


def _find_caption(
    text_blocks: list, img_info: tuple, page
) -> str:
    """Find the nearest text block below an image (likely a caption)."""
    try:
        # img_info: (xref, smask, width, height, bpc, colorspace, alt_colorspace, name, referencer)
        img_rect = page.get_image_rects(img_info[0])
        if not img_rect:
            return ""
        rect = img_rect[0]
    except Exception:
        return ""

    captions = []
    for block in text_blocks:
        if block[6] != 0:  # only text blocks (type 0)
            continue
        x0, y0, x1, y1, text = block[0], block[1], block[2], block[3], block[4]
        text = text.strip()
        if not text or len(text) < 5:
            continue
        # Caption is usually just below the image, within ~50px, and roughly same horizontal position
        if (
            y0 >= rect.y1
            and y0 - rect.y1 < 60
            and x0 < rect.x1 + 20
            and x1 > rect.x0 - 20
        ):
            captions.append(text)

    return " ".join(captions[:2]) if captions else ""


def extract_all_images(
    paths: list[str | Path],
    out_dir: str | Path = "extracted_images",
) -> list[Document]:
    """Run image extraction across multiple files. Returns flat list of image Documents."""
    all_docs: list[Document] = []
    for p in paths:
        p = Path(p)
        if p.suffix.lower() == ".pdf":
            all_docs.extend(extract_images_from_pdf(p, out_dir=out_dir))
    return all_docs
