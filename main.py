import tkinter as tk
from tkinter import messagebox
import math

class CircleDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Circle Drawing Challenge")

        # Constants
        self.WIDTH, self.HEIGHT = 600, 600
        self.CENTER = (self.WIDTH // 2, self.HEIGHT // 2)
        self.DOT_RADIUS = 3
        self.MIN_RADIUS = 40  # Minimum allowed radius for the ideal circle

        # Colors
        self.WHITE = "white"
        self.BLACK = "black"
        self.RED = "red"

        # Canvas setup
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg=self.WHITE)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Buttons and labels
        self.accuracy_label = tk.Label(root, text="Accuracy: 0%", font=("Helvetica", 12))
        self.accuracy_label.pack(pady=10)

        self.reset_button = tk.Button(root, text="See Best Attempt", command=self.see_best_attempt)
        self.reset_button.pack(pady=5)

        # Variables
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

    def draw_ideal_circle(self, radius):
        x, y = self.CENTER
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=self.RED)

    def draw_central_dot(self):
        x, y = self.CENTER
        self.canvas.create_oval(x - self.DOT_RADIUS, y - self.DOT_RADIUS,
                                 x + self.DOT_RADIUS, y + self.DOT_RADIUS,
                                 fill=self.BLACK, outline=self.BLACK)

    def update_accuracy_label(self, accuracy):
        self.accuracy_label.config(text=f"Accuracy: {accuracy:.2f}%")

    def start_drawing(self, event):
        self.drawing = True
        self.clear_canvas()

    def draw(self, event):
        if self.drawing:
            current_pos = (event.x, event.y)
            if self.user_points:
                prev_pos = self.user_points[-1]
                # Draw a line between the current and previous positions
                self.canvas.create_line(prev_pos[0], prev_pos[1], current_pos[0], current_pos[1],
                                        width=2, fill=self.BLACK, capstyle=tk.ROUND, smooth=tk.TRUE)
            else:
                self.user_points.append(current_pos)
            # Always add the current position to the list of points
            self.user_points.append(current_pos)

    def stop_drawing(self, event):
        self.drawing = False

        # Check if the central point is inside the drawn circle
        if all(math.dist(self.CENTER, point) >= self.DOT_RADIUS for point in self.user_points):
            # Calculate average radius
            average_radius = self.calculate_average_radius()

            # Check if the ideal circle's radius is below the minimum allowed
            if average_radius < self.MIN_RADIUS:
                self.flash_screen_red()
                messagebox.showinfo("Invalid Attempt", "The circle is too small. Please draw a larger circle.")
            else:
                # Check if the drawing is around the central point
                if self.check_circle_around_center():
                    # Calculate accuracy based on the similarity of the two circles
                    distance = math.dist(self.CENTER, self.user_points[-1])
                    accuracy = 100 * (1 - abs(average_radius - distance) / max(average_radius, distance))
                    self.update_accuracy_label(accuracy)

                    # Update best attempt if the current attempt is better
                    if accuracy > self.best_accuracy:
                        self.best_accuracy = accuracy
                        self.best_attempt_points = self.user_points.copy()

                    # Draw the ideal circle only if the attempt is valid
                    self.draw_ideal_circle(average_radius)
                else:
                    self.flash_screen_red()
                    messagebox.showinfo("Invalid Attempt", "The circle must be drawn around the central point.")
        else:
            self.flash_screen_red()
            messagebox.showinfo("Invalid Attempt", "The circle must be drawn around the central point.")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_central_dot()
        self.user_points = []
        self.accuracy_label.config(text="Accuracy: 0%")

    def see_best_attempt(self):
        if self.best_attempt_points:
            popup = tk.Toplevel(self.root)
            popup.title("Best Attempt")
            canvas = tk.Canvas(popup, width=self.WIDTH, height=self.HEIGHT, bg=self.WHITE)
            canvas.pack(expand=tk.YES, fill=tk.BOTH)

            # Draw central dot
            self.draw_central_dot()

            # Draw best attempt
            for point in self.best_attempt_points:
                canvas.create_oval(point[0] - self.DOT_RADIUS, point[1] - self.DOT_RADIUS,
                                    point[0] + self.DOT_RADIUS, point[1] + self.DOT_RADIUS,
                                    fill=self.BLACK, outline=self.BLACK)

            # Draw ideal circle only if the attempt is valid
            if self.check_circle_around_center():
                best_average_radius = self.calculate_average_radius()
                self.draw_ideal_circle_overlay(canvas, best_average_radius)

                # Display percentage accuracy
                distance = math.dist(self.CENTER, self.best_attempt_points[-1])
                best_accuracy = 100 * (1 - abs(best_average_radius - distance) / max(best_average_radius, distance))
                accuracy_label = tk.Label(popup, text=f"Accuracy: {best_accuracy:.2f}%", font=("Helvetica", 12))
                accuracy_label.pack(pady=10)

        else:
            messagebox.showinfo("No Best Attempt", "No best attempt available yet.")

    def draw_ideal_circle_overlay(self, canvas, radius):
        x, y = self.CENTER
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=self.RED)



    def flash_screen_red(self):
        # Flash the screen red momentarily
        original_bg_color = self.canvas["bg"]
        self.canvas["bg"] = self.RED
        self.root.after(500, lambda: self.canvas.configure(bg=original_bg_color))

    def check_circle_around_center(self):
        # Check if the central point is within the "fan-shaped" region formed by two adjacent points
        for i in range(len(self.user_points)):
            p1 = self.user_points[i]
            p2 = self.user_points[(i + 1) % len(self.user_points)]
            if self.central_point_in_fan_shape(p1, p2):
                return True
        return False

    def central_point_in_fan_shape(self, point1, point2):
        # Check if the central point is within the "fan-shaped" region formed by two points
        angle1 = math.atan2(point1[1] - self.CENTER[1], point1[0] - self.CENTER[0])
        angle2 = math.atan2(point2[1] - self.CENTER[1], point2[0] - self.CENTER[0])
        angle = math.atan2(self.CENTER[1] - point1[1], self.CENTER[0] - point1[0])
        return angle1 <= angle <= angle2 or angle2 <= angle <= angle1

if __name__ == "__main__":
    root = tk.Tk()
    app = CircleDrawingApp(root)
    root.mainloop()
