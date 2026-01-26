# AI Generated Image Detection Feature Plan

## Overview
This feature aims to detect whether an uploaded image is AI-generated or real using a machine learning model.

## Required Files & Locations

### Backend
1.  **Service Logic**: `backend/services/image_detection_service.py`
    *   Handles image loading, preprocessing, and model inference.
2.  **Route Handler**: `backend/app.py` (Update existing file)
    *   Add `/image-check` route to handle image uploads and return results.
3.  **Model Storage**: `backend/model/`
    *   Store pre-trained model weights here (e.g., `image_detector.h5`, `model.pth`).
4.  **Uploads Directory**: `backend/uploads/`
    *   Temporary storage for uploaded images during processing.

### Frontend
1.  **Template**: `backend/templates/image_detection.html`
    *   User interface for uploading images and displaying results.
2.  **Static Assets** (if needed): `frontend/css/style.css` (Update existing)

## Project Structure Update
The `backend` directory structure will look like this:
```text
backend/
├── app.py
├── ...
├── services/
│   ├── ...
│   └── image_detection_service.py  <-- [NEW]
├── templates/
│   ├── ...
│   └── image_detection.html        <-- [NEW]
├── model/
│   ├── ...
│   └── image_detector.h5           <-- [NEW] (Model weights)
└── uploads/                        <-- [NEW] (Temp storage)
```

## To-Do Task List
- [ ] **Setup Directory Structure**
    - [ ] Create `backend/uploads/` folder.
    - [ ] Ensure `backend/model/` exists (it does).
- [ ] **Update .gitignore**
    - [ ] Add `backend/uploads/` to ignore uploaded files.
    - [ ] Add `*.h5`, `*.pth`, `*.onnx` (model weights) to ignore large files.
- [ ] **Backend Implementation**
    - [ ] Create `backend/services/image_detection_service.py` with placeholder or model loading logic.
    - [ ] Update `backend/app.py` to add the `/image-check` route using `image_detection_service`.
- [ ] **Frontend Implementation**
    - [ ] Create `backend/templates/image_detection.html` with an upload form.
    - [ ] Add a link to the new tool in `frontend/pages/index.html` (or other navigation menus).
- [ ] **Dependencies**
    - [ ] Add necessary libraries (e.g., `tensorflow`, `torch`, `Pillow`, `numpy`) to `requirements.txt`.
