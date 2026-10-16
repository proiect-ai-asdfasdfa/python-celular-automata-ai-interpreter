# python-celular-automata-ai-interpreter

## What we'll use (probably)
- Python
- `scikit-learn` - handles the RN
- `numpy` - 

## Idea (for starting out)
Create a NR for each automata and train the AI on each game. Don't rely on hardcoded implementations, each generation should run entirely on the NR.

## How to train (for a certain automata)
1. Implement that automata in a program (not hardcoded)
2. Run a (preferably) big number of generations, with multiple inputs
3. Save the state changes between generations for each cell
4. Give them to a NR, using `scikit-learn` probably
5. Run experiments on said NR
   - give it a new input
   - verify output corectness
   - nush cum continuam de aici

## Input Structure
Structured JSON, kinda like this. To start, the user would have to provide a JSON much like this,
```JSON
{
  "name": "Game of Life",
  "grid_size": [20, 20],
  "states": {
    "0": "DEAD",
    "1": "ALIVE"
  },
  "neighborhood": "Moore", 
  "rules": [
    {
      "current_state": 0,
      "new_state": 1,
      "condition": "count(1) == 3"
    },
    {
      "current_state": 1,
      "new_state": 1,
      "condition": "count(1) == 2 or count(1) == 3"
    }
  ],
  "default_state": 0,
  "matrix": [...],
  "generations" : <some_number>
}
```

## NR Input
TBD but basically the data mentioned earlier, depending on the game, saves a cell and it's vicinity (either 9 cells total or 5) as a starting state and the change between that and the next generation (special cases like edge cells require special casing prob but not that complicated). Since `scikit-learn` expects arrays for data, we'll have to normalize that but that shouldn't be that complicated either.

## Things to Learn
- how `scikit-learn` works / how to use it
- how to convert from natural language to JSON
- how to handle edge cells (either wrap around or pad out)
