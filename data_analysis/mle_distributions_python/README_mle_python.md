# Python version of MBA MLE Analysis core

`mle_distributions.py` is a cleaned Python rewrite of the core MLE fitting code from the  C# project. ( 	Humphries NE, Weimerskirch H, Sims DW. A new approach for objective identification of turns and steps in organism movement data relevant to random walk modelling. Freckleton R, editor. Methods Ecol Evol. 2013;4: 930–938. doi:10.1111/2041-210X.12096)





The original project is a Windows Forms C# application. We converted the mathematical core:

- MLE estimators for:
  - power law
  - exponential
  - truncated Pareto
  - truncated exponential
  - gamma
  - log-normal
- `Xmin` search
- `Xmax` search for truncated distributions
- Kolmogorov-Smirnov distance
- log-likelihood
- AICc model weights
- optional Monte Carlo p-value test

The GUI, track-file import, graph window, and Visual Studio-specific files are not included.

## Install dependencies

```bash
pip install numpy scipy pandas
```

`pandas` is only needed for the small command-line CSV demo at the bottom of the file.

## Simple use in Python

```python
from mle_distributions import fit_distribution

steps = [1.2, 1.5, 2.3, 5.0, 8.1, 10.2, 20.0]

result = fit_distribution(
    steps,
    dist="power",
    alt_dist="exponential",
    fitting="limited",
    p_test=False,
)

print(result.name)
print(result.parameters())
print("KS D:", result.ks_d)
print("LLH:", result.log_likelihood)
print("AIC weight:", result.aic_weight)

if result.alt:
    print("Alternate:", result.alt.name)
    print(result.alt.parameters())
    print("Alternate AIC weight:", result.alt.aic_weight)
```

## Command-line use with CSV

```bash
python mle_distributions.py your_steps.csv power exponential --column step_length
```

If `--column` is omitted, the script uses the first numeric column.

## Distribution names

Accepted `dist` / `alt_dist` values include:

- `power`, `power_law`, `power-law`
- `exponential`, `exp`
- `truncated_pareto`, `tp`
- `truncated_exponential`, `te`
- `gamma`
- `lognormal`, `log_normal`, `ln`

## Fitting modes

- `fitting="none"`: use initial xmin/xmax only.
- `fitting="limited"`: search Xmin/Xmax and stop after repeated worsening. This mirrors the common mode in the C# code.
- `fitting="best"`: try all possible Xmin values and apply the original range penalty.

## Note on one C# formula

In `MLE_Random.cs`, the random truncated-exponential generator appears to omit `1 -` inside the logarithm, while the deterministic version uses the standard inverse CDF. In Python I used the standard inverse CDF for random generation, because otherwise it can generate invalid values.
