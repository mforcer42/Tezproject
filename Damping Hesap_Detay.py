import tkinter as tk
from tkinter import ttk
import numpy as np

# Girilen değeri float'a çeviren yardımcı fonksiyon
def convert_to_float(value):
    try:
        value = value.strip()
        value = value.replace(',', '.')
        return float(value)
    except ValueError:
        return None

# Mevcut tabloyu temizleyen fonksiyon
def clear_table():
    for widget in root.grid_slaves():
        if int(widget.grid_info()["row"]) > 2:
            widget.grid_forget()

# Hesaplamaları yapan ana fonksiyon
def calculate_table():
    try:
        # Kullanıcı girdilerini al ve doğrula
        kat_sayisi = int(entry_kat.get())
        damper_sonum_orani_str = entry_damper_sonum.get().strip()
        
        if not damper_sonum_orani_str:
            raise ValueError("Damper sönüm oranı boş bırakılamaz.")
        
        damper_sonum_orani = convert_to_float(damper_sonum_orani_str)
        if damper_sonum_orani is None:
            raise ValueError("Damper sönüm oranı geçerli bir sayı değil.")
        
        if damper_sonum_orani <= 0:
            raise ValueError("Damper sönüm oranı pozitif bir sayı olmalıdır.")

        # Diğer girdi değerlerini al ve doğrula
        cos_theta_values = [convert_to_float(entry.get()) for entry in entries_cos_theta]
        mi_values = [convert_to_float(entry.get()) for entry in entries_mi]
        T_values = [convert_to_float(entry.get()) for entry in entries_T]
        Ui_values = [convert_to_float(entry.get()) for entry in entries_Ui]

        if any(val is None for val in cos_theta_values + mi_values + T_values + Ui_values):
            raise ValueError("Girdilerden biri geçerli bir sayı değil.")

        # Hesaplamaları yap
        max_ui = max(Ui_values)
        total_mi_q_i_sq = 0
        total_ara_carpim = 0
        q_i_values = [Ui / max_ui for Ui in Ui_values]

        for i in range(kat_sayisi):
            cos_theta = cos_theta_values[i]
            cos_theta_sq = cos_theta ** 2
            q_i = q_i_values[i]
            mi_q_i_sq = mi_values[i] * q_i ** 2
            
            # θrl hesaplama
            if i == 0:  # En üst kat için
                theta_rl = q_i_values[i] - q_i_values[i+1]
            elif i == kat_sayisi - 1:  # En alt kat için
                theta_rl = q_i_values[i]
            else:
                theta_rl = q_i_values[i] - q_i_values[i+1]
            
            theta_rl_sq = theta_rl ** 2
            ara_carpim = cos_theta_sq * T_values[i] * theta_rl_sq

            # Hesaplanan değerleri GUI'de göster
            label_cos_theta[i].config(text=f"{cos_theta:.4f}", foreground="blue")
            label_cos_theta_sq[i].config(text=f"{cos_theta_sq:.4f}", foreground="blue")
            label_q_i[i].config(text=f"{q_i:.4f}", foreground="blue")
            label_mi_q_i_sq[i].config(text=f"{mi_q_i_sq:.4f}", foreground="blue")
            label_theta_rl[i].config(text=f"{theta_rl:.4f}", foreground="blue")
            label_theta_rl_sq[i].config(text=f"{theta_rl_sq:.4f}", foreground="blue")
            label_ara_carpim[i].config(text=f"{ara_carpim:.4f}", foreground="blue")

            total_mi_q_i_sq += mi_q_i_sq
            total_ara_carpim += ara_carpim

        # Toplam Cj hesapla ve göster
        Cj = damper_sonum_orani * 4 * np.pi * total_mi_q_i_sq / total_ara_carpim
        label_cj.config(text=f"TOPLAM Cj: {Cj:.4f}", foreground="red")
        global total_Cj
        total_Cj = Cj

    except (ValueError, IndexError) as e:
        error_message = str(e)
        print("Hata:", error_message)
        label_cj.config(text=f"HATA: {error_message}", foreground="red")

