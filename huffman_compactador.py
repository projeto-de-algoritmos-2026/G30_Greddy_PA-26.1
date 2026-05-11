import os
import heapq
import pickle
import tkinter as tk
from tkinter import ttk
from collections import Counter
import math
import time
from tkinter import messagebox, filedialog

class No:
    #Nó da árvore binária de Huffman.
    def __init__(self, char, freq):
        self.char = char      
        self.freq = freq      
        self.esq  = None     
        self.dir  = None      

    def __lt__(self, outro):
        return self.freq < outro.freq


def construir_arvore(texto: str) -> tuple[No, dict]:
    #Constrói a árvore de Huffman via algoritmo guloso

    frequencias = Counter(texto)
    heap = [No(c, f) for c, f in frequencias.items()]
    heapq.heapify(heap)

    # Caso especial: texto com apenas 1 caractere único
    if len(heap) == 1:
        unico = heapq.heappop(heap)
        raiz = No(None, unico.freq)
        raiz.esq = unico
        heapq.heappush(heap, raiz)

    while len(heap) > 1:
        menor1 = heapq.heappop(heap)   
        menor2 = heapq.heappop(heap)   
        pai = No(None, menor1.freq + menor2.freq)
        pai.esq = menor1
        pai.dir = menor2
        heapq.heappush(heap, pai)

    return heap[0], frequencias


def gerar_codigos(raiz: No, prefixo: str = "", tabela: dict = None) -> dict:
    #Percorre a árvore e atribui código binário a cada folha.
    if tabela is None:
        tabela = {}
    if raiz is None:
        return tabela
    if raiz.char is not None:
        tabela[raiz.char] = prefixo or "0"
        return tabela
    gerar_codigos(raiz.esq, prefixo + "0", tabela)
    gerar_codigos(raiz.dir, prefixo + "1", tabela)
    return tabela

def codificar(texto: str, tabela: dict) -> str:
    #Converte texto em string de bits usando a tabela de Huffman
    return "".join(tabela[c] for c in texto)


def bits_para_bytes(bits: str) -> bytes:
    # Converte string de bits em bytes.
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding
    resultado = bytearray()
    resultado.append(padding)          
    for i in range(0, len(bits), 8):
        resultado.append(int(bits[i:i+8], 2))
    return bytes(resultado)


def bytes_para_bits(dados: bytes) -> str:
    # Reverte bytes para string de bits
    padding = dados[0]
    bits = "".join(f"{b:08b}" for b in dados[1:])
    if padding:
        bits = bits[:-padding]
    return bits


def decodificar(bits: str, raiz: No) -> str:
    #Percorre a árvore seguindo os bits para recuperar o texto original
    resultado = []
    no_atual = raiz
    for bit in bits:
        no_atual = no_atual.esq if bit == "0" else no_atual.dir
        if no_atual.char is not None:
            resultado.append(no_atual.char)
            no_atual = raiz
    return "".join(resultado)


def compactar_arquivo(caminho_entrada: str, caminho_saida: str) -> dict:
   #Lê um .txt, aplica Huffman e salva como .huff. Retorna dicionário com estatísticas da operação.
  
    t_inicio = time.time()

    with open(caminho_entrada, "r", encoding="utf-8") as f:
        texto = f.read()

    if not texto:
        raise ValueError("O arquivo está vazio.")

    raiz, frequencias = construir_arvore(texto)
    tabela = gerar_codigos(raiz)
    bits = codificar(texto, tabela)
    dados_comprimidos = bits_para_bytes(bits)

    # Salva: (árvore serializada, dados comprimidos)
    pacote = {
        "arvore": raiz,
        "dados": dados_comprimidos,
        "nome_original": os.path.basename(caminho_entrada),
        "tamanho_original": len(texto),
    }
    with open(caminho_saida, "wb") as f:
        pickle.dump(pacote, f)

    t_fim = time.time()
    tamanho_orig  = os.path.getsize(caminho_entrada)
    tamanho_comp  = os.path.getsize(caminho_saida)
    taxa = (1 - tamanho_comp / tamanho_orig) * 100

    # Entropia de Shannon
    n = len(texto)
    entropia = -sum(
        (freq / n) * math.log2(freq / n)
        for freq in frequencias.values()
    )

    # Comprimento médio dos códigos Huffman
    comp_medio = sum(
        (freq / n) * len(tabela[c])
        for c, freq in frequencias.items()
    )

    return {
        "operacao": "Compactação",
        "arquivo_entrada": caminho_entrada,
        "arquivo_saida": caminho_saida,
        "tamanho_original_bytes": tamanho_orig,
        "tamanho_comprimido_bytes": tamanho_comp,
        "taxa_compressao": taxa,
        "bits_original": tamanho_orig * 8,
        "bits_comprimido": len(bits),
        "caracteres_unicos": len(frequencias),
        "total_caracteres": n,
        "entropia_shannon": entropia,
        "comprimento_medio_huffman": comp_medio,
        "tempo_segundos": t_fim - t_inicio,
        "tabela": tabela,
        "frequencias": frequencias,
    }


