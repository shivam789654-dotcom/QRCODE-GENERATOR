"""QR generation service."""
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

class QRGenerator:
    def create(self, data, error="M", box_size=10, border=4,
               fill="#111827", back="#ffffff"):
        if not isinstance(data, str) or not data.strip():
            raise ValueError("QR content cannot be empty.")
        if error not in ERROR_LEVELS:
            raise ValueError("Unsupported error-correction level.")
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_LEVELS[error],
            box_size=int(box_size),
            border=int(border),
        )
        qr.add_data(data.strip())
        qr.make(fit=True)
        return qr.make_image(fill_color=fill, back_color=back).convert("RGB")