# Sönümleyici değerlerini dağıtan fonksiyon
def distribute_dampers():
    try:
        kat_sayisi = int(entry_kat.get())
        Vx_values = [convert_to_float(entry.get()) for entry in entries_Vx]
        n_values = [convert_to_float(entry.get()) for entry in entries_n]

        if any(val is None for val in Vx_values + n_values):
            raise ValueError("V veya n değerlerinden biri geçerli bir sayı değil.")

        total_Vx = sum(Vx_values)

        # Her kat için dağıtılmış değeri hesapla ve göster
        for i in range(kat_sayisi):
            distributed_value = total_Cj * Vx_values[i] / (total_Vx * n_values[i])
            label_distributed[i].config(text=f"{distributed_value:.4f}", foreground="green")

    except (ValueError, IndexError, AttributeError) as e:
        error_message = str(e)
        print("Hata:", error_message)
        label_cj.config(text=f"HATA: {error_message}", foreground="red")

# Tabloyu oluşturan fonksiyon
def create_table():
    clear_table()
    kat_sayisi = int(entry_kat.get())
    
    global entries_cos_theta, entries_mi, entries_T, entries_Ui, entries_Vx, entries_n
    global label_cos_theta, label_cos_theta_sq, label_q_i, label_mi_q_i_sq, label_theta_rl, label_theta_rl_sq, label_ara_carpim, label_distributed
    
    # Giriş alanları ve etiketler için boş listeler oluştur
    entries_cos_theta = []
    entries_mi = []
    entries_T = []
    entries_Ui = []
    entries_Vx = []
    entries_n = []
    label_cos_theta = []
    label_cos_theta_sq = []
    label_q_i = []
    label_mi_q_i_sq = []
    label_theta_rl = []
    label_theta_rl_sq = []
    label_ara_carpim = []
    label_distributed = []

    # Her kat için giriş alanları ve etiketler oluştur
    for i in range(kat_sayisi):
        row = 3 + i
        ttk.Label(root, text=str(kat_sayisi - i), font=("Arial", 10, "bold")).grid(row=row, column=0, padx=5, pady=5)
        
        # cos θ giriş alanı
        entry_cos_theta = ttk.Entry(root, width=10)
        entry_cos_theta.grid(row=row, column=1, padx=5, pady=5)
        entries_cos_theta.append(entry_cos_theta)
        
        # cos θ sonuç etiketi
        label_cos_theta_value = tk.Label(root, text="", width=10)
        label_cos_theta_value.grid(row=row, column=2, padx=5, pady=5)
        label_cos_theta.append(label_cos_theta_value)
        
        # cos² θ sonuç etiketi
        label_cos_theta_sq_value = tk.Label(root, text="", width=10)
        label_cos_theta_sq_value.grid(row=row, column=3, padx=5, pady=5)
        label_cos_theta_sq.append(label_cos_theta_sq_value)
        
        # mi giriş alanı
        entry_mi_value = ttk.Entry(root, width=10)
        entry_mi_value.grid(row=row, column=4, padx=5, pady=5)
        entries_mi.append(entry_mi_value)
        
        # T giriş alanı
        entry_T_value = ttk.Entry(root, width=10)
        entry_T_value.grid(row=row, column=5, padx=5, pady=5)
        entries_T.append(entry_T_value)
        
        # Ui giriş alanı
        entry_Ui_value = ttk.Entry(root, width=10)
        entry_Ui_value.grid(row=row, column=6, padx=5, pady=5)
        entries_Ui.append(entry_Ui_value)
        
        # qi sonuç etiketi
        label_q_i_value = tk.Label(root, text="", width=10)
        label_q_i_value.grid(row=row, column=7, padx=5, pady=5)
        label_q_i.append(label_q_i_value)
        
        # mi*qi² sonuç etiketi
        label_mi_q_i_sq_value = tk.Label(root, text="", width=10)
        label_mi_q_i_sq_value.grid(row=row, column=8, padx=5, pady=5)
        label_mi_q_i_sq.append(label_mi_q_i_sq_value)
        
        # θrl sonuç etiketi
        label_theta_rl_value = tk.Label(root, text="", width=10)
        label_theta_rl_value.grid(row=row, column=9, padx=5, pady=5)
        label_theta_rl.append(label_theta_rl_value)
        
        # θrl² sonuç etiketi
        label_theta_rl_sq_value = tk.Label(root, text="", width=10)
        label_theta_rl_sq_value.grid(row=row, column=10, padx=5, pady=5)
        label_theta_rl_sq.append(label_theta_rl_sq_value)
        
        # Ara çarpım sonuç etiketi
        label_ara_carpim_value = tk.Label(root, text="", width=10)
        label_ara_carpim_value.grid(row=row, column=11, padx=5, pady=5)
        label_ara_carpim.append(label_ara_carpim_value)

        # Vx giriş alanı
        entry_Vx_value = ttk.Entry(root, width=10)
        entry_Vx_value.grid(row=row, column=12, padx=5, pady=5)
        entries_Vx.append(entry_Vx_value)

        # n giriş alanı
        entry_n_value = ttk.Entry(root, width=10)
        entry_n_value.grid(row=row, column=13, padx=5, pady=5)
        entries_n.append(entry_n_value)

        # Dağıtılmış Cj sonuç etiketi
        label_distributed_value = tk.Label(root, text="", width=10)
        label_distributed_value.grid(row=row, column=14, padx=5, pady=5)
        label_distributed.append(label_distributed_value)

