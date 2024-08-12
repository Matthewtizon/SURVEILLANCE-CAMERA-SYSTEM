try:
    import face_recognition
    print("face_recognition imported successfully!")
except ImportError as e:
    print(f"ImportError: {e}")

try:
    import face_recognition_models
    print("face_recognition_models imported successfully!")
except ImportError as e:
    print(f"ImportError: {e}")
