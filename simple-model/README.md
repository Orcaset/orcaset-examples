# Orcaset - Basic Model

_[Try this notebook interactively in the browser!](https://orcaset.github.io/orcaset-examples/simple-model/)_

[Orcaset](https://github.com/Orcaset/orcaset) is an open toolkit for financial analysis. It enables powerful processes like automation using AI code generation, flexible data source integration, model testability, and version control by running in an open Python environment.

This notebook demonstrates basic usage and capabilities of the `orcaset` library with a minimal example.

1. **Model construction** - Create the model by defining classes for each line item
2. **Run model scenarios** - Instantiate the model with scenario assumptions
3. **Third-party data integration** - Fetch current Treasury rates via web API
4. **Interactive sensitivity** - Use [marimo's](https://marimo.io) reactive UI components to create interactive charts

The model developed in this notebook has the following structure:

```
    ┌── Revenue
    ├── Operating Expense
┌── Operating Income
├── Interest Expense
Net Income
```

This example is short. The full analysis delivers model definitions, data retrieval, scenario sensitivity, and chart presentation in less than 100 lines of code.