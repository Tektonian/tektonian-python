<h1 align="center"><b>Simulac</b></h3>

<h3 align="center"><b>⚡️ Developer centric digital twin builder</b></h3>

---

[Simulac](https://github.com/Tektonian/simulac) is digital twin build tool filling the gap between physical world and software world.

Simulac helps transition between the two worlds, and provides developer-friendly API to building the world.

# Quick start

## Installation

Simulac requires Python 3.12 or later.

```bash
$ pip install simulac
$ uv add simulac
```

## Sign up and create an API key

Remote benchmark execution requires a Tektonian API key.
Go to our [website](https://tektonian.com) and get an API key.

Store your API key with CLI commend:
```bash
simulac login
```

You can also provide the key through an environment variable:
```bash
export SIMULAC_API_KEY=<you_api_key>
```
Note: API keys can only be viewed once when created

# Key function
Simulac provides one-line code execution for robot domain benchmark, and world building API (on developing)

## Benchmark

You can execution famous Physical-AI benchmarks with one-line of code.
We currently support: 
- **[Libero](https://tektonian.com/profile/Tektonian/Libero)**
- **[Calvin](https://tektonian.com/profile/Tektonian/Calvin)**
- **[Robomimic](https://tektonian.com/profile/Tektonian/Robomimic)**
- **[Metaworld](https://tektonian.com/profile/Tektonian/Metaworld)** 

Visit [benchmark list](https://tektonian.com/benchmark) for details for running it.
### Run benchmark
```python
from simulac.gym_style import init_bench

env = init_bench(
    "Tektonian/Libero",
    "libero_90/KITCHEN_SCENE2_put_the_black_bowl_at_the_back_on_the_plate",
    0,
    {"control_mode": "OSC_POSE"},
)

step = env.step(ACTION_ARRAY)

```
### Parallel Benchmark Execution

```python
from simulac.gym_style import init_bench, make_vec

args = (
    "Tektonian/Libero",
    "libero_90/KITCHEN_SCENE2_put_the_black_bowl_at_the_back_on_the_plate",
    0,
)
options = {"benchmark_specific": {"control_mode": "OSC_POSE"}}

envs = [init_bench(*args, **options) for _ in range(3)]
vec_env = make_vec(envs)

steps = vec_env.step([[0.0] * 7 for _ in envs])
print(len(steps))
```

## Configuration

Simulac reads configuration from environment variables when present:

- `SIMULAC_API_KEY`: use an API key without running `simulac login`
- `SIMULAC_BASE_URL`: override the default Tektonian API endpoint
- `SIMULAC_LOG_LEVEL`: set log verbosity. choose one of `off, trace, debug, info, warning, error`
- `SIMULAC_TELEMETRY=off`: disable telemetry


## World building

The world-building surface is best viewed as an evolving foundation for scene assembly and engine integration. 

## Project Status

Simulac is currently alpha software.

- The remote benchmark client is the most complete public surface.
- Local world-building and runner APIs are still evolving.

## License

Apache-2.0