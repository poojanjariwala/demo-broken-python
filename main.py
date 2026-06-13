import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Demo Broken Python App")

# BUG 1 (SECURITY): Insecure CORS configuration
# FastAPI raises an error / warning or it is a high-risk security issue when allow_origins=["*"] is combined with allow_credentials=True.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Fixed: Replaced "*" with a specific trusted origin for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BUG 2 (SECURITY): Hardcoded Sensitive Credentials
SECRET_API_KEY = "aws_access_key_id=AKIAIOSFODNN7EXAMPLE"
DATABASE_URL = "postgresql://dbadmin:SuperPassSecretWord123@postgres-server/prod"

@app.get("/")
def read_root():
    return {"message": "Demo Broken Python App is running"}

# BUG 3 (SECURITY): Remote Code Execution via unsafe YAML deserialization
# Using yaml.load with the default Loader is unsafe as it allows arbitrary code execution.
@app.post("/api/config/load")
async def load_config(payload: dict):
    yaml_data = payload.get("data", "")
    try:
        # Dangerous yaml.load execution
        config = yaml.load(yaml_data, Loader=yaml.Loader)
        return {"status": "success", "config": str(config)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# BUG 4 (PERFORMANCE): Heavy CPU computation inside async def blocks the event loop
# Async functions run on the single-threaded event loop. If they do blocking CPU computations,
# they freeze the server and prevent all other clients from connecting.
@app.get("/api/calculate/fibonacci")
async def calculate_fibonacci(n: int):
    # Synchronous recursive execution blocks the loop
    def fib(x):
        if x <= 1:
            return x
        return fib(x - 1) + fib(x - 2)
    
    if n > 40:
        raise HTTPException(status_code=400, detail="Number too large, will hang the server!")
        
    result = fib(n)
    return {"input": n, "result": result}

# BUG 5 (RUNTIME): ZeroDivisionError
@app.get("/api/divide")
def divide_numbers(a: float, b: float):
    # BUG: No validation for division by zero
    result = a / b
    return {"result": result}

# BUG 6 (RUNTIME): NameError / Missing Import
@app.get("/api/sqrt")
def get_sqrt(value: float):
    # BUG: math is not imported in this file, so math.sqrt will raise NameError
    result = math.sqrt(value)
    return {"value": value, "sqrt": result}