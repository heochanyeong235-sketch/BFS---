# Rubik's Cube Cross Solver

A high-performance Rubik's Cube cross solver using BFS (Breadth-First Search) algorithm with web integration capabilities.

## 🎯 Features

- **Advanced Cross Solving**: Finds optimal cross solutions for all 6 faces using BFS algorithm
- **Multi-Solution Support**: Discovers up to 10 different cross solutions per scramble
- **Web Integration**: RESTful API server for browser-based cube timers
- **csTimer Compatible**: Includes browser extension/Tampermonkey script for csTimer.net integration
- **Visual Feedback**: Built-in cube state visualization and solution verification
- **Performance Optimized**: Efficient state representation with fast move execution

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd BFS-완성
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Web Server (Production)
Start the Flask server for web integration:
```bash
python web_server.py
```

The server will start on `http://localhost:5000` with the following endpoint:
- `GET /solve?scramble=<scramble_moves>` - Returns cross solutions for given scramble

**Example:**
```
GET /solve?scramble=U' B2 F2 R2 U2 L' R2 D2 L' B2 D2 U L2 F L' R' B' U R2
```

### Command Line Interface
Run the cross solver directly:
```bash
python examples/run_cross_solver.py
```

### GUI Visualizer
Launch the interactive cube visualizer:
```bash
python examples/run_visualizer.py
```

### csTimer Integration
For **csTimer.net** users, install the Tampermonkey script:

1. Download Chrome extension folder
2. Open `chrome://extentions/`
3. Load the downloaded the folder 
4. Go to Cstimer
5. Cick the button Solve scrambles - cross solutions appear automatically!

## 🏗️ Project Structure

```
├── core/                   # Core cube logic
│   ├── cube_state.py      # 6x3x3 sticker representation
│   ├── move_engine.py     # Move execution engine
│   └── constants.py       # Face mappings and colors
├── ai/                     # BFS solver implementation
│   ├── cube_ai_state.py   # AI-optimized state representation
│   └── bfs_solver.py      # Cross solving algorithms
├── conversion/             # State conversion utilities
│   └── cube_to_ai.py      # Convert between representations
├── visualization/          # Rendering and display
│   ├── renderer.py        # Flat net cube renderer
│   └── tk_visualizer.py   # Interactive GUI
├── chrome_extension/       # Browser integration
│   ├── content.js         # Tampermonkey script
│   └── manifest.json      # Extension manifest
├── utils/                  # Utility functions
│   └── scramble.py        # Random scramble generation
├── examples/               # Demo scripts
├── tests/                  # Unit tests
└── web_server.py          # Flask API server
```

## 🔧 API Reference

### Solve Cross Endpoint
**GET** `/solve`

**Parameters:**
- `scramble` (string, required): Space-separated move sequence

**Response:**
```json
{
  "success": true,
  "scramble": "R U R' U'",
  "search_time": 0.0234,
  "best_length": 4,
  "total_solutions": 6,
  "solutions": [
    {
      "face": "U(white)",
      "face_number": 0,
      "moves": ["R", "U'", "R'", "U"],
      "move_count": 4,
      "solution_string": "R U' R' U",
      "is_optimal": true
    }
  ],
  "verification": {
    "face": "U(white)",
    "passed": true
  }
}
```

## 🧪 Testing

Run the test suite:
```bash
python -m unittest -q
```

Test specific components:
```bash
python -m unittest tests.test_bfssolver -v
```

## 🔬 Algorithm Details

- **BFS Implementation**: Guarantees optimal solutions (shortest move count)
- **State Representation**: Efficient cube encoding for fast processing  
- **Search Optimization**: Pruned search space using cross-specific heuristics
- **Multi-Face Solving**: Evaluates all 6 possible cross colors simultaneously

## 🌐 Deployment

### Render.com Deployment
1. Connect your GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python web_server.py`
4. Configure environment variables if needed

### Environment Variables
- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Set to 'production' for deployment

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙋‍♂️ Support

For questions or issues:
- Open an issue on GitHub
- Check existing documentation in `docs/` folder

---

*Built for the global speedcubing community* 🧩
