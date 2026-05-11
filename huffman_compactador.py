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
