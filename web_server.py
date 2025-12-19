from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os

# Import necessary components from your BFS solver
from ai.cube_ai_state import CubeAIState
from core.cube_state import CubeState
from core.move_engine import CubeMoveEngine
from core.constants import FACE_NAMES, DEFAULT_FACE_COLOR
from visualization.renderer import render_cube_flat

app = Flask(__name__)
# Enable CORS for all origins, including chrome extensions
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

# Constants
MAX_BFS_DEPTH = 8  # Same as in run_cross_solver.py

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "message": "Rubik's Cube Cross Solver API is running!",
        "version": "1.0.0",
        "endpoints": {
            "solve": "/solve?scramble=<scramble_moves>",
            "example": "/solve?scramble=R U R' U'"
        }
    })

@app.route('/solve', methods=['GET'])
def solve_cross():
    try:
        scramble = request.args.get('scramble')
        if not scramble:
            return jsonify({"error": "No scramble provided"}), 400
        
        # 1. Create initial state (solved cube)
        cube = CubeState.solved()
        
        # 2. Apply scramble
        engine = CubeMoveEngine(cube)
        moves = scramble.strip().split()
        engine.apply_sequence(moves)
        
        print(f"\n[1] Applied Scramble: {scramble}")
        print(f"[2] Initial State (After Scramble):")
        print(render_cube_flat(cube))

        # Color name mapping
        color_name_by_code = {
            1: 'white',
            2: 'yellow', 
            3: 'green',
            4: 'blue',
            5: 'orange',
            6: 'red',
        }

        def face_label(face: int) -> str:
            face_letter = FACE_NAMES[face]
            color_code = int(DEFAULT_FACE_COLOR[face])
            color_name = color_name_by_code.get(color_code, str(color_code))
            return f"{face_letter}({color_name})"

        # 3. Try all 6 color crosses and find top 10 solutions
        print(f"\n[3] Finding top 10 cross solutions from all faces (Max Depth: {MAX_BFS_DEPTH})...")
        
        start_time = time.time()
        
        # Find existing shortest solution
        best_len, best = CubeAIState.find_best_cross_solutions(
            cube_state=cube,
            max_depth=MAX_BFS_DEPTH,
            include_white=True,
        )
        
        # Find additional top 10 solutions
        all_solutions = CubeAIState.find_multiple_cross_solutions(
            cube_state=cube,
            max_depth=MAX_BFS_DEPTH,
            max_solutions=10,
            include_white=True,
        )
        
        end_time = time.time()
        
        search_time = end_time - start_time
        print(f"\n[3] Search Complete (Time taken: {search_time:.4f} seconds)")

        if not best:
            return jsonify({
                "error": f"Failed to find any cross solution (max_depth={MAX_BFS_DEPTH})",
                "search_time": search_time
            }), 404

        # 4. Prepare results - top 10 solutions
        solutions = []
        
        # Add all solutions (face_id, length, moves format)
        for face, length, solution in all_solutions:
            solutions.append({
                "face": face_label(face),
                "face_number": face,
                "moves": solution,
                "move_count": length,
                "solution_string": ' '.join(solution),
                "is_optimal": length == best_len  # Mark if optimal solution
            })
        
        # If no optimal solution exists, add using existing method
        if not solutions:
            for face, solution in best:
                solutions.append({
                    "face": face_label(face),
                    "face_number": face,
                    "moves": solution,
                    "move_count": len(solution),
                    "solution_string": ' '.join(solution),
                    "is_optimal": True
                })

        # 5. 첫 번째(최단) 해답을 실제로 적용해서 검증
        chosen_face, chosen_solution = best[0]
        solved_cube = cube.copy()
        CubeMoveEngine(solved_cube).apply_sequence(chosen_solution)

        final_ai_state = CubeAIState.from_cube_state(solved_cube)
        verification_ok = final_ai_state.is_cross_solved(chosen_face)

        print(f"\n[4] Best cross length: {best_len}")
        for face, solution in best:
            print(f"- Best Face: {face_label(face)} | Solution (len={len(solution)}): {' '.join(solution)}")
        
        print(f"\n[4] Found {len(solutions)} total solutions")
        for i, sol in enumerate(solutions[:3]):  # Print only first 3
            print(f"- #{i+1}: {sol['face']} ({sol['move_count']} moves): {sol['solution_string']}")
        
        print(f"\n[5] Cross Verification Result (Face {face_label(chosen_face)}): {verification_ok}")
        print("✅ Success" if verification_ok else "❌ Failure")

        return jsonify({
            "success": True,
            "scramble": scramble,
            "search_time": search_time,
            "best_length": best_len,
            "total_solutions": len(solutions),
            "solutions": solutions,
            "verification": {
                "face": face_label(chosen_face),
                "passed": verification_ok
            }
        })
        
    except Exception as e:
        print(f"Error in solve_cross: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask server for Rubik's Cube Cross Solver...")
    print("Available endpoints:")
    print("  GET / - Health check")
    print("  GET /solve?scramble=<scramble_moves>")
    print("  Example: /solve?scramble=R%20U%20R%27%20U%27")
    
    # Production deployment configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    
    print(f"\nServer starting on port {port}")
    print(f"Debug mode: {'ON' if debug else 'OFF'}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
