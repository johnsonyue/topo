import sys
import re

import matplotlib
matplotlib.use("Agg");
import matplotlib.pyplot as plt
import networkx as nx
from networkx import graphviz_layout


class node:
	def __init__(self,ip):
		self.addr = ip;
		self.child = [];
class dag:
	def __init__(self, root):
		self.node = [];
		self.dict = {};
		
		#add root.
		self.num_edges = 0;
		self.num_nodes = 1;
		self.prev_index = -1;

		r = node(root);
		self.node.append(r);
		self.dict[root] = 0;

	def parse_trace(self, trace):
		if re.findall("#",trace):
			return False;

		hops = trace.strip().split('\t');
		for i in range(13,len(hops)):
			self.parse_hop(hops[i]);
		return True;

	def is_child(self, pind, cind):
		for c in self.node[pind].child:
			if c == cind:
				return True;
	
		return False;

	def parse_hop(self, hop):
		if hop == "q":
			self.prev_index = -1;
			return;

		list = hop.split(';');
		for tuple in list:
			addr = (tuple.split(','))[0];
			if not self.dict.has_key(addr):
				self.node.append(node(addr));
				self.dict[addr] = self.num_nodes;
				if self.prev_index != -1:
					self.node[self.prev_index].child.append(self.num_nodes);
					self.num_edges = self.num_edges + 1;

				self.prev_index = self.num_nodes;
				self.num_nodes = self.num_nodes + 1;
			else:
				child_index = self.dict[addr];
				if self.prev_index != -1 and not self.is_child(self.prev_index, child_index):
					self.node[self.prev_index].child.append(child_index);
					self.num_edges = self.num_edges + 1;
				self.prev_index = child_index;
	def build(self, file):
		f = open(file, 'r');
		for line in f.readlines():
			self.prev_index = 0;
			self.parse_trace(line);
		f.close();
	def disp_stats(self):
		print "total nodes:",len(self.node);
		print "total edges:",self.num_edges;

	
	def draw(self):
		graph = nx.Graph();

		for i in range(len(self.node)-1,-1,-1):
			graph.add_node(i);
			for c in self.node[i].child:
				graph.add_edge(i,c);
		
		graph0 = sorted(nx.connected_component_subgraphs(graph), key = len, reverse=True)[0];		
		

		plt.figure(figsize=(8,8));
		layout = nx.graphviz_layout(graph0,prog="twopi",root=0);
		nx.draw(graph0,layout,with_labels = False,alpha=0.5,node_size=15);
		xmax = 1.02*max(xx for xx,yy in layout.values());
		ymax = 1.02*max(yy for xx,yy in layout.values());
		plt.savefig("save.png");

		
def get_src(file_name):
	f = open(file_name,'r');
	for line in f.readlines():
		if re.findall("#",line):
			continue;
		list = line.strip().split('\t');
		src = list[1];
		f.close();
		return src;

def main(argv):
	if len(argv) != 2:
		print "usage:python merge.py <dump_file_name>";
		return;

	topo = dag(get_src(argv[1]));
	topo.build(argv[1]);
	topo.disp_stats();
	topo.draw();

if __name__ == "__main__":
	main(sys.argv);
