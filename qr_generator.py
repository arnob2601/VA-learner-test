"""
qr_generator.py
Self-contained, pure Python 3 QR Code generator with ZERO external dependencies.
Generates valid ISO/IEC 18004 Model 2 QR codes (Versions 1-4) as SVG or ASCII.
Perfect for offline local networks.
"""

# GF(256) math with primitive polynomial 0x11D (285)
EXP = [0] * 512
LOG = [0] * 256
x = 1
for i in range(255):
    EXP[i] = x
    EXP[i + 255] = x
    LOG[x] = i
    x <<= 1
    if x >= 256:
        x ^= 0x11D

def gf_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]

def rs_generator_poly(degree):
    poly = [1]
    for i in range(degree):
        # multiply poly by (x + EXP[i])
        new_poly = [0] * (len(poly) + 1)
        for j, c in enumerate(poly):
            new_poly[j] ^= gf_mul(c, EXP[i])
            new_poly[j + 1] ^= c
        poly = new_poly
    return poly

def rs_encode(data, num_ec):
    gen = rs_generator_poly(num_ec)
    msg = list(data) + [0] * num_ec
    for i in range(len(data)):
        lead = msg[i]
        if lead != 0:
            for j in range(len(gen)):
                msg[i + j] ^= gf_mul(gen[j], lead)
    return msg[len(data):]

# Version tables: (version, total_codewords, ec_codewords, align_centers)
# Using ECC Level L (Low) or M (Medium)
# For local URLs (~20-35 chars), Version 2 (25x25) or Version 3 (29x29) or Version 4 (33x33)
VERSION_SPECS = {
    1: {"size": 21, "data_cw_L": 19, "ec_cw_L": 7, "align": []},
    2: {"size": 25, "data_cw_L": 34, "ec_cw_L": 10, "align": [18]},
    3: {"size": 29, "data_cw_L": 55, "ec_cw_L": 15, "align": [22]},
    4: {"size": 33, "data_cw_L": 80, "ec_cw_L": 20, "align": [26]},
}

# Format info for Error Correction Level L with mask patterns 0..7
# Precomputed with BCH (15, 5) code and masked with 0x5412
FORMAT_INFO_L = [
    0x77C4, 0x72F3, 0x7DAA, 0x789D,
    0x662F, 0x6318, 0x6C41, 0x6976
]

