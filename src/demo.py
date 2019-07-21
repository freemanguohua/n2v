#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : demo.py
# Author            : Wan Li
# Date              : 21.07.2019
# Last Modified Date: 21.07.2019
# Last Modified By  : Wan Li

import argparse
import numpy as np
import networkx as nx
import n2v
from gensim.models import Word2Vec

def parse_args():
    '''
    Parses the node2vec arguments.
    '''
    parser = argparse.ArgumentParser(description="Run node2vec.")

    parser.add_argument('--input', nargs='?', default='../data/karate.edgelist',
                        help='Input graph path')

    parser.add_argument('--output', nargs='?', default='../output/karate.emb',
                        help='Embeddings path')

    parser.add_argument('--dimensions', type=int, default=128,
                        help='Number of dimensions. Default is 128.')

    parser.add_argument('--walk-length', type=int, default=80,
                        help='Length of walk per source. Default is 80.')

    parser.add_argument('--num-walks', type=int, default=10,
                        help='Number of walks per source. Default is 10.')

    parser.add_argument('--window-size', type=int, default=10,
                        help='Context size for optimization. Default is 10.')

    parser.add_argument('--iter', default=1, type=int,
                      help='Number of epochs in SGD')

    parser.add_argument('--workers', type=int, default=8,
                        help='Number of parallel workers. Default is 8.')

    parser.add_argument('--p', type=float, default=1,
                        help='Return hyperparameter. Default is 1.')

    parser.add_argument('--q', type=float, default=1,
                        help='Inout hyperparameter. Default is 1.')

    parser.add_argument('--weighted', dest='weighted', action='store_true',
                        help='Boolean specifying (un)weighted. Default is unweighted.')
    parser.add_argument('--unweighted', dest='unweighted', action='store_false')
    parser.set_defaults(weighted=False)

    parser.add_argument('--directed', dest='directed', action='store_true',
                        help='Graph is (un)directed. Default is undirected.')
    parser.add_argument('--undirected', dest='undirected', action='store_false')
    parser.set_defaults(directed=False)

    return parser.parse_args()


def read_graph(input, is_weighted, is_directed):
    '''
    Reads the input network in networkx.
    '''
    if is_weighted:
        G = nx.read_edgelist(input, nodetype=int, data=(('weight',float),), create_using=nx.DiGraph())
    else:
        G = nx.read_edgelist(input, nodetype=int, create_using=nx.DiGraph())
        for edge in G.edges():
            G[edge[0]][edge[1]]['weight'] = 1

    if not is_directed:
        G = G.to_undirected()
    return G


def learn_embeddings(walks, dimensions, window_size, workers, iter, output):
    '''
    Learn embeddings by optimizing the Skipgram objective using SGD.
    '''
    walks = [list(map(str, walk)) for walk in walks]
    model = Word2Vec(walks, size=dimensions, window=window_size, min_count=0, sg=1, workers=workers, iter=iter)
    model.wv.save_word2vec_format(output)


def main(args):
    '''
    Pipeline for representational learning for all nodes in a graph.
    '''
    nx_G = read_graph(input=args.input, is_weighted=args.weighted, is_directed=args.directed)
    G = n2v.Graph(nx_G, is_directed=args.directed, p=args.p, q=args.q)
    G.preprocess_transition_probs()
    walks = G.simulate_walks(num_walks=args.num_walks, walk_length=args.walk_length)
    learn_embeddings(walks, dimensions=args.dimensions, window_size=args.window_size, workers=args.workers, iter=args.iter, output=args.output)

if __name__ == "__main__":
    args = parse_args()
    main(args)
