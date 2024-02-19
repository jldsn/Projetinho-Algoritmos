import csv
import math
from collections import defaultdict
import matplotlib.pyplot as plt
from tkinter import *

#Função para calcular a distância entre duas coordenadas geográficas
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  #Raio da Terra em kms
    dlat = math.radians(lat2 - lat1) #Cálculo da latitude entre dois pontos
    dlon = math.radians(lon2 - lon1) #Cálculo da longitude entre dois pontos
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

#Função que carrega as estações a partir do arquivo Stations.csv 
def load_stations(filename):
    stations = {} #Dicionário vazio criado para receber as estações 
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile) #leitor csv para iterar sobre as linhas do arquivo
        next(reader)  #pula a primeira linha, que é o cabeçalho.
        for row in reader:
            station_id, latitude, longitude, name, _, _, _, _ = row #"extrai" os campos de id da estação, lat e long e o nome, e ignora os outros 4 campos
            stations[int(station_id)] = {
                'latitude': float(latitude),
                'longitude': float(longitude),
                'name': name
            }#Adiciona os campos no dicionário station onde a chave é o ID(int) da estação e o valor é um dic que contém as demais informações relevantes 
    return stations

#Função que carrega as conexões a partir do arquivo Line_definitions.csv 
def load_connections(filename, stations):
    graph = defaultdict(dict) #Cria um defaultdict para representar o grafo, tendo como chave o ID das estações e os valores sendo dicionários que contém a estação vizinha e a informação de linha e peso.
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile) #leitor csv para iterar sobre as linhas do arquivo
        next(reader) #pula a primeira linha, que é o cabeçalho.
        #itera sobre as linhas do arquivo csv.
        for row in reader: 
            station1, station2, line = map(int, row) #extrai as infos de cada linha do arquivo
            #calcula a distância entre as estações e as usa como peso: 
            weight = haversine(stations[station1]['latitude'], stations[station1]['longitude'], stations[station2]['latitude'], stations[station2]['longitude']) 
            #Conecta os grafos de uma estação pra outra e atribui tambenm o peso e linha referentes
            graph[station1][station2] = (weight, line) 
            graph[station2][station1] = (weight, line)

    return graph

#Função dijkstra que recebe os argumentos de grafo, e os vertices de inicio e fim
def dijkstra(graph, start, end):
    unvisited = set(graph.keys()) #seta um conjunto contendo todos os vertices do grafo.
    distances = {node: float('infinity') for node in graph} #cria um dicionario tendo o vertice como chave e o valor é a distancia do vertice ao vertice de inicio, e inicialmente todas essas distancias estão definidas como infinito.
    distances[start] = 0 #ponto de partida do vertice de inicio definido como 0
    previous_nodes = {node: None for node in graph} #dicionario que rastreia os vertices que vieram antes ao longo do menor caminho.

    while unvisited:
        current_node = min(unvisited, key=lambda node: distances[node]) #seleciona o vertice não visitado com menor distancia ao vertice de inicio 
        unvisited.remove(current_node) #remove o vertice atual da lsita de não visitados

        if current_node == end: 
            break #se o vertice atual for o de destino, encerra o loop.

        for neighbor, (weight, line) in graph[current_node].items():
            if neighbor not in unvisited:
                continue #se o vizinho ja foi visitado, passa para o proximo
            new_distance = distances[current_node] + weight #calcula a distancia nova até o vizinho através do vertice atual
            if new_distance < distances[neighbor]: #verificação para saber se a nova distância é menor do que a distância registrada atualmente para o vizinho.
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node

    path = [] #Lista que armazena o caminho do vertice fim até o vertice inicio
    while end is not None: #Loop para rastrear o vertice de fim ate o de inicio
        path.append(end)
        end = previous_nodes[end]
    path = path[::-1]

    return path, distances[path[-1]] #Retorna o caminho mais curto e a distancia total do caminho.

def update_graph(entry_start, entry_end, label_result):
    start_station = int(entry_start.get()) #entrada do vertice (ID) de partida
    end_station = int(entry_end.get()) #entrada do vertice de (ID) chegada

    # Verificação se o número de estação digitada é válido
    num_stations = len(stations)
    if start_station > num_stations or end_station > num_stations:
        label_result.config(text=f"Erro: Você digitou um número maior do que o número de estações disponíveis ({num_stations}).")
        return #retorna erro caso nao seja
    
    #Executa o algoritmo para encontrar o menor caminho
    path, total_weight = dijkstra(graph, start_station, end_station)

    #construção do texto que vai ser impresso no output com o resultado
    result_text = f"O menor caminho entre as estações {stations[start_station]['name']} e {stations[end_station]['name']} é:\n"
    for i, station_id in enumerate(path):
        if i > 0:
            result_text += ", "
        result_text += f"{station_id} ({stations[station_id]['name']})"
    result_text += f"\nO peso total do caminho é: {total_weight:.2f}"
    label_result.config(text=result_text)

    plt.clf() #limpa o gráfico anterior 

    #plota o grafico de conexoes entre estações
    for station1 in graph:
        for station2, (weight, line) in graph[station1].items():
            if (station1, station2) in zip(path, path[1:]) or (station2, station1) in zip(path, path[1:]):
                plt.plot([stations[station1]['latitude'], stations[station2]['latitude']], [stations[station1]['longitude'], stations[station2]['longitude']], color='red', linestyle='-', linewidth=1.5)
                plt.text((stations[station1]['latitude'] + stations[station2]['latitude']) / 2, (stations[station1]['longitude'] + stations[station2]['longitude']) / 2, str(line), fontsize=8, ha='center', va='center', color='red')
            else:
                plt.plot([stations[station1]['latitude'], stations[station2]['latitude']], [stations[station1]['longitude'], stations[station2]['longitude']], color='grey', linestyle='-', linewidth=0.5)

    #adiciona os marcadores de partida e chegada
    plt.scatter(stations[start_station]['latitude'], stations[start_station]['longitude'], color='green', label='Estação de partida', zorder=5)
    plt.scatter(stations[end_station]['latitude'], stations[end_station]['longitude'], color='red', label='Estação de chegada', zorder=5)

    #legendas e títulos para melhor vizualização e entendimento.
    plt.legend()
    plt.title("Conexões entre as estações de metrô")
    plt.xlabel("Latitude")
    plt.ylabel("Longitude")
    plt.show() #mostra o grafico atualizado

def create_gui():
    root = Tk()
    root.title("Encontrar Rota de Metrô")

    frame = Frame(root)
    frame.pack(padx=10, pady=10)

    label_start = Label(frame, text="Estação de Partida:")
    label_start.grid(row=0, column=0, padx=5, pady=5, sticky=W)

    entry_start = Entry(frame)
    entry_start.grid(row=0, column=1, padx=5, pady=5)

    label_end = Label(frame, text="Estação de Chegada:")
    label_end.grid(row=1, column=0, padx=5, pady=5, sticky=W)

    entry_end = Entry(frame)
    entry_end.grid(row=1, column=1, padx=5, pady=5)

    button_submit = Button(frame, text="Encontrar Rota", command=lambda: update_graph(entry_start, entry_end, label_result))
    button_submit.grid(row=2, columnspan=2, padx=5, pady=5)

    label_result = Label(frame, text="", wraplength=400) 
    label_result.grid(row=3, columnspan=2, padx=5, pady=5)

    root.mainloop()

stations = load_stations("Stations.csv")
graph = load_connections("Line_definitions.csv", stations)

create_gui()