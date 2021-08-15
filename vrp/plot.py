import matplotlib.pyplot as plt

def plot_clusterization(clustered_clients, clients_coordinates, depots):
	colors = ['blue', 'green', 'red', 'darkviolet', 'darkorange', 'pink', 'maroon']
	color_index = 0

	for clustered_depot in enumerate(clustered_clients):
		color = colors[color_index]
		color_index += 1
		for client in clustered_depot:
			x,y = clients_coordinates[client]
			plt.plot(x,y, 'o', color=color, marker=".", markersize=8);

	color_index = 0
	for depot in depots:
		color = colors[color_index]
		color_index += 1
		plt.plot(depot.x,depot.y, color=color, marker="s", markersize=12);

	plt.show()

def plot_clusterization_with_line(clustered_clients, clients_coordinates, depots):
	colors = ['blue', 'green', 'red', 'darkviolet', 'darkorange', 'pink', 'maroon']
	index = 0

	for clustered_depot in clustered_clients:
		depot = depots[index]
		color = colors[index]
		index +=1

		for c in range(1, len(clustered_depot)):
			client = clustered_depot[c]
			x,y = clients_coordinates[client]
			#plt.plot(x,y, 'o', color=color, marker=".", markersize=8);
			xplot = (x, depot.x)
			yplot = (y, depot.y)
			plt.plot(xplot, yplot, color=color, marker="o", markersize=4);

	index = 0
	for depot in depots:
		color = colors[index]
		index +=1

		plt.plot(depot.x,depot.y, color=color, marker="s", markersize=10);

	plt.show()

def plot_mdvrptw_solution(mdvrptw_solution):
	colors = ['blue', 'green', 'red', 'darkviolet', 'darkorange', 'pink', 'maroon']
	mdvrptw = mdvrptw_solution.mdvrptw

	index = 0
	for vrptw_solution in mdvrptw_solution.vrptw_solutions:
		for route in vrptw_solution.routes:
			color = colors[index]

			for i in range(len(route) -1):
			#for client in route:
				client = route[i]                                      # local id created by vrptw instance
				real_client = mdvrptw_solution.clustered_clients[index][client] # real id from the mdvrptw problem
				x1,y1 = mdvrptw.coordinates[real_client]

				client = route[i+1]
				real_client = mdvrptw_solution.clustered_clients[index][client] # real id from the mdvrptw problem
				x2,y2 = mdvrptw.coordinates[real_client]

				xplot = (x1, x2)
				yplot = (y1, y2)
				plt.plot(xplot, yplot, color=color, marker="o", markersize=4);

		index +=1

	index = 0
	for depot in mdvrptw.depots:
		color = colors[index]
		index +=1

		plt.plot(depot.x,depot.y, color=color, marker="s", markersize=10);

	for i in range(1, mdvrptw.number_of_clients + mdvrptw.number_of_depots): #0 does not exist on mdvrptw
		x,y = mdvrptw.coordinates[i]
		plt.text(x,y , str(i), color='black', fontsize=12);


	plt.show()