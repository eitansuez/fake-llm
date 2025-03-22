from flask import Flask, request, jsonify
import time
import logging
import signal
import sys

# Set up logging to capture detailed request info
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture all details
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simulated LLM responses for different LoRA modules
BASE_RESPONSE = "This is the base fake LLM response. Hello, world!"
LORA_A_RESPONSE = "This is fake LLM with LoRA-A. Greetings from module A!"
LORA_B_RESPONSE = "This is fake LLM with LoRA-B. Salutations from module B!"

# Simple metrics tracking (in-memory, resets on restart)
request_count = 0
total_latency = 0.0
running_requests = 0  # Simulate requests currently "running"
waiting_requests = 0  # Simulate requests in queue

# Signal handler for graceful shutdown (to fix slow pod termination)
def shutdown_handler(signum, frame):
    print("Received SIGTERM, shutting down gracefully...")
    sys.exit(0)

# Register signal handler to catch SIGTERM from Kubernetes
signal.signal(signal.SIGTERM, shutdown_handler)

# Function to log detailed request information for debugging
def dump_request_details():
    """Log detailed information about the incoming request."""
    logger.debug("=== Incoming Request ===")
    logger.debug(f"Method: {request.method}")
    logger.debug(f"Path: {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Query Params: {request.args.to_dict()}")
    logger.debug(f"Body: {request.get_data(as_text=True)}")
    logger.debug("======================")

@app.route('/v1/completions', methods=['POST'])
def completions():
    global request_count, total_latency, running_requests, waiting_requests
    start_time = time.time()

    # Dump request details to see how the Inference Extension calls this endpoint
    dump_request_details()

    data = request.get_json()
    prompt = data.get('prompt', 'No prompt provided')

    # Simulate some queueing behavior for metrics
    waiting_requests += 1
    time.sleep(0.005)  # Fake queue delay
    waiting_requests -= 1
    running_requests += 1

    # Check for LoRA selection (via query param, header, or body)
    lora_module = (
        request.args.get('lora') or  # Query param: ?lora=lora-a
        request.headers.get('X-LoRA-Module') or  # Header: X-LoRA-Module: lora-b
        data.get('lora') or  # Body field: {"lora": "lora-a"}
        None  # Default to base model if unspecified
    )

    # Select response based on LoRA module (tweaked by eitan to also look at the model field in the request data
    if lora_module == 'lora-a' or data.get('model') == 'fake-llm-lora-a':
        response_text = LORA_A_RESPONSE
        model_name = "fake-llm-lora-a"
    elif lora_module == 'lora-b' or data.get('model') == 'fake-llm-lora-b':
        response_text = LORA_B_RESPONSE
        model_name = "fake-llm-lora-b"
    else:
        response_text = BASE_RESPONSE
        model_name = "fake-llm"

    # Simulate processing time (optional, for realism)
    time.sleep(0.01)  # 10ms fake latency

    # Build OpenAI-like response
    response = {
        "id": "fake-123",
        "object": "text_completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "text": response_text,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "total_tokens": 20
        }
    }

    # Update metrics
    latency = time.time() - start_time
    request_count += 1
    total_latency += latency
    running_requests -= 1  # Request "finishes"

    return jsonify(response), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    global request_count, total_latency, running_requests, waiting_requests
    
    # Dump request details to see how the Inference Extension calls this endpoint
    # dump_request_details()

    # Prometheus-style text format mimicking vLLM metric names
    metrics = [
        '# HELP vllm:num_requests_running Number of requests currently running on GPU.',
        '# TYPE vllm:num_requests_running gauge',
        f'vllm:num_requests_running {running_requests}',
        '# HELP vllm:num_requests_waiting Number of requests waiting to be processed.',
        '# TYPE vllm:num_requests_waiting gauge',
        f'vllm:num_requests_waiting {waiting_requests}',
        '# HELP vllm:gpu_cache_usage_perc GPU KV-cache usage. 1 means 100 percent usage.',
        '# TYPE vllm:gpu_cache_usage_perc gauge',
        f'vllm:gpu_cache_usage_perc 0.5',  # Fake static value (50%)
        '# HELP vllm:lora_requests_info Running stats on LoRA requests.',
        '# TYPE vllm:lora_requests_info gauge',
        f'vllm:lora_requests_info{{running_lora_adapters="lora-a:1,lora-b:0",max_lora="2",waiting_lora_adapters="lora-a:0,lora-b:0"}} {int(time.time())}',
    ]
    return '\n'.join(metrics) + '\n', 200, {'Content-Type': 'text/plain; version=0.0.4'}
