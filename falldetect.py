import cv2
import torch

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov7', 'yolov5s')  # Load the YOLOv5 small model

# Function to detect falls
def detect_falls(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    fall_detected = False

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform inference
        results = model(frame)

        # Process results
        detections = results.xyxy[0]  # Get detections
        for *xyxy, conf, cls in detections:
            if int(cls) == 0:  # Class 0 is 'person'
                x1, y1, x2, y2 = map(int, xyxy)  # Get bounding box coordinates
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw bounding box

                # Check for fall detection logic (simplified)
                if (y2 - y1) > 100:  # Example condition for fall detection
                    fall_detected = True
                    cv2.putText(frame, "Fall Detected!", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Write the processed frame to the output video
        out.write(frame)

    cap.release()
    out.release()  # Release the video writer

# Run fall detection on the uploaded video
video_path = '/content/drive/MyDrive/gdrive/TheCodingBug/yolov7/kkk.mp4'  # Replace with your video file name
output_path = '/content/drive/MyDrive/gdrive/TheCodingBug/yolov7/output_fall_detection.mp4'  # Output video file name
detect_falls(video_path, output_path)

print(f"Processed video saved as: {output_path}")   