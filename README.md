# LacriMetric Diagnostics

An AI-based system for automated tear film analysis, blink detection, and basic medical recommendation.

## Features
- **Flexible Input**: Upload pre-recorded eye videos or use your Live Webcam.
- **Blink Detection**: Accurately detects eye blinks and calculates blink rates per minute using OpenCV and MediaPipe Face Mesh.
- **Tear Film Analysis**: Employs a Convolutional Neural Network (TensorFlow/Keras) architecture to assess eye crops and estimate tear film conditions.
- **Decision Engine**: Rule-based medical formulation that combines CNN inference with blink rates to provide intuitive, "doctor-like" recommendations.
- **Premium UI**: Clean, responsive, glass-morphism interface modeled for medical applications.

## Folder Structure

```
LacriMetric Diagnostics/
│
├── app.py                   # Main Flask backend server
├── camera.py                # Computer vision logic (MediaPipe & OpenCV) 
├── model.py                 # TensorFlow/Keras CNN model architecture
├── requirements.txt         # Project dependencies
│
├── templates/
│   └── index.html           # Main UI template
│
└── static/
    ├── css/
    │   └── style.css        # Premium styling
    └── js/
        └── script.js        # Frontend interactions & API calls
```

## Setup & Run Instructions

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Create a Virtual Environment (Optional but Recommended)
Open your terminal and navigate to the `LacriMetric Diagnostics` folder, then run:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the Flask application server:
```bash
python app.py
```

### 5. Access the Web App
Open your web browser and navigate to:
**http://127.0.0.1:5000**

## Disclaimer regarding CNN Module
> [!IMPORTANT]
> The Convolutional Neural Network provided in `model.py` is fully architected per the specifications (Conv2D -> ReLU -> MaxPooling -> Dense -> Sigmoid). However, it is an **untrained prototype**. It will currently output pseudo-random predictions (~50%) to demonstrate pipeline functionality.
> 
> To use this system for real diagnoses, you MUST script a training pipeline over a verified medical dataset of Normal/Abnormal tear films, save the trained `.h5` model weights, and modify `model.py` to use `model.load_weights("your_weights.h5")`.

*Disclaimer: This system is for preliminary screening only and not a substitute for professional medical diagnosis.*
