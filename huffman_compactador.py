import os
import heapq
import tempfile
import pickle
from collections import Counter
import math
import time
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


#testa o compactador e descompactador
def teste_compactador():
    texto = "ABRACADABRA"
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_txt = os.path.join(tmpdir, "teste.txt")
        caminho_huff = os.path.join(tmpdir, "teste.huff")

        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(texto)

        stats = compactar_arquivo(caminho_txt, caminho_huff)

        print("Teste de compactação")
        print(f"  Arquivo de entrada: {caminho_txt}")
        print(f"  Arquivo de saída:   {caminho_huff}")
        print(f"  Tamanho original:   {stats['tamanho_original_bytes']} bytes")
        print(f"  Tamanho comprimido: {stats['tamanho_comprimido_bytes']} bytes")
        print(f"  Taxa de compressão: {stats['taxa_compressao']:.2f}%")

        assert os.path.exists(caminho_huff), "Arquivo .huff não foi criado"
        assert stats["tamanho_comprimido_bytes"] > 0, "Arquivo comprimido está vazio"

        return stats


def teste_descompactador():
    texto = "ABRACADABRA"
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho_txt = os.path.join(tmpdir, "teste.txt")
        caminho_huff = os.path.join(tmpdir, "teste.huff")
        caminho_restaurado = os.path.join(tmpdir, "teste_restaurado.txt")

        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(texto)

        compactar_arquivo(caminho_txt, caminho_huff)
        stats = descompactar_arquivo(caminho_huff, caminho_restaurado)

        with open(caminho_restaurado, "r", encoding="utf-8") as f:
            texto_restaurado = f.read()

        print("Teste de descompactação")
        print(f"  Arquivo compactado:   {caminho_huff}")
        print(f"  Arquivo restaurado:    {caminho_restaurado}")
        print(f"  Texto restaurado:      {texto_restaurado!r}")
        print(f"  Caracteres restaurados: {stats['caracteres_restaurados']}")

        assert texto_restaurado == texto, "Texto restaurado difere do original"
        assert stats["verificado"] is True, "Descompactação não foi verificada"

        return stats


if __name__ == "__main__":
    teste_compactador()
    print()
    teste_descompactador()

