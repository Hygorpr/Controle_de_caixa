import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
from datetime import datetime
import csv

# Banco de dados
conn = sqlite3.connect('Histórico.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS saidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL
    )
''')
conn.commit()

def salvar_saida():
    nome = nome_entry.get()
    quantidade = quantidade_entry.get()
    valor = valor_entry.get()
    data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if nome and quantidade and valor:
        try:
            cursor.execute('''
                INSERT INTO saidas (nome, quantidade, valor, data)
                VALUES (?, ?, ?, ?)
            ''', (nome, int(quantidade), float(valor), data))
            conn.commit()
            messagebox.showinfo('Sucesso', 'Saída registrada com sucesso!')
            nome_entry.delete(0, tk.END)
            quantidade_entry.delete(0, tk.END)
            valor_entry.delete(0, tk.END)
            atualizar_historico()
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao registrar: {e}')
    else:
        messagebox.showwarning('Atenção', 'Preencha todos os campos!')

def atualizar_historico():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT id, nome, quantidade, valor, data FROM saidas ORDER BY data DESC")
    for r in cursor.fetchall():
        # Insere o item com iid = id (interno) e mostra só as colunas sem o ID
        tree.insert('', tk.END, iid=str(r[0]), values=(r[1], r[2], f"R$ {r[3]:.2f}", r[4]))

def exportar_csv():
    cursor.execute("SELECT id, nome, quantidade, valor, data FROM saidas ORDER BY data DESC")
    registros = cursor.fetchall()
    if not registros:
        messagebox.showwarning("Aviso", "Nenhum dado para exportar.")
        return

    caminho = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Salvar arquivo CSV"
    )
    if caminho:
        try:
            with open(caminho, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Produto", "Quantidade", "Valor", "Data"])
                writer.writerows(registros)
            messagebox.showinfo("Sucesso", f"Arquivo exportado para:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar CSV:\n{e}")

def mostrar_total():
    cursor.execute("SELECT SUM(valor * quantidade) FROM saidas")
    total = cursor.fetchone()[0]
    total = total if total else 0
    messagebox.showinfo("Total de Vendas", f"Total vendido até agora: R$ {total:.2f}")

def remover_saida():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Atenção", "Selecione um item para remover.")
        return
    id_saida = int(selected[0])  # iid é o id no banco
    resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja remover a saída selecionada?")
    if resposta:
        try:
            cursor.execute("DELETE FROM saidas WHERE id = ?", (id_saida,))
            conn.commit()
            atualizar_historico()
            messagebox.showinfo("Sucesso", "Saída removida com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover saída: {e}")

app = tk.Tk()
app.title('Controle de Saída - Loja de Aquarismo')
app.geometry("800x450")

# Entrada de dados
frame_entrada = tk.Frame(app)
frame_entrada.pack(padx=10, pady=10, fill='x')

tk.Label(frame_entrada, text='Nome do Produto ou Peixe').grid(row=0, column=0, sticky='w')
nome_entry = tk.Entry(frame_entrada)
nome_entry.grid(row=1, column=0, sticky='we', padx=5)

tk.Label(frame_entrada, text='Quantidade').grid(row=0, column=1, sticky='w')
quantidade_entry = tk.Entry(frame_entrada)
quantidade_entry.grid(row=1, column=1, sticky='we', padx=5)

tk.Label(frame_entrada, text='Valor da Venda (R$)').grid(row=0, column=2, sticky='w')
valor_entry = tk.Entry(frame_entrada)
valor_entry.grid(row=1, column=2, sticky='we', padx=5)

btn_salvar = tk.Button(frame_entrada, text='Registrar Saída', command=salvar_saida)
btn_salvar.grid(row=1, column=3, padx=10)

for i in range(4):
    frame_entrada.columnconfigure(i, weight=1)

# Frame histórico e botões adicionais
frame_historico = tk.Frame(app)
frame_historico.pack(padx=10, pady=10, fill='both', expand=True)

# Treeview para histórico sem coluna ID visível
cols = ("Produto", "Quantidade", "Valor", "Data")
tree = ttk.Treeview(frame_historico, columns=cols, show='headings')
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, anchor='center')
tree.pack(side='left', fill='both', expand=True)

scrollbar = ttk.Scrollbar(frame_historico, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')

# Frame dos botões extras
frame_botoes = tk.Frame(app)
frame_botoes.pack(padx=10, pady=5, fill='x')

btn_exportar = tk.Button(frame_botoes, text='Exportar para CSV', command=exportar_csv)
btn_exportar.pack(side='left', padx=5)

btn_total = tk.Button(frame_botoes, text='Mostrar Total de Vendas', command=mostrar_total)
btn_total.pack(side='left', padx=5)

btn_remover = tk.Button(frame_botoes, text="Remover saída selecionada", command=remover_saida)
btn_remover.pack(side='left', padx=5)

# Inicializa o histórico
atualizar_historico()

app.mainloop()
conn.close()
