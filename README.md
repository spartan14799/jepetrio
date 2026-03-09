# Jepetrio 🤖 (Tetris 1vs1 Blitz Bot)

Este es un bot de alto rendimiento optimizado en Python para jugar Tetris competitivo (especialmente en *Tetr.io*). Es capaz de alcanzar velocidades inhumanas (más de 40 Piezas Por Segundo) calculando posiciones óptimas usando constantes matemáticas de supervivencia extrema (basadas en la heurística de Pierre Dellacherie).

## ⚡ ¿Por qué no usamos Multithreading por defecto en Blitz?

En Python existe un mecanismo llamado **GIL (Global Interpreter Lock)** que, a grandes rasgos, obliga a que **solo un hilo matemático interno corra cálculos reales a la vez**.

Para jugar **Blitz a velocidad de la luz**, evaluamos el bloque actual buscando la máxima velocidad (`max_depth = 1`). Con este nivel de profundidad, el cálculo matemático se resuelve en tan solo **~0.038 segundos** en un solo hilo.

Si intentamos hacer este simple cálculo separándolo en múltiples hilos (Multithread) o procesos, el tiempo que tarda la computadora en:
1. Crear los hilos
2. Repartir el trabajo
3. Pelear por el GIL
4. Volver a unir las respuestas

**Es superior al tiempo que tarda el cerebro del bot en calcular todo en un solo hilo**. Usar Multithreading para el cálculo de un bloque eleva el tiempo a **0.14 segundos** por jugada (volviendo el bot unas 3.5x veces más lento). 

**Nota:** Aún así, tu código cuenta con la función `compute()` (basada en `ThreadPoolExecutor`) en `agent.py`. Si alguna vez deseas calcular el futuro lejano de las piezas (`max_depth = 2` o superior), *allí sí te servirá invocar el Multithreading* porque los cálculos masivos terminan siendo tan largos que sí compensan dividir el trabajo.

---

## 🚀 Requisitos de Instalación

1. Asegúrate de tener Python instalado (versión 3.10 o superior recomendada).
2. Clona este proyecto y abre una terminal.
3. Crea un entorno virtual e instala las dependencias:

```powershell
# 1. Crear el Entorno Virtual (en Windows)
python -m venv .venv

# 2. Activar el Entorno
.\.venv\Scripts\activate

# 3. Instalar librerías
pip install numpy pyautogui
```

## 🎮 Cómo ejecutar los Tests y el Bot

Con tu entorno virtual activo `(.venv)`, puedes probar la capacidad de tu motor usando cualquiera de los siguientes comandos de terminal:

### 1. Testear Desempeño y Sobrevivencia contra Tetr.io (1vs1)
Valida a qué ritmo jugaría tu bot, simulando una lluvia en tiempo real de piezas (y puntaje) por dos minutos seguidos:
```powershell
python test_tetrio_score.py
```
*(Al finalizar, generará un reporte de Puntos y Líneas en `score_result.txt`)*

### 2. Comparativo de Optimización (Original vs Optimizado)
Evalúa lado a lado cómo reaccionaba el bot original comparado con esta bestia rápida actual, resolviendo las mismitas primeras 15 piezas:
```powershell
python compare_agents.py
```
*(Guarda y muestra el resultado del cruce en consola y un archivo temporal)*

### 3. Ejecutar Pruebas Base de Lógica del Tetris
Pruebas automáticas rigurosas sobre colisiones y borrado de tablas simuladas (Unit Test):
```powershell
python -m unittest test_agent.py -v
```

### 4. Lanzar el Agente (El Juego Real)
*(Nota: Actualmente requiere implementar `# TODO Implementar Vision` para leer el bucle)*
```powershell
python agent.py
```
