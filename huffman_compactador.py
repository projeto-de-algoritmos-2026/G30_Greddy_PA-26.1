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
        self._build_aba_stats()
        self._build_aba_inspecionar()

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

    def _build_aba_stats(self):
        f = self.aba_stats
        self.stats_frame = tk.Frame(f, bg=COR_BG)
        self.stats_frame.pack(fill="both", expand=True, padx=16, pady=16)
        self._label(self.stats_frame,
            "Execute uma compactação para ver as estatísticas aqui.",
            muted=True).pack(pady=40)

    def _build_aba_inspecionar(self):
        f = self.aba_inspec
        self._label(f, "Arquivo .huff para inspecionar").pack(anchor="w", padx=16, pady=(16,4))

        row = tk.Frame(f, bg=COR_BG)
        row.pack(fill="x", padx=16, pady=(0,12))
        self.entrada_inspec = self._entry(row)
        self.entrada_inspec.pack(side="left", fill="x", expand=True)
        self._btn(row, "Procurar", lambda: self._browse(self.entrada_inspec,
            [("Huffman", "*.huff"), ("Todos", "*.*")])).pack(side="left", padx=(8,0))

        self._btn_primario(f, "Inspecionar", self._executar_inspecao).pack(pady=(0,16))

        frame = tk.Frame(f, bg=COR_PAINEL,
                         highlightbackground=COR_BORDA, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=16, pady=(0,16))
        scroll_y = tk.Scrollbar(frame)
        scroll_y.pack(side="right", fill="y")
        scroll_x = tk.Scrollbar(frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")
        self.inspec_txt = tk.Text(
            frame, bg=COR_PAINEL, fg=COR_TEXTO, font=FONTE_MONO,
            bd=0, relief="flat",
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
            wrap="none", padx=10, pady=8, state="disabled", cursor="arrow"
        )
        self.inspec_txt.pack(fill="both", expand=True)
        scroll_y.config(command=self.inspec_txt.yview)
        scroll_x.config(command=self.inspec_txt.xview)

        self.inspec_txt.tag_config("titulo", foreground=COR_ROXO,  font=("Consolas", 9, "bold"))
        self.inspec_txt.tag_config("sep",    foreground=COR_BORDA)
        self.inspec_txt.tag_config("chave",  foreground=COR_MUTED, font=("Consolas", 9))
        self.inspec_txt.tag_config("char",   foreground=COR_ROXO,  font=("Consolas", 9, "bold"))
        self.inspec_txt.tag_config("code",   foreground=COR_VERDE, font=("Consolas", 9))
        self.inspec_txt.tag_config("num",    foreground="#e8c97a", font=("Consolas", 9))
        self.inspec_txt.tag_config("bits",   foreground="#5dcaa5", font=("Consolas", 8))
        self.inspec_txt.tag_config("muted",  foreground=COR_MUTED, font=("Consolas", 8))
        self.inspec_txt.tag_config("ok",     foreground=COR_VERDE, font=("Consolas", 9, "bold"))
        self.inspec_txt.tag_config("normal", foreground=COR_TEXTO, font=("Consolas", 9))

    def _executar_inspecao(self):
        caminho = self.entrada_inspec.get().strip()
        if not caminho:
            messagebox.showwarning("Atencao", "Selecione um arquivo .huff.")
            return
        if not os.path.exists(caminho):
            messagebox.showerror("Erro", "Arquivo nao encontrado.")
            return
        try:
            with open(caminho, "rb") as f:
                pacote = pickle.load(f)
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel ler o arquivo:\n{e}")
            return

        raiz   = pacote["arvore"]
        dados  = pacote["dados"]
        nome   = pacote.get("nome_original", "desconhecido")
        n_orig = pacote.get("tamanho_original", 0)

        tabela = gerar_codigos(raiz)
        freqs  = {}
        def colher_freq(no):
            if no is None: return
            if no.char is not None: freqs[no.char] = no.freq
            colher_freq(no.esq); colher_freq(no.dir)
        colher_freq(raiz)

        padding = dados[0]
        n_bytes = len(dados) - 1
        n_bits  = n_bytes * 8 - padding
        tam_arq = os.path.getsize(caminho)

        txt = self.inspec_txt
        txt.config(state="normal")
        txt.delete("1.0", "end")

        def w(texto, tag="normal"):
            txt.insert("end", texto, tag)

        sep = "-" * 62 + "\n"

        w("  INSPECAO DO ARQUIVO .huff\n\n", "titulo")

        w("  CABECALHO\n", "titulo")
        w(sep, "sep")
        w(f"  {'Arquivo inspecionado':<28}", "chave");  w(f"{os.path.basename(caminho)}\n", "normal")
        w(f"  {'Nome original gravado':<28}", "chave"); w(f"{nome}\n", "normal")
        w(f"  {'Tamanho do .huff no disco':<28}", "chave"); w(f"{tam_arq:,} bytes\n", "num")
        w(f"  {'Chars originais':<28}", "chave"); w(f"{n_orig:,}\n", "num")
        w(f"  {'Bits de dados comprimidos':<28}", "chave"); w(f"{n_bits:,} bits  ", "num")
        w(f"({n_bytes:,} bytes + padding de {padding} bits)\n", "muted")
        w(f"  {'Simbolos unicos':<28}", "chave"); w(f"{len(tabela)}\n\n", "num")

        w("  TABELA DE CODIGOS HUFFMAN\n", "titulo")
        w(sep, "sep")
        w(f"  {'Char':<10}{'Freq':<10}{'Codigo binario':<32}{'Bits':<6}Custo\n", "chave")
        w("  " + "." * 60 + "\n", "sep")

        for c, code in sorted(tabela.items(), key=lambda x: len(x[1])):
            freq  = freqs.get(c, 0)
            custo = freq * len(code)
            label = "esp" if c == " " else repr(c)[1:-1]
            w(f"  {label:<10}", "char")
            w(f"{freq:<10}", "num")
            w(f"{code:<32}", "code")
            w(f"{len(code):<6}", "num")
            w(f"{custo}\n", "muted")

        w("\n")
        w("  ESTRUTURA BINARIA\n", "titulo")
        w(sep, "sep")
        w("  Byte 0    ", "chave"); w(f"padding = {padding}", "num")
        w("  (bits de preenchimento no fim)\n\n", "muted")
        w("  Primeiros bytes em binario:\n", "chave")
        for i, byte in enumerate(dados[1:9]):
            w(f"  Byte {i+1:>2}   ", "chave")
            w(f"{byte:08b}", "bits")
            w(f"   (decimal {byte})\n", "muted")
        if n_bytes > 8:
            w(f"  ... mais {n_bytes - 8} bytes ...\n", "muted")

        w("\n")
        w("  RESUMO\n", "titulo")
        w(sep, "sep")
        bits_orig = n_orig * 8
        if bits_orig:
            # taxa real = compara tamanho total do .huff (inclui árvore) com o .txt original
            taxa_real = (1 - tam_arq / n_orig) * 100
            # taxa só dos dados = ignora overhead da árvore (número "otimista")
            taxa_dados = (1 - n_bits / bits_orig) * 100
            cor_taxa = "ok" if taxa_real > 0 else "char"
            w(f"  {'Bytes originais (.txt)':<38}", "chave");       w(f"{n_orig:,} bytes\n", "num")
            w(f"  {'Bytes do .huff (arquivo real)':<38}", "chave"); w(f"{tam_arq:,} bytes  ", "num")
            w(f"(inclui arvore + dados)\n", "muted")
            w(f"  {'Taxa real de compressao':<38}", "chave");       w(f"{taxa_real:.1f}%\n", cor_taxa)
            w(f"\n  {'Apenas bits de dados (sem overhead)':<38}", "muted")
            w(f"{n_bits:,} bits vs {bits_orig:,} bits", "muted")
            w(f"  →  {taxa_dados:.1f}%\n", "muted")
            w(f"  (esse numero ignora o peso da arvore serializada)\n\n", "muted")
        w("  Arquivo integro. Arvore e dados decodificaveis.\n", "ok")

        txt.config(state="disabled")

    def _render_stats(self, s: dict):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        # Título
        op = s.get("operacao", "")
        cor_op = COR_VERDE if op == "Compactação" else COR_ROXO
        tk.Label(self.stats_frame, text=f"Resultado: {op}",
                 font=("Consolas", 11, "bold"), bg=COR_BG, fg=cor_op
                 ).pack(anchor="w", pady=(0,12))

        if op == "Compactação":
            self._cards_comp(s)
            self._tabela_codigos(s)
        else:
            self._cards_decomp(s)

    def _cards_comp(self, s):
        grid = tk.Frame(self.stats_frame, bg=COR_BG)
        grid.pack(fill="x", pady=(0,16))
        grid.columnconfigure((0,1,2,3), weight=1, uniform="col")

        taxa = s["taxa_compressao"]
        cor_taxa = COR_VERDE if taxa > 0 else COR_VERMELHO

        items = [
            ("Tamanho original",   f"{s['tamanho_original_bytes']:,} bytes", COR_TEXTO),
            ("Tamanho comprimido", f"{s['tamanho_comprimido_bytes']:,} bytes", COR_TEXTO),
            ("Taxa de compressão", f"{taxa:.1f}%", cor_taxa),
            ("Tempo",              f"{s['tempo_segundos']*1000:.1f} ms", COR_TEXTO),
            ("Caracteres únicos",  str(s["caracteres_unicos"]), COR_TEXTO),
            ("Total de chars",     f"{s['total_caracteres']:,}", COR_TEXTO),
            ("Entropia Shannon",   f"{s['entropia_shannon']:.3f} b/símbolo", COR_TEXTO),
            ("Compr. médio Huff",  f"{s['comprimento_medio_huffman']:.3f} b/símbolo", COR_TEXTO),
        ]
        for i, (lbl, val, cor) in enumerate(items):
            card = tk.Frame(grid, bg=COR_PAINEL, bd=0,
                            highlightbackground=COR_BORDA, highlightthickness=1)
            card.grid(row=i//4, column=i%4, padx=4, pady=4, sticky="nsew")
            tk.Label(card, text=lbl, font=("Consolas", 8), bg=COR_PAINEL,
                     fg=COR_MUTED).pack(anchor="w", padx=10, pady=(8,0))
            tk.Label(card, text=val, font=("Consolas", 12, "bold"),
                     bg=COR_PAINEL, fg=cor).pack(anchor="w", padx=10, pady=(2,8))

        # Barra visual de compressão
        pct = max(0, min(100, s["taxa_compressao"]))
        tk.Label(self.stats_frame, text="Redução de tamanho",
                 font=("Consolas", 9), bg=COR_BG, fg=COR_MUTED
                 ).pack(anchor="w", pady=(4,4))
        canvas = tk.Canvas(self.stats_frame, height=16, bg=COR_PAINEL,
                           bd=0, highlightthickness=0)
        canvas.pack(fill="x", pady=(0,16))
        canvas.update_idletasks()
        w = canvas.winfo_width() or 700
        canvas.create_rectangle(0, 0, w, 16, fill=COR_BORDA, outline="")
        canvas.create_rectangle(0, 0, w * (pct/100), 16, fill=COR_VERDE, outline="")
        canvas.create_text(w//2, 8, text=f"{pct:.1f}% economizado",
                           fill=COR_TEXTO, font=("Consolas", 8))

    def _cards_decomp(self, s):
        grid = tk.Frame(self.stats_frame, bg=COR_BG)
        grid.pack(fill="x", pady=(0,16))
        grid.columnconfigure((0,1,2), weight=1, uniform="col")
        items = [
            ("Arquivo original",       s.get("nome_original", "—"),   COR_TEXTO),
            ("Caracteres restaurados", f"{s['caracteres_restaurados']:,}", COR_VERDE),
            ("Tempo",                  f"{s['tempo_segundos']*1000:.1f} ms", COR_TEXTO),
        ]
        for i, (lbl, val, cor) in enumerate(items):
            card = tk.Frame(grid, bg=COR_PAINEL, bd=0,
                            highlightbackground=COR_BORDA, highlightthickness=1)
            card.grid(row=0, column=i, padx=4, pady=4, sticky="nsew")
            tk.Label(card, text=lbl, font=("Consolas", 8), bg=COR_PAINEL,
                     fg=COR_MUTED).pack(anchor="w", padx=10, pady=(8,0))
            tk.Label(card, text=val, font=("Consolas", 12, "bold"),
                     bg=COR_PAINEL, fg=cor).pack(anchor="w", padx=10, pady=(2,8))
        ok = tk.Label(self.stats_frame,
                      text="✔  Arquivo restaurado e verificado com sucesso.",
                      font=("Consolas", 10), bg=COR_BG, fg=COR_VERDE)
        ok.pack(pady=12)

    def _tabela_codigos(self, s):
        tk.Label(self.stats_frame, text="Tabela de códigos Huffman",
                 font=("Consolas", 9, "bold"), bg=COR_BG, fg=COR_MUTED
                 ).pack(anchor="w", pady=(4,6))

        frame = tk.Frame(self.stats_frame, bg=COR_PAINEL,
                         highlightbackground=COR_BORDA, highlightthickness=1)
        frame.pack(fill="both", expand=True)

        scroll = tk.Scrollbar(frame)
        scroll.pack(side="right", fill="y")
        txt = tk.Text(frame, bg=COR_PAINEL, fg=COR_TEXTO, font=FONTE_MONO,
                      bd=0, relief="flat", yscrollcommand=scroll.set,
                      height=10, padx=10, pady=8, cursor="arrow",
                      state="normal")
        txt.pack(fill="both", expand=True)
        scroll.config(command=txt.yview)
        txt.tag_config("hdr",   foreground=COR_MUTED)
        txt.tag_config("char",  foreground=COR_ROXO,   font=("Consolas", 9, "bold"))
        txt.tag_config("code",  foreground=COR_VERDE)
        txt.tag_config("freq",  foreground=COR_TEXTO)

        txt.insert("end", f"{'Char':<8}{'Freq':<8}{'Código':<28}{'Bits':<6}Custo\n", "hdr")
        txt.insert("end", "─"*58 + "\n", "hdr")

        tabela = s["tabela"]
        freqs  = s["frequencias"]
        n      = s["total_caracteres"]
        for c, code in sorted(tabela.items(), key=lambda x: len(x[1])):
            f = freqs[c]
            label = "␣" if c == " " else repr(c)[1:-1]
            txt.insert("end", f"{label:<8}", "char")
            txt.insert("end", f"{f:<8}", "freq")
            txt.insert("end", f"{code:<28}", "code")
            txt.insert("end", f"{len(code):<6}{f*len(code)}\n", "freq")

        txt.config(state="disabled")
    
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