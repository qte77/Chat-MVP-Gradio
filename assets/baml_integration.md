# Refactoring from Pydantic to BAML

BAML (short for Bayesian Assertion Markup Language) primarily involves reworking how input/output validation is defined and enforced in machine learning (ML) workflows. Here's a detailed approach to doing this, along with the pros and cons:

## Step 1: Understand Current Pydantic Use

Identify all BaseModel definitions used for:

- Input validation (e.g., PredictionRequest)
- Output format enforcement (e.g., PredictionResponse)
- Data constraints (min/max, types, enums)

### Example

```python
class PredictionInput(BaseModel):
    age: int
    income: float
    gender: Literal['male', 'female']

# Initialize a .baml file for ML model assertions
# Example (schema.baml):
input:
  age: int >= 0
  income: float >= 0
  gender: category('male', 'female')

output:
  prediction: float between 0 and 1
  
from baml import check_io

@check_io("schema.baml")
def predict(input):
    # ML inference code here
    return {"prediction": 0.76}
```

## BAML monitoring

BAML runtime hooks to detect input drift, out-of-distribution values, or contract violations during inference in production.

## Comparison

| Feature                          | Pydantic                         | BAML                                     |
|----------------------------------|----------------------------------|------------------------------------------|
| ✔ Type enforcement               | ✅ Strong                         | ✅ Strong                                 |
| ✔ Data bounds/range checks       | ✅ Supported                      | ✅ Stronger support with probabilistic rules |
| ✔ Category enforcement           | ✅ With `Literal`                | ✅ More expressive                        |
| ✔ Distributional checks          | ❌ Not supported                 | ✅ Supports Gaussian, Uniform, etc.       |
| ✔ Drift detection                | ❌ Not native                    | ✅ Built-in                               |
| ✔ Output contract validation     | 🟡 Manual                        | ✅ Built-in                               |
| ✔ Production runtime validation  | 🟡 Needs manual instrumentation | ✅ Built-in                               |


## ⚖️ When to Use BAML vs Pydantic?

- BAML: ML model runtime validation, ML production drift detection, Declarative contract enforcement
- Pydantic: FastAPI or Web APIs
- Either: Internal tooling and validation

## Hybrid Approach

```python
# Pydantic for API
class PredictRequest(BaseModel):
    age: int
    income: float

# BAML for inference contract
@check_io("schema.baml")
def model_infer(input: dict):
    ...
```
