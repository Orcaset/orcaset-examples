# Orcaset - Basic Model


This notebook demonstrates basic usage and capabilities of Orcaset.

1. **Model construction** - Create the model by construction classes for each line item
2. **Run model scenarios** - Instantiate the model with base case assumptions
3. **Third-party data integration** - Fetch interpolated Treasury rates via web API
4. **Interactive sensitivity** - Use [marimo's](https://marimo.io) reactive UI components to create interactive charts

This notebook creates a simple model with the following structure.

```
    ┌── Revenue
    ├── Operating Expense
┌── Operating Income
├── Interest Expense
Net Income
```

Interest expense is calculated by adding a spread to the most recent end-of-day 5-year US Treasury rate fetched over the web. Since the rate is updated at the end of every business day, the interest expense line item will change depending on the date this notebook is run.

The demo analysis is short. Model definitions, data retrieval, scenario instantiation, and chart presentation are all delivered in less than 100 lines of code.