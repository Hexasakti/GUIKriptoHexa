import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import os

# Fungsi untuk membaca file Excel
def import_sbox():
    filepath = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if filepath:
        try:
            df = pd.read_excel(filepath, header=None)
            sbox = df.values.flatten()
            if len(sbox) != 256:
                raise ValueError("S-Box harus memiliki panjang 256 elemen.")
            update_sbox_display(sbox)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengimpor S-Box: {e}")

def export_results():
    filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    if filepath:
        try:
            results_df.to_excel(filepath, index=False, header=True)
            messagebox.showinfo("Export Berhasil", f"Hasil telah diekspor ke {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor hasil: {e}")

def calculate_sac(sbox):
    n = len(sbox)
    bit_size = int(np.log2(n))
    sac_total = 0
    for i in range(n):
        for bit in range(bit_size):
            flipped_input = i ^ (1 << bit)
            output_diff = sbox[i] ^ sbox[flipped_input]
            sac_total += bin(output_diff).count('1') / bit_size
    return sac_total / (n * bit_size)

def calculate_lap(sbox):
    n = len(sbox)
    max_prob = 0
    for input_mask in range(1, 256):
        for output_mask in range(1, 256):
            count = 0
            for x in range(n):
                input_parity = bin(x & input_mask).count('1') % 2
                output_parity = bin(sbox[x] & output_mask).count('1') % 2
                if input_parity == output_parity:
                    count += 1
            prob = abs(count - n / 2) / n
            max_prob = max(max_prob, prob)
    return max_prob

def calculate_dap(sbox):
    n = len(sbox)
    max_prob = 0
    for input_diff in range(1, 256):
        for output_diff in range(256):
            count = 0
            for x in range(n):
                if x ^ input_diff < n and sbox[x] ^ sbox[x ^ input_diff] == output_diff:
                    count += 1
            prob = count / n
            max_prob = max(max_prob, prob)
    return max_prob

def binary_representation(num, bits=8):
    return np.array([int(b) for b in format(num, f'0{bits}b')])

def optimized_walsh_hadamard(sbox, n=8, m=8):
    inputs = np.array([binary_representation(x, n) for x in range(2**n)])
    outputs = np.array([binary_representation(sbox[x], m) for x in range(2**n)])
    max_walsh = 0
    for u in range(1, 2**n):
        u_bin = binary_representation(u, n)
        for v in range(1, 2**m):
            v_bin = binary_representation(v, m)
            dot_u_x = (inputs @ u_bin) % 2
            dot_v_Sx = (outputs @ v_bin) % 2
            dot_result = (dot_u_x ^ dot_v_Sx)
            walsh_sum = np.sum(1 - 2 * dot_result)
            max_walsh = max(max_walsh, abs(walsh_sum))
    return 2**(n-1) - max_walsh / 2

def perform_calculation():
    global results_df
    try:
        if len(current_sbox) != 256:
            raise ValueError("S-Box belum dimuat atau tidak valid.")

        operation = operation_var.get()
        if operation == "NL":
            result = optimized_walsh_hadamard(current_sbox)
        elif operation == "SAC":
            result = calculate_sac(current_sbox)
        elif operation == "LAP":
            result = calculate_lap(current_sbox)
        elif operation == "DAP":
            result = calculate_dap(current_sbox)
        else:
            raise ValueError("Operasi tidak dikenali.")

        results_df = pd.DataFrame({"Operation": [operation], "Result": [result]})
        update_result_display(results_df)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal melakukan perhitungan: {e}")

def update_sbox_display(sbox):
    global current_sbox
    current_sbox = sbox
    sbox_display.delete("1.0", tk.END)
    sbox_display.insert(tk.END, " ".join(map(str, sbox)))

def update_result_display(results_df):
    result_display.delete("1.0", tk.END)
    result_display.insert(tk.END, results_df.to_string(index=False))

# GUI Setup
root = tk.Tk()
root.title("S-Box Analysis Tool")
root.geometry("600x500")

current_sbox = []
results_df = pd.DataFrame()

# Frame Import
import_frame = tk.Frame(root)
import_frame.pack(pady=10)
import_button = tk.Button(import_frame, text="Import S-Box", command=import_sbox)
import_button.pack()

# Display S-Box
sbox_display = tk.Text(root, height=10, width=50)
sbox_display.pack(pady=10)
sbox_display.insert(tk.END, "S-Box belum dimuat.")

# Operation Selection
operation_var = tk.StringVar(value="NL")
operation_frame = tk.Frame(root)
operation_frame.pack(pady=10)
operations = ["NL", "SAC", "LAP", "DAP"]
for op in operations:
    tk.Radiobutton(operation_frame, text=op, variable=operation_var, value=op).pack(side=tk.LEFT)

# Perform Calculation
calculate_button = tk.Button(root, text="Hitung", command=perform_calculation)
calculate_button.pack(pady=10)

# Display Result
result_display = tk.Text(root, height=10, width=50)
result_display.pack(pady=10)
result_display.insert(tk.END, "Hasil perhitungan akan ditampilkan di sini.")

# Export Results
export_button = tk.Button(root, text="Export Hasil", command=export_results)
export_button.pack(pady=10)

root.mainloop()
