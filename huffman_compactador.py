import heapq
from collections import Counter

class No:
    #Nó da árvore binária de Huffman.
    def __init__(self, char, freq):
        self.char = char      # Caractere (None para nós internos)
        self.freq = freq      # Frequência acumulada
        self.esq  = None      # Filho esquerdo  (bit 0)
        self.dir  = None      # Filho direito   (bit 1)

    def __lt__(self, outro):
        return self.freq < outro.freq

def construir_arvore(texto: str) -> tuple[No, dict]:
    """
    Constrói a árvore de Huffman via algoritmo guloso:
    a cada passo escolhe os dois nós de menor frequência.
    Retorna (raiz, tabela_de_frequências).
    """
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
        menor1 = heapq.heappop(heap)   # ← decisão gulosa
        menor2 = heapq.heappop(heap)   # ← decisão gulosa
        pai = No(None, menor1.freq + menor2.freq)
        pai.esq = menor1
        pai.dir = menor2
        heapq.heappush(heap, pai)

    return heap[0], frequencias

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

    print("\nFrequências:")
    for char, freq in frequencias.items():
        label = "espaço" if char == " " else char
        print(f"  {label!r}: {freq}")