class QRCode:
    def __init__(self, text):
        self.text = text
        data_bytes = text.encode('utf-8')
        
        # Determine smallest version
        self.version = 1
        for v in [1, 2, 3, 4]:
            if len(data_bytes) + 3 <= VERSION_SPECS[v]["data_cw_L"]:
                self.version = v
                break
        else:
            self.version = 4

        spec = VERSION_SPECS[self.version]
        self.size = spec["size"]
        self.matrix = [[None] * self.size for _ in range(self.size)]
        self.reserved = [[False] * self.size for _ in range(self.size)]
        
        self._build_function_patterns(spec)
        codewords = self._encode_data(data_bytes, spec["data_cw_L"], spec["ec_cw_L"])
        self._place_codewords(codewords)
        self._apply_best_mask(spec)

    def _build_function_patterns(self, spec):
        size = self.size
        # Finder patterns at (0,0), (size-7, 0), (0, size-7)
        for r, c in [(0, 0), (size - 7, 0), (0, size - 7)]:
            for i in range(-1, 8):
                for j in range(-1, 8):
                    nr, nc = r + i, c + j
                    if 0 <= nr < size and 0 <= nc < size:
                        self.reserved[nr][nc] = True
                        if 0 <= i <= 6 and 0 <= j <= 6:
                            is_black = (i in (0, 6) or j in (0, 6) or (2 <= i <= 4 and 2 <= j <= 4))
                            self.matrix[nr][nc] = 1 if is_black else 0
                        else:
                            self.matrix[nr][nc] = 0

        # Timing patterns
        for i in range(8, size - 8):
            self.matrix[6][i] = 1 if i % 2 == 0 else 0
            self.matrix[i][6] = 1 if i % 2 == 0 else 0
            self.reserved[6][i] = True
            self.reserved[i][6] = True

        # Alignment patterns
        for center in spec["align"]:
            # centers: (center, center)
            for i in range(-2, 3):
                for j in range(-2, 3):
                    nr, nc = center + i, center + j
                    if not self.reserved[nr][nc]:
                        self.reserved[nr][nc] = True
                        is_black = (max(abs(i), abs(j)) in (0, 2))
                        self.matrix[nr][nc] = 1 if is_black else 0

        # Dark module
        self.matrix[4 * self.version + 9][8] = 1
        self.reserved[4 * self.version + 9][8] = True

        # Reserve format info areas
        for i in range(9):
            if not self.reserved[8][i]:
                self.reserved[8][i] = True
            if not self.reserved[i][8]:
                self.reserved[i][8] = True
        for i in range(8):
            self.reserved[8][size - 1 - i] = True
            self.reserved[size - 1 - i][8] = True

    def _encode_data(self, data_bytes, data_cw_count, ec_cw_count):
        bits = []
        # Mode: Byte (0100)
        bits.extend([0, 1, 0, 0])
        # Count indicator (8 bits for Byte mode in Vers 1-9)
        length = len(data_bytes)
        for i in range(7, -1, -1):
            bits.append((length >> i) & 1)
        # Data bytes
        for b in data_bytes:
            for i in range(7, -1, -1):
                bits.append((b >> i) & 1)
        # Terminator: up to 4 zero bits
        bits.extend([0] * min(4, data_cw_count * 8 - len(bits)))
        # Pad to multiple of 8
        while len(bits) % 8 != 0:
            bits.append(0)
        # Convert to bytes
        data_cws = []
        for i in range(0, len(bits), 8):
            val = 0
            for bit in bits[i:i + 8]:
                val = (val << 1) | bit
            data_cws.append(val)
        # Pad with 0xEC, 0x11
        pad_bytes = [0xEC, 0x11]
        pad_idx = 0
        while len(data_cws) < data_cw_count:
            data_cws.append(pad_bytes[pad_idx])
            pad_idx ^= 1

        # Calculate Reed-Solomon error correction
        ec_cws = rs_encode(data_cws, ec_cw_count)
        return data_cws + ec_cws

    def _place_codewords(self, codewords):
        bits = []
        for cw in codewords:
            for i in range(7, -1, -1):
                bits.append((cw >> i) & 1)

        size = self.size
        bit_idx = 0
        col = size - 1
        up = True

        while col > 0:
            if col == 6:
                col -= 1  # Skip timing column
            for row_offset in range(size):
                row = (size - 1 - row_offset) if up else row_offset
                for c in (col, col - 1):
                    if not self.reserved[row][c]:
                        if bit_idx < len(bits):
                            self.matrix[row][c] = bits[bit_idx]
                            bit_idx += 1
                        else:
                            self.matrix[row][c] = 0
            up = not up
            col -= 2

    def _apply_best_mask(self, spec):
        # We test masks 0..7 and pick lowest penalty score
        best_mask = 0
        best_score = float('inf')
        size = self.size

        # Create copy of matrix without mask
        raw_matrix = [row[:] for row in self.matrix]

        for mask in range(8):
            # Apply mask to non-reserved
            for r in range(size):
                for c in range(size):
                    if not self.reserved[r][c]:
                        invert = False
                        if mask == 0: invert = (r + c) % 2 == 0
                        elif mask == 1: invert = r % 2 == 0
                        elif mask == 2: invert = c % 3 == 0
                        elif mask == 3: invert = (r + c) % 3 == 0
                        elif mask == 4: invert = ((r // 2) + (c // 3)) % 2 == 0
                        elif mask == 5: invert = ((r * c) % 2 + (r * c) % 3) == 0
                        elif mask == 6: invert = (((r * c) % 2) + ((r * c) % 3)) % 2 == 0
                        elif mask == 7: invert = (((r + c) % 2) + ((r * c) % 3)) % 2 == 0
                        self.matrix[r][c] = raw_matrix[r][c] ^ (1 if invert else 0)

            # Insert format bits
            self._write_format_info(mask)
            score = self._compute_penalty()
            if score < best_score:
                best_score = score
                best_mask = mask

        # Final application with best_mask
        for r in range(size):
            for c in range(size):
                if not self.reserved[r][c]:
                    invert = False
                    if best_mask == 0: invert = (r + c) % 2 == 0
                    elif best_mask == 1: invert = r % 2 == 0
                    elif best_mask == 2: invert = c % 3 == 0
                    elif best_mask == 3: invert = (r + c) % 3 == 0
                    elif best_mask == 4: invert = ((r // 2) + (c // 3)) % 2 == 0
                    elif best_mask == 5: invert = ((r * c) % 2 + (r * c) % 3) == 0
                    elif best_mask == 6: invert = (((r * c) % 2) + ((r * c) % 3)) % 2 == 0
                    elif best_mask == 7: invert = (((r + c) % 2) + ((r * c) % 3)) % 2 == 0
                    self.matrix[r][c] = raw_matrix[r][c] ^ (1 if invert else 0)
        self._write_format_info(best_mask)

    def _write_format_info(self, mask):
        size = self.size
        bits_val = FORMAT_INFO_L[mask]
        bits = [(bits_val >> (14 - i)) & 1 for i in range(15)]

        # Position 1: Around top-left finder
        seq1 = [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8),
                (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)]
        for (r, c), bit in zip(seq1, bits):
            self.matrix[r][c] = bit

        # Position 2: Bottom-left and Top-right
        seq2 = [(size - 1, 8), (size - 2, 8), (size - 3, 8), (size - 4, 8),
                (size - 5, 8), (size - 6, 8), (size - 7, 8)]
        seq3 = [(8, size - 8), (8, size - 7), (8, size - 6), (8, size - 5),
                (8, size - 4), (8, size - 3), (8, size - 2), (8, size - 1)]
        for (r, c), bit in zip(seq2 + seq3, bits):
            self.matrix[r][c] = bit

    def _compute_penalty(self):
        size = self.size
        penalty = 0
        # Rule 1: 5 or more same color in row/col
        for r in range(size):
            count, prev = 0, None
            for c in range(size):
                v = self.matrix[r][c]
                if v == prev:
                    count += 1
                else:
                    if count >= 5: penalty += 3 + (count - 5)
                    count = 1
                    prev = v
            if count >= 5: penalty += 3 + (count - 5)

        for c in range(size):
            count, prev = 0, None
            for r in range(size):
                v = self.matrix[r][c]
                if v == prev:
                    count += 1
                else:
                    if count >= 5: penalty += 3 + (count - 5)
                    count = 1
                    prev = v
            if count >= 5: penalty += 3 + (count - 5)

        # Rule 2: 2x2 blocks of same color
        for r in range(size - 1):
            for c in range(size - 1):
                v = self.matrix[r][c]
                if v == self.matrix[r][c+1] == self.matrix[r+1][c] == self.matrix[r+1][c+1]:
                    penalty += 3

        return penalty

    def to_svg(self, border=4, scale=8):
        """Returns clean SVG string of the QR Code."""
        total_dim = (self.size + border * 2) * scale
        rects = []
        for r in range(self.size):
            for c in range(self.size):
                if self.matrix[r][c] == 1:
                    x = (c + border) * scale
                    y = (r + border) * scale
                    rects.append(f'<rect x="{x}" y="{y}" width="{scale}" height="{scale}" fill="#000000"/>')
        
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_dim} {total_dim}" '
            f'width="{total_dim}" height="{total_dim}">\n'
            f'<rect width="100%" height="100%" fill="#FFFFFF"/>\n'
            + '\n'.join(rects) +
            '\n</svg>'
        )
        return svg

    def to_ascii(self, border=2):
        """Returns ASCII art representation using block characters."""
        lines = []
        pad = " " * (border * 2)
        lines.append(pad * (self.size + border * 2))
        for r in range(0, self.size, 2):
            line = [" " * border * 2]
            for c in range(self.size):
                top = self.matrix[r][c] == 1
                bot = (r + 1 < self.size) and (self.matrix[r + 1][c] == 1)
                if top and bot:
                    line.append("█")
                elif top and not bot:
                    line.append("▀")
                elif not top and bot:
                    line.append("▄")
                else:
                    line.append(" ")
            line.append(" " * border * 2)
            lines.append("".join(line))
        return "\n".join(lines)

def make_qr_svg(url):
    qr = QRCode(url)
    return qr.to_svg(border=3, scale=6)

def make_qr_ascii(url):
    qr = QRCode(url)
    return qr.to_ascii(border=1)

if __name__ == "__main__":
    test_url = "http://192.168.1.150:8080/"
    qr = QRCode(test_url)
    print(f"Generated QR Code for: {test_url} (Version {qr.version}, Size {qr.size}x{qr.size})")
    print(qr.to_ascii())
    svg = qr.to_svg()
    print(f"SVG generated successfully ({len(svg)} chars)")
