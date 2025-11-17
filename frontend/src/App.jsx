import { useState, useEffect } from 'react';

function App() {
    const [numbers, setNumbers] = useState("");
    const [resultado, setResultado] = useState(null);
    const [historial, setHistorial] = useState([]);
    const [errorMessage, setErrorMessage] = useState("");
    const [filterOperation, setFilterOperation] = useState('all');
    const [filterDate, setFilterDate] = useState('');
    const [sortBy, setSortBy] = useState('date');
    const [sortOrder, setSortOrder] = useState('desc');

    const getOperationSymbol = (operation) => {
        switch (operation) {
            case 'sum':
                return '+';
            case 'rest':
                return '-';
            case 'div':
                return '/';
            case 'mult':
                return '*';
            default:
                return '?';
        }
    };

    const performOperation = async (operation) => {
        setErrorMessage("");
        setResultado(null);
        
        const numList = numbers.split(',').map(num => parseFloat(num.trim())).filter(num => !isNaN(num));
        if (numList.length === 0) {
            setErrorMessage("Por favor, ingresa al menos un número.");
            return;
        }

        const queryParams = new URLSearchParams();
        numList.forEach(num => queryParams.append('a', num));

        try {
            const res = await fetch(`http://localhost:8089/calculator/${operation}?${queryParams.toString()}`);
            const data = await res.json();
            
            if (!res.ok) { 
                setErrorMessage(data.detail || "Ocurrió un error en la solicitud.");
            } else {
                setResultado(data.result);
                // Llamamos al historial solo si la operación fue exitosa
                obtenerHistorial(); 
            }
        } catch (error) {
            setErrorMessage("Error al conectar con el servidor.");
        }
    };

    const obtenerHistorial = async () => {
        try {
            const queryParams = new URLSearchParams({
                sort_by: sortBy,
                sort_order: sortOrder,
            });
            if (filterOperation !== 'all') {
                queryParams.append('operation', filterOperation);
            }
            if (filterDate) {
                queryParams.append('date', filterDate);
            }

            const res = await fetch(`http://localhost:8089/calculator/history?${queryParams.toString()}`);
            const data = await res.json();
            setHistorial(data.history || []); 
        } catch (error) {
            setErrorMessage("Error al obtener el historial.");
        }
    };

    useEffect(() => {
        obtenerHistorial();
    }, [filterOperation, filterDate, sortBy, sortOrder]);


    return (
        <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center p-6 font-sans">
            <div className="w-full max-w-md bg-gray-800 rounded-xl shadow-lg p-6">
                <h1 className="text-3xl font-bold text-center text-blue-400 mb-6">
                    Calculadora
                </h1>

                {/* Inputs */}
                <div className="flex flex-col space-y-4">
                    <input
                        type="text"
                        value={numbers}
                        onChange={(e) => setNumbers(e.target.value)}
                        placeholder="Ingresa números separados por comas (e.g., 2,4,5)"
                        className="px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="grid grid-cols-2 gap-4">
                        <button
                            onClick={() => performOperation('sum')}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition duration-200"
                        >
                            Sumar
                        </button>
                        <button
                            onClick={() => performOperation('rest')}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition duration-200"
                        >
                            Restar
                        </button>
                        <button
                            onClick={() => performOperation('div')}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition duration-200"
                        >
                            Dividir
                        </button>
                        <button
                            onClick={() => performOperation('mult')}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition duration-200"
                        >
                            Multiplicar
                        </button>
                    </div>
                </div>

                {/* Mensaje de error */}
                {errorMessage && (
                    <div className="mt-6 text-center bg-red-800 text-red-100 p-3 rounded-lg">
                        <p>{errorMessage}</p>
                    </div>
                )}

                {/* Resultado */}
                {resultado !== null && (
                    <h2 className="mt-6 text-xl font-semibold text-green-400 text-center">
                        Resultado: {resultado}
                    </h2>
                )}

                {/* Controles de filtro y ordenación */}
                <div className="mt-8 space-y-4">
                    <h3 className="text-lg font-semibold text-gray-300 mb-2">Historial:</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div className="flex flex-col space-y-2">
                            <label className="text-gray-400 text-sm">Filtrar por operación:</label>
                            <select
                                value={filterOperation}
                                onChange={(e) => setFilterOperation(e.target.value)}
                                className="px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100"
                            >
                                <option value="all">Todas</option>
                                <option value="sum">Suma</option>
                                <option value="rest">Resta</option>
                                <option value="div">División</option>
                                <option value="mult">Multiplicación</option>
                            </select>
                        </div>
                         <div className="flex flex-col space-y-2">
                            <label className="text-gray-400 text-sm">Filtrar por fecha:</label>
                            <input
                                type="date"
                                value={filterDate}
                                onChange={(e) => setFilterDate(e.target.value)}
                                className="px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100"
                            />
                        </div>
                        <div className="flex flex-col space-y-2">
                            <label className="text-gray-400 text-sm">Ordenar por:</label>
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value)}
                                className="px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100"
                            >
                                <option value="date">Fecha</option>
                                <option value="result">Resultado</option>
                            </select>
                        </div>
                        <div className="flex flex-col space-y-2">
                            <label className="text-gray-400 text-sm">Orden:</label>
                            <select
                                value={sortOrder}
                                onChange={(e) => setSortOrder(e.target.value)}
                                className="px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-100"
                            >
                                <option value="desc">Descendente</option>
                                <option value="asc">Ascendente</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Historial */}
                <div className="mt-8">
                    <ul className="space-y-2 max-h-40 overflow-y-auto">
                        {historial.length > 0 ? (
                            historial.map((op, i) => (
                                <li
                                    key={i}
                                    className="bg-gray-700 px-4 py-2 rounded-lg border border-gray-600 text-sm flex justify-between items-center flex-wrap"
                                >
                                    
                                    <span className="break-all">
                                      {op.numbers ? op.numbers.join(` ${getOperationSymbol(op.operation)} `) : 'Operación inválida'} ={' '}
                                      <span className="text-green-400 font-bold">{op.result}</span>
                                    </span>
                                    
                                    <span className="text-gray-400 text-xs text-right">({new Date(op.date).toLocaleString()})</span>
                                </li>
                            ))
                        ) : (
                            <li className="text-gray-400 text-sm text-center">No hay historial disponible.</li>
                        )}
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default App;
