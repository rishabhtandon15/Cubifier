import cv2
import numpy as np
from color_trainer import CubeColorTrainer, get_dominant_color

class CubeProcessor:
    def __init__(self):
        self.color_trainer = CubeColorTrainer()
        self.color_trainer.load_model()
        self.grid_size = 3
        self.face_colors = []
        self.current_face = 0
        self.solution_path = None
        
    def process_frame(self, frame):
        """Process a video frame to detect cube faces"""
        height, width = frame.shape[:2]
        cell_height = height // self.grid_size
        cell_width = width // self.grid_size
        
        # Convert frame to HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create grid overlay
        grid_frame = frame.copy()
        self.face_colors = []
        
        # Process each cell in the grid
        for i in range(self.grid_size):
            row_colors = []
            for j in range(self.grid_size):
                # Calculate cell boundaries
                x1 = j * cell_width
                y1 = i * cell_height
                x2 = (j + 1) * cell_width
                y2 = (i + 1) * cell_height
                
                # Extract cell region
                cell = hsv_frame[y1:y2, x1:x2]
                
                # Get dominant color
                dominant_color = get_dominant_color(cell)
                
                # Predict color name
                color_name = self.color_trainer.predict_color(dominant_color)
                
                # Draw cell rectangle
                cv2.rectangle(grid_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add text label
                if color_name:
                    cv2.putText(grid_frame, color_name, (x1 + 10, y1 + 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    row_colors.append(color_name)
                
            self.face_colors.append(row_colors)
        
        # Add face counter and instructions
        cv2.putText(grid_frame, f"Face {self.current_face + 1}/6", 
                   (10, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # If we have a solution, display it
        if self.solution_path:
            solution_text = " ".join(self.solution_path)
            cv2.putText(grid_frame, f"Solution: {solution_text}", 
                       (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return grid_frame
    
    def capture_face(self):
        """Capture the current face colors and update cube state"""
        if len(self.face_colors) == self.grid_size:
            face_num = self.color_trainer.update_cube_state(self.face_colors)
            if face_num == 6:  # All faces captured
                self.solution_path = self.color_trainer.get_solution_path()
                self.current_face = 0
                return True, "All faces captured. Solution found!"
            elif face_num > 0:
                self.current_face = face_num
                return True, f"Face {face_num} captured. Please show face {face_num + 1}"
        return False, "Invalid face detection"
    
    def reset_capture(self):
        """Reset the face capture process"""
        self.current_face = 0
        self.solution_path = None
        self.color_trainer.current_cube_state = None
        return "Capture reset. Please start with face 1"

    def calibrate_color(self, frame, color_name):
        """Calibrate a new color sample from the center of the frame"""
        height, width = frame.shape[:2]
        center_x = width // 2
        center_y = height // 2
        sample_size = 50
        
        # Extract center region
        x1 = center_x - sample_size // 2
        y1 = center_y - sample_size // 2
        x2 = center_x + sample_size // 2
        y2 = center_y + sample_size // 2
        
        center_region = frame[y1:y2, x1:x2]
        hsv_center = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
        
        # Get dominant color
        dominant_color = get_dominant_color(hsv_center)
        
        # Add to training data
        self.color_trainer.add_training_sample(color_name, dominant_color)
        
        return True