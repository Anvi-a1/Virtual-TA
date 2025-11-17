---
title: "HuggingFace Spaces"
original_url: "https://tds.s-anand.net/#/huggingface-spaces?id=setting-up-a-docker-space"
downloaded_at: "2025-11-17T01:48:26.599343"
---
[Container hosting: Hugging Face Spaces with Docker](#/huggingface-spaces?id=container-hosting-hugging-face-spaces-with-docker)
-------------------------------------------------------------------------------------------------------------------------------

Container platforms let you deploy applications in isolated, portable environments that include all dependencies. They’re perfect for ML applications that need *custom environments, specific packages, or persistent state*. Here are some common real-life uses:

* A text summarization API that processes documents using custom NLP models (runs for 10-30 seconds per request)
* An image classification tool that requires specific computer vision libraries (runs for 5-15 seconds per upload)
* A chatbot with custom fine-tuned models that need GPU acceleration (runs for 2-5 seconds per message)

Unlike serverless functions, containers can maintain state, install any packages, write to the filesystem, and run background processes. They provide more control over the environment but require more configuration.

[![Best Platform for Python Apps Deployment - Hugging Face Spaces with Docker](https://i.ytimg.com/vi_webp/DQjze1SlYd4/sddefault.webp)](https://www.youtube.com/watch?v=DQjze1SlYd4)

[Hugging Face Spaces](https://huggingface.co/spaces) hosts ML apps with free CPU runtime for public repos and paid upgrades for persistent runs or stronger hardware. It plugs into the wider Hub—models, datasets, and tokens—so you can ship demos quickly.

Spaces offer four SDKs when you create a project: **Gradio** (default ML demos), **Streamlit** (dashboards), **Static HTML**, and **Docker** for any custom stack. This guide focuses on [Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker), which provide full control over runtimes and dependencies.

### [Setting up a Docker Space](#/huggingface-spaces?id=setting-up-a-docker-space)

[Sign up with Hugging Face](https://huggingface.co/join) and create a new Space. Choose “Docker” as your SDK.

Your Space repository needs these essential files:

**README.md** - Configure your Space with [YAML frontmatter](https://huggingface.co/docs/hub/spaces-config-reference):

```
---
title: My FastAPI App
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---
# My FastAPI Application
Description of your app goes here.Copy to clipboardErrorCopied
```

**Dockerfile** - Define your container environment (see [Dockerfile documentation](https://huggingface.co/docs/hub/spaces-sdks-docker)):

```
FROM python:3.11-slim

# Create the same UID (1000) that Spaces uses when running your container
RUN useradd -m -u 1000 user

# Install Python dependencies before copying the entire source tree
WORKDIR /home/user/app
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app and switch to the non-root user
COPY --chown=user . .
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]Copy to clipboardErrorCopied
```

Spaces execute your container as UID 1000. Creating that user in the image avoids permission problems when the platform switches users at runtime.

**requirements.txt** - List your Python dependencies:

```
fastapi
uvicorn[standard]
transformers
torchCopy to clipboardErrorCopied
```

**main.py** - Your [FastAPI](https://fastapi.tiangolo.com/) application:

```
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()

# Initialize your model (this happens once when container starts)
classifier = pipeline("sentiment-analysis")

@app.get("/")
def read_root():
    return {"message": "Hello from Hugging Face Spaces!"}

@app.post("/analyze")
def analyze_sentiment(text: str):
    result = classifier(text)
    return {"sentiment": result[0]["label"], "score": result[0]["score"]}Copy to clipboardErrorCopied
```

### [Deployment Process](#/huggingface-spaces?id=deployment-process)

1. **Create Space**: Visit [huggingface.co/new-space](https://huggingface.co/new-space) and select Docker SDK.
2. **Clone Repository**: `git clone https://huggingface.co/spaces/your-username/your-space-name`
3. **Add Files**: Create the files above in your local repository.
4. **Deploy**:

```
git add .
git commit -m "Initial deployment"
git pushCopy to clipboardErrorCopied
```

Your Space will automatically build and deploy. Build time depends on your base image and dependency downloads—refresh the **Logs** tab if the build appears stuck.

### [Writing Files and Data Persistence](#/huggingface-spaces?id=writing-files-and-data-persistence)

Docker Spaces support both temporary and persistent storage. Every Space gets 50 GB of free ephemeral disk that resets whenever the Space restarts or is paused.

**Temporary Files** (reset on restart):

```
import tempfile
import os

# Write temporary files
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("This will be lost on restart")
    temp_path = f.name

# Read it back
with open(temp_path, 'r') as f:
    content = f.read()Copy to clipboardErrorCopied
```

**Persistent Files** (paid upgrade):

Upgrade to a [persistent storage plan](https://huggingface.co/docs/hub/spaces-storage) from the Space **Settings** tab to mount `/data` as durable disk. Tiers start at 20 GB for $5/month and scale up to 1 TB for $100/month. The `/data` volume exists only at runtime (not during Docker build).

```
import os

# Write to persistent storage (requires upgrade)
data_dir = "/data"
if os.path.exists(data_dir):
    with open(f"{data_dir}/persistent_file.txt", "w") as f:
        f.write("This persists across restarts")Copy to clipboardErrorCopied
```

**Using Hugging Face Hub for Data Storage** (Free Alternative):

As a free alternative to persistent storage, you can programmatically upload files to a [Hugging Face Dataset repository](https://huggingface.co/docs/hub/datasets-overview) using the [`huggingface_hub` library](https://huggingface.co/docs/huggingface_hub/guides/upload).

```
from huggingface_hub import HfApi, upload_file

# Upload files to a dataset repository for persistence
api = HfApi()
upload_file(
    path_or_fileobj="local_file.json",
    path_in_repo="data/saved_data.json",
    repo_id="your-username/your-dataset",
    repo_type="dataset"
)Copy to clipboardErrorCopied
```

### [Environment Variables and Secrets](#/huggingface-spaces?id=environment-variables-and-secrets)

**Adding Variables**: Go to your Space settings → **Variables & secrets** tab. Add environment variables and secrets that will be available in your container.

**Using Variables in Code**:

```
import os

# Access environment variables
model_name = os.environ.get("MODEL_NAME", "default-model")
api_key = os.environ.get("SECRET_API_KEY") # For secretsCopy to clipboardErrorCopied
```

**Using Variables in Dockerfile**:
You can expose variables at build time using the `ARG` directive.

```
# Declare build-time variables
ARG MODEL_REPO_NAME
ENV MODEL_NAME=$MODEL_REPO_NAME

# Use in your application
RUN echo "Using model: $MODEL_NAME"Copy to clipboardErrorCopied
```

### [Advanced Features](#/huggingface-spaces?id=advanced-features)

**Hardware upgrades**: By default Spaces run on the free CPU basic tier (2 vCPU, 16 GB RAM, 50 GB disk). You can switch to CPU Upgrade ($0.03/hour) or attach GPUs/TPUs such as T4, A10G, L40S, H100, and TPU v5e in the **Settings → Hardware** panel. See the [hardware spec table](https://huggingface.co/docs/hub/spaces-gpus#hardware-specs) for prices and memory footprints.

**GPU Support**: When you select GPU hardware, base your image on an NVIDIA CUDA runtime and install CUDA-ready wheels. GPU devices are injected only at runtime—skip commands like `nvidia-smi` during the Docker build phase.

```
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04Copy to clipboardErrorCopied
```

**Multiple Ports**: Spaces expose a single public port. To serve multiple internal services, run a reverse proxy (for example Nginx or Caddy) and route everything through the exposed port defined by `app_port`.

```
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/nginx.confCopy to clipboardErrorCopied
```

**Custom Dependencies**: Install system packages before switching away from `root` to avoid permission issues.

```
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
 && rm -rf /var/lib/apt/lists/*Copy to clipboardErrorCopied
```

Keep persistent caches (like Hugging Face model downloads) under `/data/.huggingface` after enabling persistent storage and setting `HF_HOME=/data/.huggingface` so restarts skip re-downloading assets.

[Previous

Serverless hosting: Vercel](#/vercel)

[Next

Local LLMs: Ollama](#/ollama)