# main.py
import tkinter as tk
from detector import TargetDetector
from tracker import TargetTracker
from missile_sim import MissileLauncher
from gui_app import IronDomeGUI
from config import Config

def main():
    print("=" * 50)
    print("NEUROSHIELD AI")
    print("=" * 50)
    print("\nInitializing system...")
    
    # Initialize components
    config = Config()
    detector = TargetDetector()
    tracker = TargetTracker()
    launcher = MissileLauncher()
    
    # Create GUI
    root = tk.Tk()
    app = IronDomeGUI(root, detector, tracker, launcher, config)
    
    print("System ready!")
    print("\nInstructions:")
    print("1. Ensure the laptop webcam is active")
    print("2. Press 'Connect Camera' to begin")
    print("3. Press 'Start Tracking' to detect targets")
    print("4. Check 'Auto Fire' to enable automatic firing")
    print("=" * 50)
    
    # Run the application
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    root.mainloop()

if __name__ == "__main__":
    main()