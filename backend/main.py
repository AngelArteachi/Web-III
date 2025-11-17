import datetime
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Union

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb://admin_user:web3@mongo:27017/")
database = client.practica1
collection_historial = database.historial

def validate_non_negative(numbers: List[float]):
    if any(num < 0 for num in numbers):
        raise HTTPException(
            status_code=400, 
            detail="No se aceptan números negativos para esta operación."
        )

# --- Endpoints de la Calculadora ---

@app.get("/calculator/sum")
def sum_numbers(a: List[float] = Query(..., description="Una lista de números para sumar")):
    validate_non_negative(a)
    
    result = sum(a)
    
    document = {
        "operation": "sum",
        "numbers": a,
        "result": result,
        "date": datetime.datetime.now(tz=datetime.timezone.utc)
    }
    collection_historial.insert_one(document)

    # 4. Devolver la respuesta.
    return {"operation": "sum", "numbers": a, "result": result}

@app.get("/calculator/rest")
def rest_numbers(a: List[float] = Query(..., description="Una lista de números para restar")):
    validate_non_negative(a)
    if not a:
        raise HTTPException(status_code=400, detail="Se requiere al menos un número para la resta.")
    
    result = a[0]
    for num in a[1:]:
        result -= num
        
    document = {
        "operation": "rest",
        "numbers": a,
        "result": result,
        "date": datetime.datetime.now(tz=datetime.timezone.utc)
    }
    collection_historial.insert_one(document)

    return {"operation": "rest", "numbers": a, "result": result}

@app.get("/calculator/div")
def dividir(a: List[float] = Query(..., description="Una lista de números para dividir")):
    validate_non_negative(a)
    if len(a) < 2:
        raise HTTPException(status_code=400, detail="Se requieren al menos dos números para la división.")
    if 0 in a[1:]:
        raise HTTPException(status_code=400, detail="No se puede dividir por cero")

    result = a[0]
    for num in a[1:]:
        result /= num
        
    document = {
        "operation": "div",
        "numbers": a,
        "result": result,
        "date": datetime.datetime.now(tz=datetime.timezone.utc)
    }
    collection_historial.insert_one(document)

    return {"operation": "div", "numbers": a, "result": result}

@app.get("/calculator/mult")
def mult_numbers(a: List[float] = Query(..., description="Una lista de números para multiplicar")):
    validate_non_negative(a)
    if not a:
        raise HTTPException(status_code=400, detail="Se requiere al menos un número para multiplicar.")

    result = 1
    for num in a:
        result *= num

    document = {
        "operation": "mult",
        "numbers": a,
        "result": result,
        "date": datetime.datetime.now(tz=datetime.timezone.utc)
    }
    collection_historial.insert_one(document)
    
    return {"operation": "mult", "numbers": a, "result": result}

@app.get("/calculator/history")
def obtain_history(
    operation: Optional[str] = Query(None, description="Filtrar por tipo de operación"),
    date: Optional[str] = Query(None, description="Filtrar por fecha (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("date", description="Ordenar por 'date' o 'result'"),
    sort_order: Optional[str] = Query("desc", description="Orden 'asc' o 'desc'")
):
    filter_query = {}
    if operation and operation != "all":
        filter_query["operation"] = operation

    if date:
        try:
            start_of_day = datetime.datetime.fromisoformat(date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)
            end_of_day = start_of_day + datetime.timedelta(days=1)
            filter_query["date"] = {"$gte": start_of_day, "$lt": end_of_day}
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD.")


    sort_direction = -1 if sort_order == "desc" else 1
    sort_key = sort_by if sort_by in ["date", "result"] else "date"

    records = collection_historial.find(filter_query).sort(sort_key, sort_direction).limit(20)

    history = []
    for record in records:
        history.append({
            "numbers": record.get("numbers"),
            "result": record.get("result"),
            "operation": record.get("operation"),
            "date": record["date"].isoformat() if "date" in record else None
        })
    return {"history": history}

# El endpoint de batch_operations no guarda en el historial, por lo que no necesita cambios.
@app.post("/calculator/batch_operations")
def batch_operations(operations: List[Dict[str, Union[str, List[float]]]]):
    results = []
    for op_data in operations:
        op_type = op_data.get("op")
        nums = op_data.get("nums", [])
        
        if any(n < 0 for n in nums):
            results.append({"op": op_type, "error": "No se aceptan números negativos para esta operación."})
            continue

        op_type_map = {
            "sum": {"func": sum, "min_operands": 2, "initial": None},
            "mult": {"func": lambda l: eval('*'.join(map(str, l))), "min_operands": 2, "initial": 1},
            "rest": {"func": lambda l: l[0] - sum(l[1:]), "min_operands": 2, "initial": None},
            "div": {"func": lambda l: l[0] / eval('*'.join(map(str, l[1:]))), "min_operands": 2, "initial": None},
        }

        if op_type in op_type_map:
            config = op_type_map[op_type]
            if len(nums) < config["min_operands"]:
                results.append({"op": op_type, "error": f"La operación requiere al menos {config['min_operands']} operandos."})
                continue
            
            if op_type == "div" and 0 in nums[1:]:
                 results.append({"op": op_type, "error": "No se puede dividir por cero."})
                 continue
            
            result = config["func"](nums)
            results.append({"op": op_type, "result": result})
        else:
            results.append({"op": op_type, "error": "Operación no soportada."})

    return results
