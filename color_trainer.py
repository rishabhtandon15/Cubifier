import cv2
import numpy as np
import pickle
import os
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from collections import deque

class CubeSolver:
    def __init__(self):
        # Move definitions
        self.basic_moves = {
            'R': lambda cube: self._rotate_face(cube, 'right'),
            'L': lambda cube: self._rotate_face(cube, 'left'),
            'U': lambda cube: self._rotate_face(cube, 'up'),
            'D': lambda cube: self._rotate_face(cube, 'down'),
            'F': lambda cube: self._rotate_face(cube, 'front'),
            'B': lambda cube: self._rotate_face(cube, 'back')
        }
        
        # Movement patterns for common situations
        self.patterns = {
            'corner_swap': "R U R' U' R' F R2 U' R' U' R U R' F'",
            'edge_flip': "R U R' U' R' F R F'",
            'corner_rotation': "R U R' U R U2 R'"
        }
    
    def _rotate_face(self, cube_state, face):
        """Simulate rotation of a face"""
        state = cube_state.copy()
        idx_map = {
            'front': ([0,1,2], [3,4,5], [6,7,8]),
            'right': ([2,5,8], [1,4,7], [0,3,6]),
            'up': ([0,1,2], [3,4,5], [6,7,8]),
            'down': ([6,7,8], [3,4,5], [0,1,2]),
            'left': ([0,3,6], [1,4,7], [2,5,8]),
            'back': ([2,1,0], [5,4,3], [8,7,6])
        }
        
        indices = idx_map[face]
        # Perform rotation logic
        return state
    
    def find_solution(self, cube_state):
        """Find solution using IDA* search"""
        if self.is_solved(cube_state):
            return []
        
        max_depth = 20
        moves = []
        visited = set()
        
        def ida_star(state, depth, path):
            if depth == 0 and self.is_solved(state):
                return path
            if depth == 0:
                return None
                
            for move in self.basic_moves:
                new_state = self.basic_moves[move](state)
                state_hash = self.hash_state(new_state)
                
                if state_hash not in visited:
                    visited.add(state_hash)
                    result = ida_star(new_state, depth - 1, path + [move])
                    if result:
                        return result
                    visited.remove(state_hash)
            return None
        
        # Iteratively deepen search
        for depth in range(1, max_depth):
            visited.clear()
            solution = ida_star(cube_state, depth, [])
            if solution:
                return solution
        
        return None
    
    def hash_state(self, state):
        """Create a unique hash for a cube state"""
        return tuple(map(tuple, state))
    
    def is_solved(self, state):
        """Check if cube is solved"""
        for face in state:
            if not all(x == face[0] for x in face):
                return False
        return True

class CubeColorTrainer:
    def __init__(self):
        self.color_model = KNeighborsClassifier(n_neighbors=3)
        self.colors = {
            'white': [], 'yellow': [], 'red': [],
            'orange': [], 'blue': [], 'green': []
        }
        self.model_path = 'cube_color_model.pkl'
        self.solver = CubeSolver()
        self.current_cube_state = None
        
    def add_training_sample(self, color_name, hsv_values):
        """Add a color sample to the training data"""
        if color_name in self.colors:
            self.colors[color_name].append(hsv_values)
            
    def train_model(self):
        """Train the color recognition model"""
        X = []  # Features (HSV values)
        y = []  # Labels (color names)
        
        for color_name, samples in self.colors.items():
            for sample in samples:
                X.append(sample)
                y.append(color_name)
                
        if len(X) > 0:
            X = np.array(X)
            y = np.array(y)
            self.color_model.fit(X, y)
            
            # Save the trained model
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.color_model, f)
            
            return True
        return False
    
    def predict_color(self, hsv_values):
        """Predict the color of a given HSV value"""
        try:
            hsv_values = np.array(hsv_values).reshape(1, -1)
            return self.color_model.predict(hsv_values)[0]
        except:
            return None
    
    def load_model(self):
        """Load a previously trained model"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.color_model = pickle.load(f)
            return True
        return False
    
    def update_cube_state(self, face_colors):
        """Update the current cube state with new face colors"""
        if not self.current_cube_state:
            self.current_cube_state = []
        
        if len(self.current_cube_state) < 6:  # Not all faces scanned yet
            self.current_cube_state.append(face_colors)
            return len(self.current_cube_state)
        
        return -1  # All faces already scanned
    
    def get_solution_path(self):
        """Get solution path for current cube state"""
        if self.current_cube_state and len(self.current_cube_state) == 6:
            solution = self.solver.find_solution(self.current_cube_state)
            if solution:
                return self.optimize_solution(solution)
        return None
    
    def optimize_solution(self, solution):
        """Optimize the solution path by removing redundant moves"""
        optimized = []
        i = 0
        while i < len(solution):
            if i + 1 < len(solution) and solution[i] == solution[i + 1]:
                # Two same moves = half turn
                optimized.append(solution[i] + "2")
                i += 2
            elif (i + 2 < len(solution) and 
                  solution[i] == solution[i + 1] == solution[i + 2]):
                # Three same moves = inverse move
                optimized.append(solution[i] + "'")
                i += 3
            else:
                optimized.append(solution[i])
                i += 1
        return optimized

def get_dominant_color(image):
    """Extract the dominant color from an image region"""
    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 3)
    
    # Cluster the pixels
    kmeans = KMeans(n_clusters=1, n_init=10)
    kmeans.fit(pixels)
    
    # Get the dominant color
    dominant_color = kmeans.cluster_centers_[0]
    return dominant_color.astype(int)