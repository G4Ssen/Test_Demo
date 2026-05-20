"""
generate_testdata.py
────────────────────
Creates the minimal PDF test fixtures required by the Karate test suite.
Run once before executing Karate tests:

    python generate_testdata.py

Output directory:  tests/karate/src/test/resources/testdata/
"""

import os
import struct

# ── Minimal valid PDF factory ─────────────────────────────────────────────────

def _build_pdf(text_lines: list[str]) -> bytes:
    """
    Build a single-page PDF embedding *text_lines* as visible BT/ET text.
    The PDF is plain ASCII, no compression — small but fully spec-compliant.
    """
    body_text = "\n".join(f"({line}) Tj" for line in text_lines)

    stream = (
        "BT\n"
        "/F1 12 Tf\n"
        "50 750 Td\n"
        f"{body_text}\n"
        "ET"
    )
    stream_bytes = stream.encode()
    stream_len = len(stream_bytes)

    # Object map:
    # 1 = catalog, 2 = pages, 3 = page, 4 = font, 5 = content stream
    objects: dict[int, bytes] = {}

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[2] = b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    objects[3] = (
        b"<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] "
        b"/Contents 5 0 R "
        b"/Resources << /Font << /F1 4 0 R >> >> >>"
    )
    objects[4] = (
        b"<< /Type /Font /Subtype /Type1 "
        b"/BaseFont /Helvetica >>"
    )
    objects[5] = (
        f"<< /Length {stream_len} >>\nstream\n".encode()
        + stream_bytes
        + b"\nendstream"
    )

    # Serialise
    lines: list[bytes] = [b"%PDF-1.4\n"]
    offsets: dict[int, int] = {}

    for obj_id in sorted(objects):
        offsets[obj_id] = len(b"".join(lines))
        lines.append(f"{obj_id} 0 obj\n".encode())
        lines.append(objects[obj_id])
        lines.append(b"\nendobj\n")

    # Cross-reference table
    xref_offset = len(b"".join(lines))
    lines.append(b"xref\n")
    lines.append(f"0 {max(objects) + 1}\n".encode())
    lines.append(b"0000000000 65535 f \n")
    for obj_id in sorted(objects):
        lines.append(f"{offsets[obj_id]:010d} 00000 n \n".encode())

    lines.append(b"trailer\n")
    lines.append(f"<< /Size {max(objects) + 1} /Root 1 0 R >>\n".encode())
    lines.append(b"startxref\n")
    lines.append(f"{xref_offset}\n".encode())
    lines.append(b"%%EOF\n")

    return b"".join(lines)


# ── Test document definitions ─────────────────────────────────────────────────

DOCUMENTS = {
    "invoice_sample.pdf": [
        "INVOICE",
        "Invoice No: 12345",
        "Bill To: ACME Corp",
        "Date: 15/09/2025",
        "Payment Terms: Net 30",
        "Subtotal: 1000.00",
        "VAT: 200.00",
        "Total: 1200.00",
        "Amount Due: 1200.00",
    ],
    "identity_sample.pdf": [
        "PASSPORT",
        "Surname: DOE",
        "Given Names: JOHN",
        "Nationality: GBR",
        "Date of Birth: 01/01/1990",
        "Expiry Date: 01/01/2030",
        "National ID: AB123456",
    ],
    "report_sample.pdf": [
        "ANNUAL REPORT 2025",
        "Executive Summary",
        "This report presents the findings of the 2025 audit.",
        "Methodology",
        "Section 1: Introduction",
        "Findings",
        "Recommendations",
        "Conclusion",
        "Figure 1: Revenue growth",
    ],
    "contract_sample.pdf": [
        "SERVICE AGREEMENT",
        "This agreement is entered into by the parties below.",
        "Whereas both parties agree to the following terms:",
        "Article 1: Obligations of the Service Provider",
        "Article 2: Payment Terms",
        "Article 3: Termination",
        "Clause 4: Governing Law",
        "Hereby agreed by both parties.",
    ],
}


def _make_corrupted_pdf() -> bytes:
    """A file that starts with %PDF but is structurally invalid."""
    return b"%PDF-1.4\nThis is not a valid PDF structure."


def _make_oversized_pdf(target_mb: int = 21) -> bytes:
    """Valid PDF header + padding to exceed the 20 MB upload limit."""
    base = _build_pdf(["Oversized test document"])
    padding = b"%% padding\n" * ((target_mb * 1024 * 1024) // 11 + 1)
    return base + padding


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    out_dir = os.path.join(
        os.path.dirname(__file__),
        "tests", "karate", "src", "test", "resources", "testdata",
    )
    os.makedirs(out_dir, exist_ok=True)

    print(f"Writing test PDFs to: {os.path.abspath(out_dir)}\n")

    for filename, lines in DOCUMENTS.items():
        path = os.path.join(out_dir, filename)
        pdf_bytes = _build_pdf(lines)
        with open(path, "wb") as f:
            f.write(pdf_bytes)
        print(f"  [OK]  {filename:40s}  ({len(pdf_bytes):,} bytes)")

    # Corrupted PDF
    path = os.path.join(out_dir, "corrupted.pdf")
    with open(path, "wb") as f:
        f.write(_make_corrupted_pdf())
    print(f"  [OK]  corrupted.pdf")

    # Oversized PDF (>20 MB)
    path = os.path.join(out_dir, "oversized.pdf")
    data = _make_oversized_pdf(21)
    with open(path, "wb") as f:
        f.write(data)
    print(f"  [OK]  oversized.pdf  ({len(data) / 1024 / 1024:.1f} MB)")

    print("\nDone. Test data ready for Karate.")


if __name__ == "__main__":
    main()