def descompactar_arquivo(caminho_entrada: str, caminho_saida: str) -> dict:
    # Lê um .huff e restaura o .txt original. Retorna dicionário com estatísticas.
    
    t_inicio = time.time()

    with open(caminho_entrada, "rb") as f:
        pacote = pickle.load(f)

    raiz  = pacote["arvore"]
    dados = pacote["dados"]
    bits  = bytes_para_bits(dados)
    texto = decodificar(bits, raiz)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(texto)

    t_fim = time.time()

    return {
        "operacao": "Descompactação",
        "arquivo_entrada": caminho_entrada,
        "arquivo_saida": caminho_saida,
        "nome_original": pacote.get("nome_original", "—"),
        "caracteres_restaurados": len(texto),
        "tempo_segundos": t_fim - t_inicio,
        "verificado": True,
    }

#Interface

COR_BG       = "#0f1117"
COR_PAINEL   = "#1a1d27"
COR_BORDA    = "#2a2d3e"
COR_ROXO     = "#7f77dd"
COR_ROXO_ESC = "#534ab7"
COR_VERDE    = "#1d9e75"
COR_VERMELHO = "#e24b4a"
COR_TEXTO    = "#e8e6f0"
COR_MUTED    = "#6b6880"
FONTE        = ("Consolas", 10)
FONTE_TITULO = ("Consolas", 13, "bold")
FONTE_MONO   = ("Consolas", 9)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compactador Huffman")
        self.geometry("780x640")
        self.resizable(True, True)
        self.configure(bg=COR_BG)
        self.stats = None
        self._build_ui()

    # ── Layout principal ──────────────────────────────────

    def _build_ui(self):
        # Cabeçalho
        cab = tk.Frame(self, bg=COR_BG)
        cab.pack(fill="x", padx=24, pady=(20, 4))
        tk.Label(cab, text="⬡ Compactador Huffman", font=FONTE_TITULO,
                 bg=COR_BG, fg=COR_ROXO).pack(side="left")
        tk.Label(cab, text="Algoritmo Guloso (Greedy)", font=("Consolas", 9),
                 bg=COR_BG, fg=COR_MUTED).pack(side="left", padx=12)

        sep = tk.Frame(self, bg=COR_BORDA, height=1)
        sep.pack(fill="x", padx=24, pady=(4, 16))

        # Abas
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        self._style_notebook(nb)

        self.aba_comp    = tk.Frame(nb, bg=COR_BG)
        self.aba_decomp  = tk.Frame(nb, bg=COR_BG)
        self.aba_stats   = tk.Frame(nb, bg=COR_BG)
        self.aba_inspec  = tk.Frame(nb, bg=COR_BG)

        nb.add(self.aba_comp,   text="  Compactar  ")
        nb.add(self.aba_decomp, text="  Descompactar  ")
        nb.add(self.aba_stats,  text="  Estatísticas  ")
        nb.add(self.aba_inspec, text="  Inspecionar .huff  ")

        self._build_aba_compactar()
        self._build_aba_descompactar()

    def _style_notebook(self, nb):
        s = ttk.Style()
        s.theme_use("default")
        s.configure("TNotebook",
                     background=COR_BG, borderwidth=0, tabmargins=[0,0,0,0])
        s.configure("TNotebook.Tab",
                     background=COR_PAINEL, foreground=COR_MUTED,
                     font=("Consolas", 10), padding=[12, 6],
                     borderwidth=0, relief="flat")
        s.map("TNotebook.Tab",
              background=[("selected", COR_ROXO_ESC)],
              foreground=[("selected", COR_TEXTO)])

    def _build_aba_compactar(self):
        f = self.aba_comp
        self._label(f, "Arquivo de entrada (.txt)").pack(anchor="w", padx=16, pady=(16,4))

        row = tk.Frame(f, bg=COR_BG)
        row.pack(fill="x", padx=16, pady=(0,12))
        self.entrada_comp = self._entry(row)
        self.entrada_comp.pack(side="left", fill="x", expand=True)
        self._btn(row, "Procurar", lambda: self._browse(self.entrada_comp,
            [("Texto", "*.txt"), ("Todos", "*.*")])).pack(side="left", padx=(8,0))

        self._label(f, "Arquivo de saída (.huff)").pack(anchor="w", padx=16, pady=(0,4))
        row2 = tk.Frame(f, bg=COR_BG)
        row2.pack(fill="x", padx=16, pady=(0,20))
        self.saida_comp = self._entry(row2)
        self.saida_comp.pack(side="left", fill="x", expand=True)
        self._btn(row2, "Salvar como", lambda: self._save_as(self.saida_comp,
            [("Huffman", "*.huff")], ".huff")).pack(side="left", padx=(8,0))

        self._btn_primario(f, "▶  Compactar", self._executar_compactacao).pack(pady=(0,16))

        self.log_comp = self._log_box(f)

    # ── Aba Descompactar ───────────────────────────────────

    def _build_aba_descompactar(self):
        f = self.aba_decomp
        self._label(f, "Arquivo comprimido (.huff)").pack(anchor="w", padx=16, pady=(16,4))

        row = tk.Frame(f, bg=COR_BG)
        row.pack(fill="x", padx=16, pady=(0,12))
        self.entrada_decomp = self._entry(row)
        self.entrada_decomp.pack(side="left", fill="x", expand=True)
        self._btn(row, "Procurar", lambda: self._browse(self.entrada_decomp,
            [("Huffman", "*.huff"), ("Todos", "*.*")])).pack(side="left", padx=(8,0))

        self._label(f, "Arquivo de saída (.txt)").pack(anchor="w", padx=16, pady=(0,4))
        row2 = tk.Frame(f, bg=COR_BG)
        row2.pack(fill="x", padx=16, pady=(0,20))
        self.saida_decomp = self._entry(row2)
        self.saida_decomp.pack(side="left", fill="x", expand=True)
        self._btn(row2, "Salvar como", lambda: self._save_as(self.saida_decomp,
            [("Texto", "*.txt")], ".txt")).pack(side="left", padx=(8,0))

        self._btn_primario(f, "▶  Descompactar", self._executar_descompactacao).pack(pady=(0,16))
        self.log_decomp = self._log_box(f)
    def _executar_compactacao(self):
        entrada = self.entrada_comp.get().strip()
        saida   = self.saida_comp.get().strip()
        if not entrada or not saida:
            messagebox.showwarning("Atenção", "Selecione os arquivos de entrada e saída.")
            return
        if not os.path.exists(entrada):
            messagebox.showerror("Erro", "Arquivo de entrada não encontrado.")
            return
        try:
            self._log(self.log_comp, f"Compactando: {os.path.basename(entrada)} …")
            stats = compactar_arquivo(entrada, saida)
            self._log(self.log_comp,
                f"✔  Concluído em {stats['tempo_segundos']*1000:.1f} ms  |  "
                f"Taxa: {stats['taxa_compressao']:.1f}%  |  "
                f"Salvo em: {os.path.basename(saida)}", COR_VERDE)
            self.stats = stats
            self._render_stats(stats)
        except Exception as e:
            self._log(self.log_comp, f"✘  Erro: {e}", COR_VERMELHO)
            messagebox.showerror("Erro na compactação", str(e))

    def _executar_descompactacao(self):
        entrada = self.entrada_decomp.get().strip()
        saida   = self.saida_decomp.get().strip()
        if not entrada or not saida:
            messagebox.showwarning("Atenção", "Selecione os arquivos de entrada e saída.")
            return
        if not os.path.exists(entrada):
            messagebox.showerror("Erro", "Arquivo de entrada não encontrado.")
            return
        try:
            self._log(self.log_decomp, f"Descompactando: {os.path.basename(entrada)} …")
            stats = descompactar_arquivo(entrada, saida)
            self._log(self.log_decomp,
                f"✔  Concluído em {stats['tempo_segundos']*1000:.1f} ms  |  "
                f"{stats['caracteres_restaurados']:,} caracteres restaurados.", COR_VERDE)
            self.stats = stats
            self._render_stats(stats)
        except Exception as e:
            self._log(self.log_decomp, f"✘  Erro: {e}", COR_VERMELHO)
            messagebox.showerror("Erro na descompactação", str(e))

    def _label(self, pai, texto, muted=False):
        return tk.Label(pai, text=texto,
                        font=("Consolas", 9), bg=COR_BG,
                        fg=COR_MUTED if muted else COR_TEXTO)

    def _entry(self, pai):
        e = tk.Entry(pai, font=FONTE_MONO, bg=COR_PAINEL, fg=COR_TEXTO,
                     insertbackground=COR_TEXTO, relief="flat", bd=0,
                     highlightbackground=COR_BORDA, highlightthickness=1)
        e.configure(width=45)
        return e

    def _btn(self, pai, texto, cmd):
        return tk.Button(pai, text=texto, command=cmd,
                         font=("Consolas", 9), bg=COR_PAINEL, fg=COR_TEXTO,
                         activebackground=COR_BORDA, activeforeground=COR_TEXTO,
                         relief="flat", bd=0, cursor="hand2", padx=12, pady=5,
                         highlightbackground=COR_BORDA, highlightthickness=1)

    def _btn_primario(self, pai, texto, cmd):
        return tk.Button(pai, text=texto, command=cmd,
                         font=("Consolas", 10, "bold"),
                         bg=COR_ROXO_ESC, fg=COR_TEXTO,
                         activebackground=COR_ROXO, activeforeground=COR_TEXTO,
                         relief="flat", bd=0, cursor="hand2", padx=20, pady=8)

    def _log_box(self, pai):
        frame = tk.Frame(pai, bg=COR_PAINEL,
                         highlightbackground=COR_BORDA, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=16, pady=(0,16))
        scroll = tk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")
        txt = tk.Text(frame, bg=COR_PAINEL, fg=COR_MUTED, font=FONTE_MONO,
                      bd=0, relief="flat", yscrollcommand=scroll.set,
                      height=6, padx=8, pady=6, state="disabled", cursor="arrow")
        txt.pack(fill="both", expand=True)
        scroll.config(command=txt.yview)
        return txt

    def _log(self, widget, msg, cor=None):
        widget.config(state="normal")
        tag = f"c{id(cor)}"
        widget.tag_config(tag, foreground=cor or COR_MUTED)
        widget.insert("end", msg + "\n", tag)
        widget.see("end")
        widget.config(state="disabled")

    def _browse(self, entry, tipos):
        path = filedialog.askopenfilename(filetypes=tipos)
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)
            # Sugerir nome de saída automaticamente
            base, _ = os.path.splitext(path)
            if entry is self.entrada_comp and not self.saida_comp.get():
                self.saida_comp.delete(0, "end")
                self.saida_comp.insert(0, base + ".huff")
            elif entry is self.entrada_decomp and not self.saida_decomp.get():
                self.saida_decomp.delete(0, "end")
                self.saida_decomp.insert(0, base + "_restaurado.txt")

    def _save_as(self, entry, tipos, ext):
        path = filedialog.asksaveasfilename(filetypes=tipos, defaultextension=ext)
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

if __name__ == "__main__":
    app = App()
    app.mainloop()