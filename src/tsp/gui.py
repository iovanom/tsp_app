import math
import time
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from tsp.algorithms.constructive import cheapest_insertion, nearest_neighbor, three_opt, two_opt
from tsp.io.csv_reader import read_asymetric_matrix
from tsp.models.graph import AsymmetricGraph


class TSPGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TSP Solver")
        self.geometry("1200x800")

        # Variables
        self.csv_file = tk.StringVar()
        self.algorithm = tk.StringVar(value="nearest_neighbor")
        self.start = tk.IntVar(value=0)
        self.two_opt = tk.BooleanVar()
        self.two_opt_max_passes = tk.IntVar(value=100)
        self.two_opt_timeout = tk.DoubleVar()
        self.three_opt = tk.BooleanVar()
        self.three_opt_max_passes = tk.IntVar(value=100)
        self.three_opt_timeout = tk.DoubleVar()
        self.benchmark = tk.BooleanVar()
        self.runs = tk.IntVar(value=10)

        # Graph and table
        self.graph: Optional[AsymmetricGraph] = None
        self.table_entries: list[list[tk.Entry]] = []
        self.labels: list[str] = []

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Left frame for inputs
        input_frame = tk.Frame(self)
        input_frame.grid(row=0, column=0, sticky="n")

        # CSV File
        tk.Label(input_frame, text="CSV File:").grid(row=0, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.csv_file, width=30).grid(row=0, column=1)
        tk.Button(input_frame, text="Browse", command=self.browse_file).grid(row=0, column=2)
        tk.Button(input_frame, text="Load Table", command=self.load_table).grid(row=0, column=3)

        # Algorithm
        tk.Label(input_frame, text="Algorithm:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(
            input_frame,
            textvariable=self.algorithm,
            values=["nearest_neighbor", "cheapest_insertion"],
            width=15,
        ).grid(row=1, column=1)

        # Start
        tk.Label(input_frame, text="Start Node:").grid(row=2, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.start, width=5).grid(row=2, column=1)

        # 2-opt
        tk.Checkbutton(input_frame, text="2-opt", variable=self.two_opt).grid(
            row=3, column=0, sticky="w"
        )
        tk.Label(input_frame, text="Max Passes:").grid(row=4, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.two_opt_max_passes, width=5).grid(row=4, column=1)
        tk.Label(input_frame, text="Timeout (s):").grid(row=5, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.two_opt_timeout, width=5).grid(row=5, column=1)

        # 3-opt
        tk.Checkbutton(input_frame, text="3-opt", variable=self.three_opt).grid(
            row=6, column=0, sticky="w"
        )
        tk.Label(input_frame, text="Max Passes:").grid(row=7, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.three_opt_max_passes, width=5).grid(row=7, column=1)
        tk.Label(input_frame, text="Timeout (s):").grid(row=8, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.three_opt_timeout, width=5).grid(row=8, column=1)

        # Benchmark
        tk.Checkbutton(input_frame, text="Benchmark", variable=self.benchmark).grid(
            row=9, column=0, sticky="w"
        )
        tk.Label(input_frame, text="Runs:").grid(row=10, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.runs, width=5).grid(row=10, column=1)

        # Run
        tk.Button(input_frame, text="Run", command=self.run_tsp).grid(
            row=11, column=0, columnspan=4
        )

        # Table frame
        self.table_frame = tk.Frame(self)
        self.table_frame.grid(row=0, column=1, sticky="n")

        # Results
        self.result_text = tk.Text(self, height=10, width=80)
        self.result_text.grid(row=1, column=0, columnspan=2)

        # Plot
        if MATPLOTLIB_AVAILABLE:
            self.figure = plt.Figure(figsize=(5, 4), dpi=100)
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self)
            self.canvas.get_tk_widget().grid(row=0, column=2, sticky="n")
        else:
            tk.Label(self, text="Matplotlib not available for plotting").grid(row=0, column=2)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file:
            self.csv_file.set(file)

    def load_table(self):
        try:
            self.graph = read_asymetric_matrix(self.csv_file.get())
            self.labels = self.graph.labels
            self.create_table()
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error loading table: {e}")

    def create_table(self):
        if self.graph is None:
            return
        # Clear existing table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.table_entries = []

        n = self.graph.n
        # Headers
        tk.Label(self.table_frame, text="", width=5).grid(row=0, column=0)  # Corner
        for j in range(n):
            tk.Label(self.table_frame, text=self.labels[j], width=5).grid(row=0, column=j + 1)
        for i in range(n):
            tk.Label(self.table_frame, text=self.labels[i], width=5).grid(row=i + 1, column=0)
            row_entries = []
            for j in range(n):
                entry = tk.Entry(self.table_frame, width=5)
                if i == j:
                    entry.insert(0, "inf")
                    entry.config(state="disabled")
                else:
                    entry.insert(0, str(self.graph.c(i, j)))
                entry.grid(row=i + 1, column=j + 1)
                row_entries.append(entry)
            self.table_entries.append(row_entries)

    def get_graph_from_table(self) -> AsymmetricGraph:
        if not self.table_entries:
            raise ValueError("Table not loaded")
        n = len(self.table_entries)
        cost_matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(float("inf"))
                else:
                    val = self.table_entries[i][j].get().strip()
                    if val in ["", "inf", "NA"]:
                        row.append(float("inf"))
                    else:
                        row.append(float(val))
            cost_matrix.append(row)
        return AsymmetricGraph(cost_matrix, self.labels)

    def run_tsp(self):
        try:
            if self.table_entries:
                graph = self.get_graph_from_table()
            else:
                graph = read_asymetric_matrix(self.csv_file.get())
            algos = {"nearest_neighbor": nearest_neighbor, "cheapest_insertion": cheapest_insertion}

            def get_tour_cost(start):
                tour, cost = algos[self.algorithm.get()](graph, start)
                if self.two_opt.get():
                    timeout = self.two_opt_timeout.get() if self.two_opt_timeout.get() > 0 else None
                    tour, cost = two_opt(
                        graph, tour, max_passes=self.two_opt_max_passes.get(), timeout=timeout
                    )
                if self.three_opt.get():
                    timeout = (
                        self.three_opt_timeout.get() if self.three_opt_timeout.get() > 0 else None
                    )
                    tour, cost = three_opt(
                        graph, tour, max_passes=self.three_opt_max_passes.get(), timeout=timeout
                    )
                return tour, cost

            if self.benchmark.get():
                costs = []
                times = []
                tour = []
                for _ in range(self.runs.get()):
                    start_time = time.time()
                    tour, cost = get_tour_cost(self.start.get())
                    end_time = time.time()
                    costs.append(cost)
                    times.append(end_time - start_time)
                algo_name = f"{self.algorithm.get()}{' + 2-opt' if self.two_opt.get() else ''}{' + 3-opt' if self.three_opt.get() else ''}"
                avg_cost = sum(costs) / len(costs)
                avg_time = sum(times) / len(times)
                result = (
                    f"Algorithm: {algo_name}\nRuns: {self.runs.get()}\n"
                    f"Cost - Min: {min(costs):.2f}, Max: {max(costs):.2f}, Avg: {avg_cost:.2f}\n"
                    f"Time - Min: {min(times):.4f}s, Max: {max(times):.4f}s, Avg: {avg_time:.4f}s"
                )
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, result)
                self.plot_tour(graph, tour)
            else:
                tour, cost = get_tour_cost(self.start.get())
                tour_labels = [graph.labels[i] for i in tour]
                result = f"Tour: {tour_labels}\nCost: {cost}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, result)
                self.plot_tour(graph, tour)
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error: {e}")

    def plot_tour(self, graph, tour):
        if not MATPLOTLIB_AVAILABLE:
            return
        self.ax.clear()
        n = graph.n
        angles = [2 * math.pi * i / n for i in range(n)]
        x = [math.cos(a) for a in angles]
        y = [math.sin(a) for a in angles]
        self.ax.scatter(x, y, c='blue')
        for i, label in enumerate(graph.labels):
            self.ax.text(x[i], y[i], label, fontsize=12, ha='center', va='center')
        tour_x = [x[i] for i in tour] + [x[tour[0]]]
        tour_y = [y[i] for i in tour] + [y[tour[0]]]
        self.ax.plot(tour_x, tour_y, 'r-')
        self.canvas.draw()


def main():
    app = TSPGUI()
    app.mainloop()
