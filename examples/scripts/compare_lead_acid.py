import numpy as np
import pybamm

pybamm.set_logging_level("INFO")

# load models
models = [
    pybamm.lead_acid.LOQS(),
    # pybamm.lead_acid.FOQS(),
    pybamm.lead_acid.Composite(),
    # pybamm.lead_acid.Composite({"surface form": "algebraic"}),
    # pybamm.lead_acid.NewmanTiedemann(),
]

# create geometry
geometry = models[-1].default_geometry

# load parameter values and process models and geometry
param = models[0].default_parameter_values
param.update(
    {
        "Typical current [A]": 20,
        "Initial State of Charge": 1,
        "Typical electrolyte concentration [mol.m-3]": 5600,
        "Negative electrode reference exchange-current density [A.m-2]": 0.08,
        "Positive electrode reference exchange-current density [A.m-2]": 0.006,
    }
)
for model in models:
    param.process_model(model)
param.process_geometry(geometry)

# set mesh
var = pybamm.standard_spatial_vars
var_pts = {var.x_n: 25, var.x_s: 41, var.x_p: 34}
mesh = pybamm.Mesh(geometry, models[-1].default_submesh_types, var_pts)

# discretise models
for model in models:
    disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
    disc.process_model(model)

# solve model
solutions = [None] * len(models)
t_eval = np.linspace(0, 1, 100)
for i, model in enumerate(models):
    solution = model.default_solver.solve(model, t_eval)
    solutions[i] = solution

# plot
output_variables = [
    [
        "Average negative electrode interfacial current density [A.m-2]",
        "Average positive electrode interfacial current density [A.m-2]",
    ],
    "Average negative electrode surface potential difference [V]",
    "Average positive electrode surface potential difference [V]",
    "Electrolyte concentration",
    "Electrolyte flux",
    "Terminal voltage [V]",
]
plot = pybamm.QuickPlot(models, mesh, solutions, output_variables)
plot.dynamic_plot()
