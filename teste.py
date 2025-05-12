import json
def ordena(dicio):
    chaves = []
    valores = []

    # Separar as chaves e valores em listas
    for chave in dicio:
        chaves.append(chave)
        valores.append(dicio[chave])

    # Ordenar os valores manualmente (Selection Sort)
    i = 0
    while i < len(valores):
        indice_menor = i
        j = i + 1
        while j < len(valores):
            if valores[j] < valores[indice_menor]:
                indice_menor = j
            j += 1
        # Troca os valores
        temp = valores[i]
        valores[i] = valores[indice_menor]
        valores[indice_menor] = temp
        i += 1

    # Criar novo dicionário ordenado
    novo = {}
    usados = []

    for valor in valores:
        for chave in dicio:
            if dicio[chave] == valor and chave not in usados:
                novo[chave] = valor
                usados.append(chave)
                break

    return novo
        


with open("ranking.json","r") as arquivo:
    texto=arquivo.read()
dicionario = json.loads(texto)
pontos=int(input("pontos: "))
us=input("nome: ")
dicionario[us]=pontos
dicionario2=ordena(dicionario)
if len(dicionario2)>3:
    i=0
    dicionario3={}
    for chave,valor in dicionario2.items():
        if i<3:
            dicionario3[chave]=valor
        i=i+1
else:
    dicionario3=dicionario2

hum=json.dumps(dicionario3)
with open('ranking.json', 'w') as arquivo_json:
    arquivo_json.write(hum)
print(hum)