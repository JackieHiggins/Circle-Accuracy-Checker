import tkinter as tk
from tkinter import messagebox
import math
import numpy as np

class CircleDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Circle Drawing Challenge")

        # Constants
        self.WIDTH, self.HEIGHT = 600, 600
        self.CENTER = (self.WIDTH // 2, self.HEIGHT // 2)
        self.DOT_RADIUS = 2  # Smaller radius for smoother appearance
        self.MIN_RADIUS = 70  # Minimum allowed radius for the ideal circle
        self.CLOSE_ENOUGH_THRESHOLD = 60  # Distance threshold to consider ends close enough

        # Colors
        self.WHITE = "white"
        self.BLACK = "black"
        self.RED = "red"

        # Canvas setup
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg=self.BLACK)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Labels
        self.accuracy_label = tk.Label(root, text="0.0%", font=("Helvetica", 10), fg=self.WHITE, bg=self.BLACK)
        self.accuracy_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.best_accuracy_label = tk.Label(root, text="Best: 0.0%", font=("Helvetica", 10), fg=self.WHITE, bg=self.BLACK)
        self.best_accuracy_label.place(relx=0.5, rely=0.55, anchor=tk.S)

        self.reset_button = tk.Button(root, text="See Best Attempt", command=self.see_best_attempt)
        self.reset_button.pack(pady=10)

        self.drawing = False
        self.user_points = []
        self.best_accuracy = 0
        self.best_attempt_points = []

        # Draw central dot
        self.draw_central_dot()

        # Events
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def calculate_average_radius(self):
        total_radius = sum(math.dist(self.CENTER, point) for point in self.user_points)
        return total_radius / len(self.user_points) if len(self.user_points) > 0 else 0

    def calculate_standard_deviation(self, radii):
        return np.std(radii)

    def draw_central_dot(self):
        x, y = self.CENTER
        self.canvas.create_oval(x - self.DOT_RADIUS * 3, y - self.DOT_RADIUS * 3,
                                x + self.DOT_RADIUS * 3, y + self.DOT_RADIUS * 3,
                                fill=self.WHITE, outline=self.WHITE)

    def update_accuracy_label(self, accuracy):
        integer_part = int(accuracy)
        decimal_part = int((accuracy - integer_part) * 10)
        color = self.get_color(accuracy)
        self.accuracy_label.config(text=f"{integer_part}.{decimal_part}%", fg=color)

    def start_drawing(self, event):
        self.drawing = True
        self.clear_canvas()

    def draw(self, event):
        if self.drawing:
            current_pos = (event.x, event.y)
            self.user_points.append(current_pos)
            if len(self.user_points) > 1:
                accuracy = self.calculate_accuracy()
                color = self.get_color(accuracy)
                self.canvas.create_line(self.user_points[-2][0], self.user_points[-2][1], 
                                        current_pos[0], current_pos[1], 
                                        fill=color, width=2)
            self.update_live_accuracy()

    def update_live_accuracy(self):
        if len(self.user_points) > 1:
            average_radius = self.calculate_average_radius()
            radii = [math.dist(self.CENTER, point) for point in self.user_points]
            std_deviation = self.calculate_standard_deviation(radii)

            if average_radius >= self.MIN_RADIUS:
                ideal_radius = self.calculate_average_radius()
                average_distance = np.mean([abs(ideal_radius - r) for r in radii])
                accuracy = max(0, 100 - (average_distance + std_deviation))
                self.update_accuracy_label(accuracy)

    def stop_drawing(self, event):
        self.drawing = False

        if len(self.user_points) > 1:
            if self.is_circle_complete():
                average_radius = self.calculate_average_radius()
                radii = [math.dist(self.CENTER, point) for point in self.user_points]
                std_deviation = self.calculate_standard_deviation(radii)

                if average_radius < self.MIN_RADIUS:
                    messagebox.showinfo("Invalid Attempt", "The circle is too small. Please draw a larger circle.")
                    self.clear_canvas()
                else:
                    ideal_radius = self.calculate_average_radius()
                    average_distance = np.mean([abs(ideal_radius - r) for r in radii])
                    accuracy = max(0, 100 - (average_distance + std_deviation))
                    self.update_accuracy_label(accuracy)

                    if accuracy > self.best_accuracy:
                        self.best_accuracy = accuracy
                        self.best_attempt_points = self.user_points.copy()
                        self.best_accuracy_label.config(text=f"Best: {accuracy:.1f}%")

            else:
                messagebox.showinfo("Invalid Attempt", "The circle is incomplete. Please draw a complete circle.")
                self.clear_canvas()
        else:
            messagebox.showinfo("Invalid Attempt", "Please draw a complete circle.")
            self.clear_canvas()

    def is_circle_complete(self):
        start_point = self.user_points[0]
        end_point = self.user_points[-1]
        distance = math.dist(start_point, end_point)

        return distance <= self.CLOSE_ENOUGH_THRESHOLD

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_central_dot()
        self.user_points = []
        self.accuracy_label.config(text="0.0%")

    def see_best_attempt(self):
        if self.best_attempt_points:
            popup = tk.Toplevel(self.root)
            popup.title("Best Attempt")
            canvas = tk.Canvas(popup, width=self.WIDTH, height=self.HEIGHT, bg=self.BLACK)
            canvas.pack(expand=tk.YES, fill=tk.BOTH)

            # Draw central dot
            self.draw_central_dot_on_canvas(canvas)

            for i in range(len(self.best_attempt_points) - 1):
                canvas.create_line(self.best_attempt_points[i][0], self.best_attempt_points[i][1], 
                                   self.best_attempt_points[i + 1][0], self.best_attempt_points[i + 1][1], 
                                   fill=self.WHITE, width=2)

            radii = [math.dist(self.CENTER, point) for point in self.best_attempt_points]
            std_deviation = self.calculate_standard_deviation(radii)
            average_distance = np.mean([abs(self.calculate_average_radius() - r) for r in radii])
            best_accuracy = max(0, 100 - (average_distance + std_deviation))
            accuracy_label = tk.Label(popup, text=f"Accuracy: {best_accuracy:.1f}%", font=("Helvetica", 12), fg=self.WHITE, bg=self.BLACK)
            accuracy_label.pack(pady=10)
        else:
            messagebox.showinfo("No Best Attempt", "No best attempt available yet.")

    def draw_central_dot_on_canvas(self, canvas):
        x, y = self.CENTER
        canvas.create_oval(x - self.DOT_RADIUS * 3, y - self.DOT_RADIUS * 3,
                           x + self.DOT_RADIUS * 3, y + self.DOT_RADIUS * 3,
                           fill=self.WHITE, outline=self.WHITE)



    def calculate_accuracy(self):
        if len(self.user_points) < 2:
            return 0
        average_radius = self.calculate_average_radius()
        radii = [math.dist(self.CENTER, point) for point in self.user_points]
        std_deviation = self.calculate_standard_deviation(radii)
        ideal_radius = self.calculate_average_radius()
        average_distance = np.mean([abs(ideal_radius - r) for r in radii])
        accuracy = max(0, 100 - (average_distance + std_deviation))
        return accuracy

    def get_color(self, accuracy):
        # Define custom color gradient between red and green
        colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0)     # Green
        ]

        # Define the ranges for the color transition
        ranges = [60, 80, 90, 100]

        # Interpolate between colors based on the accuracy value
        if accuracy <= ranges[0]:
            return "#%02x%02x%02x" % colors[0]
        elif accuracy <= ranges[1]:
            ratio = (accuracy - ranges[0]) / (ranges[1] - ranges[0])
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            return "#%02x%02x%02x" % (r, g, b)
        elif accuracy <= ranges[2]:
            ratio = (accuracy - ranges[1]) / (ranges[2] - ranges[1])
            r = int(colors[1][0] * (1 - ratio) + colors[2][0] * ratio)
            g = int(colors[1][1] * (1 - ratio) + colors[2][1] * ratio)
            b = int(colors[1][2] * (1 - ratio) + colors[2][2] * ratio)
            return "#%02x%02x%02x" % (r, g, b)
        elif accuracy <= ranges[3]:
            ratio = (accuracy - ranges[2]) / (ranges[3] - ranges[2])
            r = int(colors[2][0] * (1 - ratio) + colors[3][0] * ratio)
            g = int(colors[2][1] * (1 - ratio) + colors[3][1] * ratio)
            b = int(colors[2][2] * (1 - ratio) + colors[3][2] * ratio)
            return "#%02x%02x%02x" % (r, g, b)
        else:
            return "#%02x%02x%02x" % colors[3]



if __name__ == "__main__":
    root = tk.Tk()
    app = CircleDrawingApp(root)
    root.mainloop()
