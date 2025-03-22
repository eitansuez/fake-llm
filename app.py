from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulated LLM responses for different LoRA modules
BASE_RESPONSE = "This is the base fake LLM response. Hello, world!"
LORA_A_RESPONSE = "This is fake LLM with LoRA-A. Greetings from module A!"
LORA_B_RESPONSE = "This is fake LLM with LoRA-B. Salutations from module B!"

@app.route('/v1/completions', methods=['POST'])
def completions():
    data = request.get_json()
    prompt = data.get('prompt', 'No prompt provided')

    # Check for LoRA selection (via query param, header, or body)
    lora_module = (
        request.args.get('lora') or  # Query param: ?lora=lora-a
        request.headers.get('X-LoRA-Module') or  # Header: X-LoRA-Module: lora-b
        data.get('lora') or  # Body field: {"lora": "lora-a"}
        None  # Default to base model if unspecified
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

    # Build OpenAI-like response
    response = {
        "id": "fake-123",
        "object": "text_completion",
        "created": 1677652288,
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
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
