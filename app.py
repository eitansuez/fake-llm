from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Simulated LLM responses for different LoRA modules
BASE_RESPONSE = "This is the base fake LLM response. Hello, world!"
LORA_A_RESPONSE = "This is fake LLM with LoRA-A. Greetings from module A!"
LORA_B_RESPONSE = "This is fake LLM with LoRA-B. Salutations from module B!"

# Simple metrics tracking (in-memory, resets on restart)
request_count = 0
total_latency = 0.0

@app.route('/v1/completions', methods=['POST'])
def completions():
    global request_count, total_latency
    start_time = time.time()

    data = request.get_json()
    prompt = data.get('prompt', 'No prompt provided')

    # Check for LoRA selection (via query param, header, or body)
    lora_module = (
        request.args.get('lora') or
        request.headers.get('X-LoRA-Module') or
        data.get('lora') or
        None
    )

    # Select response based on LoRA module
    if lora_module == 'lora-a':
        response_text = LORA_A_RESPONSE
        model_name = "fake-llm-lora-a"
    elif lora_module == 'lora-b':
        response_text = LORA_B_RESPONSE
        model_name = "fake-llm-lora-b"
    else:
        response_text = BASE_RESPONSE
        model_name = "fake-llm"

    # Simulate some processing time (optional, for realism)
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

    return jsonify(response), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    global request_count, total_latency
    # Prometheus-style text format
    metrics = [
        '# HELP fake_llm_requests_total Total number of requests processed',
        '# TYPE fake_llm_requests_total counter',
        f'fake_llm_requests_total {request_count}',
        '# HELP fake_llm_latency_seconds Total latency of all requests in seconds',
        '# TYPE fake_llm_latency_seconds gauge',
        f'fake_llm_latency_seconds {total_latency:.4f}',
        '# HELP fake_llm_avg_latency_seconds Average latency per request in seconds',
        '# TYPE fake_llm_avg_latency_seconds gauge',
        f'fake_llm_avg_latency_seconds {(total_latency / request_count if request_count > 0 else 0):.4f}',
    ]
    return '\n'.join(metrics) + '\n', 200, {'Content-Type': 'text/plain; version=0.0.4'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
