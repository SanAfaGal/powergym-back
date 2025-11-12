# Face Recognition System

This guide explains the face recognition system in PowerGym, including setup, usage, API endpoints, and best practices.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [InsightFace Model](#insightface-model)
- [Face Embeddings](#face-embeddings)
- [Database Storage](#database-storage)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)

## Overview

The PowerGym face recognition system uses **InsightFace** to provide secure, fast, and accurate facial recognition for gym member check-in. The system:

- Extracts 512-dimensional face embeddings from images
- Stores embeddings in PostgreSQL using pgvector extension
- Performs fast similarity searches for authentication
- Supports real-time face recognition for attendance tracking

### Key Features

- **Fast Recognition**: Vector similarity search using pgvector
- **Secure Storage**: Encrypted thumbnails, vector embeddings for search
- **High Accuracy**: InsightFace buffalo_s model (state-of-the-art)
- **Scalable**: Efficient database storage and indexing
- **Privacy**: Only face embeddings stored, not full images

## Architecture

### Components

1. **EmbeddingService** (`app/services/face_recognition/embedding.py`)
   - Extracts face embeddings from images
   - Compares embeddings for similarity
   - Uses InsightFace for face detection and encoding

2. **FaceDatabase** (`app/services/face_recognition/database.py`)
   - Stores and retrieves face biometrics
   - Handles encryption of thumbnails
   - Manages vector similarity searches

3. **FaceRecognitionService** (`app/services/face_recognition/core.py`)
   - Orchestrates face recognition operations
   - Handles registration and authentication workflows
   - Manages business logic

4. **API Endpoints** (`app/api/v1/endpoints/face_recognition.py`)
   - REST API for face operations
   - Request validation and response formatting

### Data Flow

```
Image (Base64) 
  → Image Processing
  → Face Detection (InsightFace)
  → Embedding Extraction (512-dim vector)
  → Storage (PostgreSQL + pgvector)
  → Similarity Search (for authentication)
```

## InsightFace Model

### Model Selection

The system uses **InsightFace buffalo_s** model by default:

- **buffalo_s**: Smaller, faster, recommended for most use cases
- **buffalo_l**: Larger, more accurate, requires more resources

### Model Download

The model is **automatically downloaded** on first use:

1. First API call triggers model download
2. Model stored in: `~/.insightface/models/` (or `/root/.insightface/models/` in Docker)
3. Subsequent requests use cached model

### Model Configuration

Configure in `.env`:

```env
INSIGHTFACE_MODEL=buffalo_s
INSIGHTFACE_DET_SIZE=640
INSIGHTFACE_CTX_ID=-1  # -1 for CPU, 0+ for GPU
```

### GPU Support

For GPU acceleration:

1. **Install CUDA** and cuDNN
2. **Install ONNX Runtime GPU**:
   ```bash
   pip install onnxruntime-gpu
   ```
3. **Set context ID**:
   ```env
   INSIGHTFACE_CTX_ID=0  # Use first GPU
   ```

**Note**: GPU support requires CUDA-compatible hardware and drivers.

## Face Embeddings

### Embedding Dimensions

- **Size**: 512 dimensions (for buffalo_s model)
- **Type**: Float32 numpy array
- **Normalized**: L2 normalized for efficient similarity calculation

### Embedding Extraction

The system extracts embeddings using InsightFace:

1. **Face Detection**: Detects faces in the image
2. **Face Alignment**: Aligns face for optimal recognition
3. **Embedding Generation**: Extracts 512-dimensional vector
4. **Normalization**: L2 normalizes the vector

### Embedding Storage

Embeddings are stored as **pgvector** vectors in PostgreSQL:

```sql
CREATE TABLE biometrics (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    embedding vector(512),  -- pgvector type
    ...
);
```

## Database Storage

### pgvector Extension

The system uses **pgvector** for efficient vector storage and similarity search:

```sql
-- Enable extension (done automatically in migrations)
CREATE EXTENSION IF NOT EXISTS vector;
```

### Vector Indexing

For optimal performance, create an index:

```sql
CREATE INDEX ON biometrics 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Note**: Index creation is handled automatically in migrations.

### Similarity Search

The system uses **cosine similarity** for face matching:

```python
# Cosine similarity calculation
similarity = 1 - cosine_distance(embedding1, embedding2)
```

- **Range**: 0.0 (different) to 1.0 (identical)
- **Threshold**: Configurable via `FACE_RECOGNITION_TOLERANCE` (default: 0.6)

### Data Privacy

- **Embeddings**: Stored as vectors (not encrypted, needed for search)
- **Thumbnails**: Encrypted using `BIOMETRIC_ENCRYPTION_KEY`
- **Full Images**: Not stored, only thumbnails

## API Endpoints

### Register Face

Register a client's face for recognition:

```http
POST /api/v1/face/register
Content-Type: application/json
Authorization: Bearer <token>

{
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Face registered successfully",
  "biometric_id": "987fcdeb-51a2-43f1-9876-543210fedcba",
  "client_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Authenticate Face

Authenticate a face and identify the client:

```http
POST /api/v1/face/authenticate
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "success": true,
  "match": true,
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "similarity": 0.95,
  "biometric_id": "987fcdeb-51a2-43f1-9876-543210fedcba"
}
```

### Compare Faces

Compare two faces without database lookup:

```http
POST /api/v1/face/compare
Content-Type: application/json

{
  "image1_base64": "data:image/jpeg;base64,...",
  "image2_base64": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "match": true,
  "similarity": 0.92
}
```

### Update Face

Update a client's registered face:

```http
PUT /api/v1/face/update
Content-Type: application/json
Authorization: Bearer <token>

{
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "image_base64": "data:image/jpeg;base64,..."
}
```

### Delete Face

Remove a client's face registration:

```http
DELETE /api/v1/face/{client_id}
Authorization: Bearer <token>
```

## Configuration

### Environment Variables

See [CONFIGURATION.md](CONFIGURATION.md) for all options.

**Key settings:**

```env
# Face Recognition
EMBEDDING_DIMENSIONS=512
INSIGHTFACE_MODEL=buffalo_s
INSIGHTFACE_DET_SIZE=640
INSIGHTFACE_CTX_ID=-1  # -1 for CPU, 0+ for GPU
FACE_RECOGNITION_TOLERANCE=0.6

# Image Processing
MAX_IMAGE_SIZE_MB=5
ALLOWED_IMAGE_FORMATS_STR=jpg,jpeg,png,webp
IMAGE_COMPRESSION_QUALITY=85
THUMBNAIL_COMPRESSION_QUALITY=70
THUMBNAIL_WIDTH=150
THUMBNAIL_HEIGHT=150
```

### Tolerance Tuning

The `FACE_RECOGNITION_TOLERANCE` setting controls matching strictness:

- **Lower (0.4-0.5)**: More strict, fewer false positives
- **Default (0.6)**: Balanced accuracy
- **Higher (0.7-0.8)**: More lenient, more false positives

**Recommendation**: Start with 0.6 and adjust based on your use case.

## Best Practices

### Image Quality

1. **Resolution**: Minimum 640x640 pixels recommended
2. **Lighting**: Good, even lighting
3. **Angle**: Face should be frontal (within 30 degrees)
4. **Distance**: Face should fill 30-50% of image
5. **Background**: Plain background preferred

### Registration

1. **Multiple Attempts**: Allow users to retry if registration fails
2. **Quality Check**: Validate image quality before registration
3. **User Feedback**: Provide clear instructions to users
4. **Error Handling**: Handle "no face detected" gracefully

### Authentication

1. **Timeout**: Set reasonable timeout for recognition (5-10 seconds)
2. **Retry Logic**: Allow 2-3 attempts before failing
3. **User Feedback**: Show "recognizing..." status
4. **Fallback**: Provide manual check-in option

### Security

1. **Encryption**: Thumbnails are encrypted at rest
2. **Access Control**: Only authorized users can register/delete faces
3. **Rate Limiting**: Prevent abuse of recognition endpoints
4. **Logging**: Log all face operations for audit

### Performance

1. **Model Caching**: Model is cached after first load
2. **Connection Pooling**: Use database connection pooling
3. **Indexing**: Ensure vector indexes are created
4. **Batch Operations**: Process multiple faces efficiently

## Performance Tips

### 1. Model Warmup

The model is pre-loaded on application startup (see `main.py`):

```python
# Model is warmed up during application startup
EmbeddingService._get_face_analysis()
```

### 2. Database Optimization

- **Vector Index**: Ensure `ivfflat` index is created
- **Connection Pooling**: Configure appropriate pool size
- **Query Optimization**: Use efficient similarity queries

### 3. GPU Acceleration

For high-traffic scenarios, use GPU:

```env
INSIGHTFACE_CTX_ID=0  # Use first GPU
```

**Benefits**:
- 5-10x faster inference
- Better for concurrent requests

**Requirements**:
- CUDA-compatible GPU
- CUDA drivers installed
- `onnxruntime-gpu` package

### 4. Caching

Consider caching frequently accessed embeddings:

- **Redis**: Cache client embeddings
- **Application Cache**: Cache model instance

### 5. Batch Processing

For bulk operations, process multiple faces:

```python
# Process multiple faces efficiently
embeddings = []
for image in images:
    embedding = EmbeddingService.extract_face_encoding(image)
    embeddings.append(embedding)
```

## Troubleshooting

### No Face Detected

**Symptoms**: Error "No face detected in the image"

**Solutions**:
1. Check image quality and resolution
2. Ensure face is clearly visible
3. Verify lighting conditions
4. Check image format (JPEG, PNG supported)

### Multiple Faces Detected

**Symptoms**: Warning about multiple faces

**Solution**: System automatically uses the largest face. For better accuracy, use images with single face.

### Low Similarity Scores

**Symptoms**: Authentication fails even with correct face

**Solutions**:
1. Increase `FACE_RECOGNITION_TOLERANCE` (e.g., 0.7)
2. Re-register face with better quality image
3. Check lighting conditions match registration
4. Ensure face angle is similar to registration

### Model Loading Errors

**Symptoms**: "Failed to initialize InsightFace model"

**Solutions**:
1. Check internet connection (for model download)
2. Verify disk space in model directory
3. Check ONNX Runtime installation
4. Review logs for specific error

### Slow Recognition

**Symptoms**: Recognition takes too long

**Solutions**:
1. Use GPU acceleration (`INSIGHTFACE_CTX_ID=0`)
2. Optimize database queries
3. Ensure vector indexes are created
4. Check server resources (CPU, memory)

### Database Connection Errors

**Symptoms**: "Database connection failed" during face operations

**Solutions**:
1. Verify database is running
2. Check `DATABASE_URL` configuration
3. Verify pgvector extension is installed
4. Check database connection pool settings

## Example Usage

### Python Client

```python
import requests
import base64

# Read image
with open("face.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Register face
response = requests.post(
    "http://localhost:8000/api/v1/face/register",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "client_id": "123e4567-e89b-12d3-a456-426614174000",
        "image_base64": f"data:image/jpeg;base64,{image_data}"
    }
)

# Authenticate face
response = requests.post(
    "http://localhost:8000/api/v1/face/authenticate",
    json={
        "image_base64": f"data:image/jpeg;base64,{image_data}"
    }
)
```

### cURL Example

```bash
# Register face
curl -X POST http://localhost:8000/api/v1/face/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "123e4567-e89b-12d3-a456-426614174000",
    "image_base64": "data:image/jpeg;base64,..."
  }'

# Authenticate
curl -X POST http://localhost:8000/api/v1/face/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,..."
  }'
```

## Advanced Topics

### Custom Models

To use a different InsightFace model:

1. Update `INSIGHTFACE_MODEL` in `.env`
2. Restart application
3. Model will be downloaded automatically

### Embedding Compression

Embeddings can be compressed for storage:

```env
EMBEDDING_COMPRESSION_LEVEL=9  # 0-9, higher = more compression
```

**Trade-off**: More compression saves space but uses more CPU.

### Similarity Metrics

The system uses cosine similarity. Other metrics available:

- **Cosine Similarity**: Default, good for normalized vectors
- **Euclidean Distance**: Alternative metric
- **Inner Product**: Fastest, but requires normalized vectors

---

**Next**: [API Documentation](API.md) | [Database Guide](DATABASE.md)

