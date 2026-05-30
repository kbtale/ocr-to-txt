import os
import sys

# Add the src directory to the path (insert at front to prefer local package)
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import and run the main function
from main import main

if __name__ == "__main__":
    main()
