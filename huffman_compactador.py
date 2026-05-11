import heapq
from collections import Counter

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



#Testando a criação da arvore
def imprimir_arvore(no, nivel=0):
    if no is None:
        return
    indent = "  " * nivel
    if no.char is not None:
        print(f"{indent}Folha: '{no.char}' freq={no.freq}")
    else:
        print(f"{indent}No interno freq={no.freq}")
    imprimir_arvore(no.esq, nivel + 1)
    imprimir_arvore(no.dir, nivel + 1)


if __name__ == "__main__":
    texto = "ABRACADABRA"
    print(f"Texto de teste: {texto}\n")

    raiz, frequencias = construir_arvore(texto)
    print("Árvore de Huffman:")
    imprimir_arvore(raiz)

    tabela = gerar_codigos(raiz)
    print("\nCódigos Huffman:")
    for char, codigo in sorted(tabela.items(), key=lambda x: (len(x[1]), x[0])):
        label = "espaço" if char == " " else char
        print(f"  {label!r}: {codigo}")

    print("\nFrequências:")
    for char, freq in frequencias.items():
        label = "espaço" if char == " " else char
        print(f"  {label!r}: {freq}")


