from app import app
import multiprocessing

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    app.run(host="0.0.0.0", port=5000, debug=True)