# Panoya kopyalanan değerleri ilgili sütuna yapıştıran fonksiyon
def paste_column(column_index):
    clipboard = root.clipboard_get()
    values = clipboard.split()
    for i, value in enumerate(values):
        if i < len(entries_cos_theta):
            if column_index == 1:
                entries_cos_theta[i].delete(0, tk.END)
                entries_cos_theta[i].insert(0, value)
            elif column_index == 4:
                entries_mi[i].delete(0, tk.END)
                entries_mi[i].insert(0, value)
            elif column_index == 5:
                entries_T[i].delete(0, tk.END)
                entries_T[i].insert(0, value)
            elif column_index == 6:
                entries_Ui[i].delete(0, tk.END)
                entries_Ui[i].insert(0, value)
            elif column_index == 12:
                entries_Vx[i].delete(0, tk.END)
                entries_Vx[i].insert(0, value)
            elif column_index == 13:
                entries_n[i].delete(0, tk.END)
                entries_n[i].insert(0, value)

# Ana pencereyi oluştur
root = tk.Tk()
root.title("DAMPING COEFFICIENT CALCULATOR by Mustafa ÇALI")

# Kat sayısı giriş alanı
ttk.Label(root, text="KAT SAYISI:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
entry_kat = ttk.Entry(root, width=10)
entry_kat.grid(row=0, column=1, padx=10, pady=10)

# Damper sönüm oranı giriş alanı
ttk.Label(root, text="SÖNÜM ORANI:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, pady=10)
entry_damper_sonum = ttk.Entry(root, width=10)
entry_damper_sonum.grid(row=0, column=3, padx=10, pady=10)

# Tablo başlıkları
headers = ["KAT NO", "cos θ", "cos θ", "cos² θ", "mi (kn.s²/m)", "T (sn)", "Ui (m)", "θİ", "mi.θİ²", "θrl", "θrl²", "T.Σj⋅θrl²⋅(cos)²⁡(θj)", "V", "n", "DAĞITILMIŞ Cj"]
for i, header in enumerate(headers):
    ttk.Label(root, text=header, font=("Arial", 10, "bold")).grid(row=1, column=i, padx=5, pady=5)

# Yapıştırma butonları
for i in [1, 4, 5, 6, 12, 13]:
    paste_button = ttk.Button(root, text="📋", width=2, command=lambda col=i: paste_column(col))
    paste_button.grid(row=2, column=i, padx=5, pady=5, sticky='n')

# Tabloyu oluştur butonu
create_table_button = ttk.Button(root, text="TABLOYU OLUŞTUR", command=create_table)
create_table_button.grid(row=0, column=4, padx=10, pady=10)

# Hesapla butonu
calculate_button = ttk.Button(root, text="HESAPLA", command=calculate_table)
calculate_button.grid(row=0, column=5, padx=10, pady=10)

# Sönümleyici değeri dağıt butonu
distribute_button = ttk.Button(root, text="SÖNÜMLEYİCİ DEĞERİ DAĞIT", command=distribute_dampers)
distribute_button.grid(row=0, column=6, padx=10, pady=10)

# Toplam Cj etiketi
label_cj = tk.Label(root, text="TOPLAM Cj: ", foreground="red", font=("Arial", 12, "bold"))
label_cj.grid(row=0, column=7, padx=10, pady=10)

# Toplam Cj değişkeni
total_Cj = 0

# Ana döngüyü başlat
root.mainloop()
