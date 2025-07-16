import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
from datetime import datetime
import csv

# Banco de dados
conn = sqlite3.connect('Historico.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS saidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        dia TEXT NOT NULL
    )
''')
conn.commit()

def salvar_saida():
    nome = nome_entry.get()
    quantidade = quantidade_entry.get()
    valor = valor_entry.get()
    data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dia = datetime.now().strftime('%Y-%m-%d')

    if nome and quantidade and valor:
        try:
            cursor.execute('''
                INSERT INTO saidas (nome, quantidade, valor, data, dia)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, int(quantidade), float(valor), data, dia))
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

    nome_filtro = filtro_nome_entry.get().strip().lower()
    data_ini = filtro_data_ini.get()
    data_fim = filtro_data_fim.get()

    query = "SELECT id, nome, quantidade, valor, data FROM saidas WHERE 1=1"
    params = []

    if nome_filtro:
        query += " AND LOWER(nome) LIKE ?"
        params.append(f"%{nome_filtro}%")

    if data_ini:
        query += " AND dia >= ?"
        params.append(data_ini)

    if data_fim:
        query += " AND dia <= ?"
        params.append(data_fim)

    query += " ORDER BY data DESC"

    cursor.execute(query, tuple(params))
    for r in cursor.fetchall():
        tree.insert('', tk.END, iid=str(r[0]), values=(r[1], r[2], f"R$ {r[3]:.2f}", r[4]))

def exportar_csv():
    registros = tree.get_children()
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
                writer.writerow(["Produto", "Quantidade", "Valor", "Data"])
                for item_id in registros:
                    writer.writerow(tree.item(item_id)['values'])
            messagebox.showinfo("Sucesso", f"Arquivo exportado para:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar CSV:\n{e}")

def mostrar_total():
    total = 0
    for item in tree.get_children():
        valor = tree.item(item)['values'][2]  # 'R$ xx,xx'
        valor_float = float(str(valor).replace('R$', '').replace(',', '').strip())
        qtd = int(tree.item(item)['values'][1])
        total += valor_float * qtd
    messagebox.showinfo("Total de Vendas Filtradas", f"Total: R$ {total:.2f}")

def remover_saida():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Atenção", "Selecione um ou mais itens para remover.")
        return

    quantidade_itens = len(selected)
    resposta = messagebox.askyesno("Confirmar Remoção", f"Deseja remover {quantidade_itens} item(ns) selecionado(s)?")
    if resposta:
        try:
            for item in selected:
                id_saida = int(item)
                cursor.execute("DELETE FROM saidas WHERE id = ?", (id_saida,))
            conn.commit()
            atualizar_historico()
            messagebox.showinfo("Sucesso", f"{quantidade_itens} item(ns) removido(s) com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover saída(s): {e}")

def ordenar_coluna(col):
    dados = [(tree.set(k, col), k) for k in tree.get_children('')]
    try:
        dados.sort(key=lambda t: float(t[0].replace('R$', '').replace(',', '')))
    except:
        dados.sort()
    for index, (val, k) in enumerate(dados):
        tree.move(k, '', index)

def fechar_caixa():
    hoje = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT nome, quantidade, valor, data FROM saidas WHERE dia = ?", (hoje,))
    registros = cursor.fetchall()
    if not registros:
        messagebox.showinfo("Fechamento de Caixa", "Nenhuma venda registrada hoje.")
        return

    total = sum(q * v for _, q, v, _ in registros)
    caminho = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")],
        title="Salvar fechamento do dia"
    )
    if caminho:
        try:
            with open(caminho, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Produto", "Quantidade", "Valor", "Data"])
                for r in registros:
                    writer.writerow(r)
                writer.writerow([])
                writer.writerow(["TOTAL DO DIA", "", f"R$ {total:.2f}", hoje])
            messagebox.showinfo("Fechamento Concluído", f"Arquivo salvo e total do dia foi R$ {total:.2f}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar fechamento: {e}")

app = tk.Tk()
app.title('Controle de Saída - Loja de Aquarismo')
app.geometry("950x580")

# Entrada de dados
frame_entrada = tk.Frame(app)
frame_entrada.pack(padx=10, pady=10, fill='x')

tk.Label(frame_entrada, text='Produto ou Peixe').grid(row=0, column=0)
nome_entry = tk.Entry(frame_entrada)
nome_entry.grid(row=1, column=0, padx=5)

tk.Label(frame_entrada, text='Quantidade').grid(row=0, column=1)
quantidade_entry = tk.Entry(frame_entrada)
quantidade_entry.grid(row=1, column=1, padx=5)

tk.Label(frame_entrada, text='Valor (R$)').grid(row=0, column=2)
valor_entry = tk.Entry(frame_entrada)
valor_entry.grid(row=1, column=2, padx=5)

btn_salvar = tk.Button(frame_entrada, text='Registrar Saída', command=salvar_saida)
btn_salvar.grid(row=1, column=3, padx=10)

# Filtros
frame_filtro = tk.Frame(app)
frame_filtro.pack(padx=10, pady=5, fill='x')

filtro_nome_entry = tk.Entry(frame_filtro, width=20)
filtro_nome_entry.pack(side='left', padx=5)
filtro_nome_entry.insert(0, '')
tk.Label(frame_filtro, text='Nome (opcional)').pack(side='left')

filtro_data_ini = tk.Entry(frame_filtro, width=12)
filtro_data_ini.pack(side='left', padx=5)
tk.Label(frame_filtro, text='Data Início').pack(side='left')

filtro_data_fim = tk.Entry(frame_filtro, width=12)
filtro_data_fim.pack(side='left', padx=5)
tk.Label(frame_filtro, text='Data Fim').pack(side='left')

btn_filtrar = tk.Button(frame_filtro, text='Filtrar', command=atualizar_historico)
btn_filtrar.pack(side='left', padx=10)

# Tabela
frame_historico = tk.Frame(app)
frame_historico.pack(padx=10, pady=10, fill='both', expand=True)

cols = ("Produto", "Quantidade", "Valor", "Data")
tree = ttk.Treeview(frame_historico, columns=cols, show='headings', selectmode='extended')
for col in cols:
    tree.heading(col, text=col, command=lambda _col=col: ordenar_coluna(_col))
    tree.column(col, anchor='center')
tree.pack(side='left', fill='both', expand=True)

scrollbar = ttk.Scrollbar(frame_historico, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side='right', fill='y')

# Botões
frame_botoes = tk.Frame(app)
frame_botoes.pack(padx=10, pady=5, fill='x')

btn_exportar = tk.Button(frame_botoes, text='Exportar CSV', command=exportar_csv)
btn_exportar.pack(side='left', padx=5)

btn_total = tk.Button(frame_botoes, text='Total Vendas (Filtrado)', command=mostrar_total)
btn_total.pack(side='left', padx=5)

btn_remover = tk.Button(frame_botoes, text="Remover Selecionado(s)", command=remover_saida)
btn_remover.pack(side='left', padx=5)

btn_fechar_caixa = tk.Button(frame_botoes, text="Fechar Caixa (Hoje)", command=fechar_caixa)
btn_fechar_caixa.pack(side='left', padx=5)

atualizar_historico()
app.mainloop()
conn.close()