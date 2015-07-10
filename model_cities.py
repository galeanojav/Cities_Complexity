""" model_cities.py is a model of distribution of population in Spain from 1842 to 2014.
"""
__author__ = 'Javier Galeano (javier.galeano@upm.es) && Fernando de Frutos (defrutosgarciafernando@gmail.com)'
__version__ = '1.0'

#imports

import matplotlib
import random as rd
from pylab import *
import numpy as np
import networkx as nx

#_____________________________________________________________________________
# INPUT DATA 

def net_spain(database, database_links):
    
    Mun_INE = nx.Graph()
    g_draw = nx.Graph()
    
    # Nodes

    text_Mun = open(str(database), 'r')
    text_nodes = text_Mun.read()
    lines_text_nodes = text_nodes.splitlines()

    for element_nodes in lines_text_nodes:
        unit_nodes = element_nodes.split('\t')
    
        ID = unit_nodes[0]
        provincia = unit_nodes[1]
        name = unit_nodes[2]
        x_coord = unit_nodes[3]
        y_coord = unit_nodes[4]
        Pob_1842 = unit_nodes[5]
    
        Mun_INE.add_node(ID)
        Mun_INE.node[ID]['provincia'] = provincia
        Mun_INE.node[ID]['name'] = name
        Mun_INE.node[ID]['x_coord'] = float(x_coord)
        Mun_INE.node[ID]['y_coord'] = float(y_coord)
        Mun_INE.node[ID]['Pob_1842'] = int(Pob_1842)

    text_Mun.close()

    # Edges
    text_AdjList = open(str(database_links), 'r')
    text_edges = text_AdjList.read()
    lines_text_edges = text_edges.splitlines()

    for element_edges in lines_text_edges:
        unit_edges = element_edges.split('\t')
        source = unit_edges[0]
        target = unit_edges[1]
        Mun_INE.add_edge(source, target)
        Migracion_Pob = unit_edges[2]
        Mun_INE.edge[source][target]['Mig_Pob'] = int(Migracion_Pob)

    text_AdjList.close()
    
    # Coordinates
    Mun_INE.pos = nx.spring_layout(Mun_INE)
    
    for nodo in Mun_INE.nodes_iter():
    
        x = Mun_INE.node[nodo]['x_coord']
        y = Mun_INE.node[nodo]['y_coord']
        Mun_INE.pos[nodo] = array([x, y])


    
    return(Mun_INE)

#_____________________________________________________________________________    
# DRAWING THE MODEL NETWORK BUILDER


# funcion color enlaces
def colors_links(Mig_Pob):
    if Mig_Pob < 2:
        # color = [1, 1, 1] blanco
        color = [0.134, 0.134, 0.134] #gris 
    elif Mig_Pob < 10:
        color = [0.5, 0, 1] #morado
    elif Mig_Pob < 50: 
        color = [0, 0, 0.8] #azul oscuro
    elif Mig_Pob < 100:
        color = [0, 0.7, 1] #cian
    elif Mig_Pob < 300:
        color = [0, 1, 0] #verde
    elif Mig_Pob < 500:     
        color = [1, 1, 0] #amarillo
    elif Mig_Pob < 1000:        
        color = [1, 0, 0] #rojo
    else:
        color = [1, 1, 1] #blanco
    return color

# funcion color nodos
def colors_nodes(pob_year):
    if pob_year < 10:
        color = [0.5, 0.5, 0.5] #blanco
    elif pob_year < 100:
        color = [0.5, 0, 1] #morado
    elif pob_year < 1000:
        color = [0, 0, 0.8] #azul oscuro
    elif pob_year < 10000:
        color = [0, 0.7, 1] #cian
    elif pob_year < 100000:
        color = [0, 1, 0] #verde
    elif pob_year < 1000000:
        color = [1, 1, 0] #amarillo
    elif pob_year < 10000000:
        color = [1, 0, 0]#rojo
    else:
        color = [1, 1, 1] #blanco
    return color


#_____________________________________________________________________________
# INITIAL DATA 

def init(min_rat,max_rat):
    global g, nextg, positions
    g = Mun_INE
    style.use('dark_background')
    bias =linspace(min_rat,max_rat) #(-0.7,0.7)
    
    for nd in g.nodes_iter():      
        g.node[nd]['poblacion'] = g.node[nd]['Pob_1842']#1000.0*random()
        g.node[nd]['epsi'] = round(rd.choice(bias),3)
        positions = Mun_INE.pos
        
        if g.node[nd]['poblacion'] == 0:
            g.node[nd]['poblacion'] = 1
        
    #g.node['40194']['epsi']=0.001 # estabilizador 
    nextg = g.copy()

#_____________________________________________________________________________
# Draw DATA 
 
def draw():
    global g, nextg, positions, g_draw
    cla()      
    
    nx.draw(g, pos = positions, alpha = 0.8,
            linewidths = 0.1,
            node_color = [colors_nodes(g.node[nd]['poblacion']) for nd in g.nodes_iter()],
            node_size = [0.5*log(g.node[nd]['poblacion']) for nd in g.nodes_iter()],
            width = 0,
            node_edge = 'gray')
    

def step(alpha,min_rat,max_rat):
    
    global g, nextg, positions
    Dt = 0.01
    bias =linspace(min_rat,max_rat)
    
    for i in g.nodes_iter():
        if g.node[i]['poblacion'] == 0:
            g.node[i]['poblacion'] = 1
        
        g.node[i]['epsi'] = round(rd.choice(bias),3)
        #g.node['40194']['epsi'] = 0.1 #0.1 #0.005 # estabilizador
        
        # Solo Crecimiento multiplicativo 
        # g.node[i]['poblacion'] = g.node[i]['poblacion'] + g.node[i]['poblacion']*g.node[i]['epsi']
        
        # Crecimiento multiplicativo con difusion -> alpha peso
        p_i = g.node[i]['poblacion'] #Poblacion en cada nodo
        w_nor = sum(g.edge[i][k]['Mig_Pob'] for k in g.neighbors(i))
        
        for j in g.neighbors(i):
            w_i = g.edge[i][j]['Mig_Pob']
            w_ij = alpha*float(w_i)/w_nor
            #print w_ij
        nextg.node[i]['poblacion'] = p_i + p_i*g.node[i]['epsi'] + w_ij * (sum(g.node[j]['poblacion'] for j in g.neighbors(i)) - p_i * g.degree(i))* Dt

    g, nextg = nextg, g

#_____________________________________________________________________________
# MAIN ()

Mun_INE=net_spain('Base_mun.csv','Base_links.csv')
num_itero = 2
g = Mun_INE
poblacion_acum = np.zeros(len(g.node))

for num_iter in xrange(num_itero):
    
    #print num_iter
    init(-0.5,0.5)
    for t in xrange(1, 11):
        #print t
        step(0.5,-0.5,1.0)
        #if (t%5 == 0):
        #    draw()
        #    savefig('pob_bin-0p7_0p7_'+ str(t) +'.png',dpi=400)

        
    poblacion_2014=[g.node[i]['poblacion'] for i in g.nodes_iter()]
    poblacion_2014.sort(reverse=True)
    
    poblacion_acum =poblacion_acum + poblacion_2014

poblacion_media = poblacion_acum/num_itero

fout2 = open('pobmed2_bin-0p5_0p5_or1842_al1p0_niter10.txt','w')

for i in range(len(poblacion_media)):
    fout2.write(str(poblacion_media[i])+'\n')
fout2.close()
