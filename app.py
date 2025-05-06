from flask import Flask, render_template, request
import os
import cv2
import torch
import requests
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['OUTPUT_FOLDER'] = 'static/output/'
API_KEY = "AIzaSyDcmGt12GtuxbDbyKHWg0gqKXWhpUgalHQ"  # Replace with a valid YouTube API key

# Load YOLOv5 model safely
try:
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
except Exception as e:
    print("Error loading YOLO model:", e)
    model = None  # Avoid crashes if the model fails to load

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def process_video(video_path, output_path, detection_type):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    detected_images = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if model is not None:
            results = model(frame)
            detections = results.xyxy[0].tolist()

            for *xyxy, conf, cls in detections:
                x1, y1, x2, y2 = map(int, xyxy)
                label = model.names[int(cls)]

                if detection_type == "fall" and label == "person":
                    if (y2 - y1) < (height * 0.3):  # Detect small person indicating a fall
                        cv2.putText(frame, "Fall Detected", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # Save detected frame
            detected_img_path = os.path.join(app.config['OUTPUT_FOLDER'], f"detected_{uuid.uuid4().hex[:6]}.jpg")
            cv2.imwrite(detected_img_path, frame)
            detected_images.append(detected_img_path)
        
        out.write(frame)

    cap.release()
    out.release()
    return detected_images

def fetch_youtube_videos(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses
        data = response.json()
        return [
            {
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            }
            for item in data.get("items", [])
        ]
    except requests.exceptions.RequestException as e:
        print("YouTube API request failed:", e)
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        detection_type = request.form.get('detection_type', 'object')

        if file:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'processed_{filename}')

            file.save(file_path)
            detected_images = process_video(file_path, output_path, detection_type)

            return render_template('index.html', output_video=output_path, detected_images=detected_images)

    return render_template('index.html')

@app.route('/youtube', methods=['GET'])
def youtube_search():
    query = request.args.get('query', 'fall detection')
    videos = fetch_youtube_videos(query)
    return render_template('index.html', videos=videos)

if __name__ == '__main__':
    app.run(debug=True)
