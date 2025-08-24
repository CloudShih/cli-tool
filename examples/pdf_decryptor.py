"""Utility for decrypting PDF files using :mod:`pikepdf`.

The module exposes :func:`decrypt_pdf` which can be imported by other code and
also provides a simple command line interface when executed directly.
"""

from __future__ import annotations

import argparse
import pikepdf


def decrypt_pdf(input_path: str, output_path: str, password: str | None = None) -> bool:
    """Decrypt ``input_path`` and write the result to ``output_path``.

    Parameters
    ----------
    input_path: str
        Path to the encrypted PDF file.
    output_path: str
        Destination path for the decrypted PDF.
    password: str | None, optional
        Password for the PDF, if required.

    Returns
    -------
    bool
        ``True`` if the file was decrypted successfully, ``False`` otherwise.
    """

    try:
        pdf = pikepdf.open(input_path, password=password)
        pdf.save(output_path)
        return True
    except pikepdf.PasswordError:
        print(f"Error: Incorrect password for {input_path}")
    except Exception as exc:  # pragma: no cover - unexpected errors
        print(f"Error decrypting PDF: {exc}")
    return False


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decrypt a PDF file")
    parser.add_argument("input_path", help="Path to the encrypted PDF")
    parser.add_argument("output_path", help="Destination path for the decrypted PDF")
    parser.add_argument("-p", "--password", help="Password for the PDF", default=None)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    success = decrypt_pdf(args.input_path, args.output_path, args.password)
    if success:
        print(f"PDF successfully decrypted and saved to: {args.output_path}")
    else:
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

