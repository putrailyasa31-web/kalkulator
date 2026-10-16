"""
Kalkulator Python dengan riwayat hitung
- Mendukung + - * / // % ** ^ dan tanda kurung
- Fungsi: sqrt, sin, cos, tan (dalam derajat), log, ln, abs, round, fak
- Konstanta: pi, e, ans (hasil terakhir)
- Riwayat otomatis tersimpan di riwayat.json
Cara pakai: python kalkulator.py
"""
import ast
import json
import math
import operator
import os

FILE_RIWAYAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "riwayat.json")

OPERATOR = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

FUNGSI = {
    "sqrt": math.sqrt,
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "log": math.log10,
    "ln": math.log,
    "abs": abs,
    "round": round,
    "fak": math.factorial,
}
KONSTANTA = {"pi": math.pi, "e": math.e}


# ---------- Penghitung aman (tanpa eval) ----------
def hitung_node(node, ans):
    if isinstance(node, ast.Expression):
        return hitung_node(node.body, ans)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATOR:
        kiri = hitung_node(node.left, ans)
        kanan = hitung_node(node.right, ans)
        if isinstance(node.op, ast.Pow) and abs(kanan) > 1000:
            raise ValueError("Pangkat terlalu besar")
        return OPERATOR[type(node.op)](kiri, kanan)
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
        return UNARY[type(node.op)](hitung_node(node.operand, ans))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNGSI:
        argumen = [hitung_node(a, ans) for a in node.args]
        return FUNGSI[node.func.id](*argumen)
    if isinstance(node, ast.Name):
        if node.id == "ans":
            return ans
        if node.id in KONSTANTA:
            return KONSTANTA[node.id]
    raise ValueError("Ekspresi tidak dikenali")


def hitung(teks, ans=0):
    teks = teks.replace("^", "**").replace("×", "*").replace("÷", "/").replace(",", ".")
    pohon = ast.parse(teks, mode="eval")
    return hitung_node(pohon, ans)


def format_hasil(x):
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    if isinstance(x, float):
        return format(x, ".10g")
    return str(x)


# ---------- Riwayat ----------
def muat_riwayat():
    try:
        with open(FILE_RIWAYAT, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def simpan_riwayat(data):
    try:
        with open(FILE_RIWAYAT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        print("(Peringatan: riwayat tidak bisa disimpan)")


def tampilkan_riwayat(data):
    if not data:
        print("Riwayat masih kosong.")
        return
    print("\n--- Riwayat (10 terakhir) ---")
    for i, item in enumerate(data[-10:], 1):
        print(f"{i:>2}. {item['ekspresi']} = {item['hasil']}")
    print()


BANTUAN = """
Contoh:  12 + 5 * 3      (2 + 3) ^ 4      sqrt(144)      sin(30)
         ans * 2         fak(5)           pi * 7 ^ 2
Perintah:  riwayat  -> lihat riwayat
           hapus    -> hapus riwayat
           bantuan  -> tampilkan bantuan ini
           keluar   -> tutup program
"""


def main():
    riwayat = muat_riwayat()
    ans = 0
    print("=" * 40)
    print("   KALKULATOR PYTHON")
    print("   ketik 'bantuan' untuk panduan")
    print("=" * 40)

    while True:
        try:
            teks = input("hitung > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa!")
            break

        if not teks:
            continue
        perintah = teks.lower()
        if perintah in ("keluar", "exit", "q"):
            print("Sampai jumpa!")
            break
        if perintah == "bantuan":
            print(BANTUAN)
            continue
        if perintah == "riwayat":
            tampilkan_riwayat(riwayat)
            continue
        if perintah == "hapus":
            riwayat = []
            simpan_riwayat(riwayat)
            print("Riwayat dihapus.")
            continue

        try:
            hasil = hitung(teks, ans)
        except ZeroDivisionError:
            print("Error: tidak bisa dibagi nol")
            continue
        except (ValueError, SyntaxError, TypeError, OverflowError):
            print("Error: ekspresi tidak valid, ketik 'bantuan'")
            continue

        ans = hasil
        teks_hasil = format_hasil(hasil)
        print(f"= {teks_hasil}")
        riwayat.append({"ekspresi": teks, "hasil": teks_hasil})
        simpan_riwayat(riwayat)


if __name__ == "__main__":
    main()
