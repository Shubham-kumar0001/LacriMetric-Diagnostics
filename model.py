def get_model():
    try:
        from tensorflow.keras.models import load_model
        return load_model("model.h5")
    except:
        return None

def predict_eye_condition(model, image):
    """
    Step 4: CNN Prediction & Output Logic
    """
    if model is None or image is None or len(image) == 0:
        return "Normal", 0.5 # Default neutral if no frames caught
        
    try:
        import numpy as np
        prediction = model.predict(image, verbose=0)
        # Average the probability across all valid frames recorded in the blink interval
        prob = float(np.mean(prediction))
        if prob > 0.5:
            return "Abnormal", prob
        else:
            return "Normal", prob
    except Exception as e:
        print("Prediction Error:", e)
        return "Normal", 0.5
