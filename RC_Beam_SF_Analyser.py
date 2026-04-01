import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import math
from IPython.display import display, Markdown
from IPython.display import HTML
from scipy.interpolate import interp1d
import ast
import ipywidgets as widgets
from IPython.display import display
import streamlit as st

# title document
st.title("Moment Capacity of Rectangular Singly Reinforced Concrete Sections - AASHTO LRFD 10th Edition")

# draw beam and rebar diagrams
def draw_beam_with_rebars(width, height, num_rebars, cover, bar_dia):
    fig, ax = plt.subplots(figsize=(4, 3))  # compact figure
    
    # Draw beam rectangle with grey fill
    beam_rect = plt.Rectangle(
        (0, 0), width, height,
        fill=True, facecolor="lightgrey", edgecolor="black", linewidth=2
    )
    ax.add_patch(beam_rect)
    
    # Effective spacing considering cover on both sides
    if num_rebars > 1:
        spacing = (width - 2 * cover) / (num_rebars - 1)
    else:
        spacing = 0
    
    # Vertical position of rebars (cover from bottom)
    y_pos = cover
    
    for i in range(num_rebars):
        # Horizontal positions start at "cover" and end at "width - cover"
        x_pos = cover + i * spacing if num_rebars > 1 else width / 2
        rebar = plt.Circle((x_pos, y_pos), radius=bar_dia/2, 
                           color="red", fill=True)
        ax.add_patch(rebar)
    
    # Formatting
    ax.set_xlim(-width * 0.1, width * 1.1)
    ax.set_ylim(-height * 0.1, height * 1.1)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    
    return fig



# Layout: inputs left, figure right
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Beam Parameters")
    width       = st.number_input("Beam width (in)", min_value=0.0, value=12.0, step=0.1)
    depth       = st.number_input("Beam depth (in)", min_value=0.0, value=20.0, step=0.1)
    bar_nos     = st.number_input("No. of rebars", min_value=0, value=4, step=1) 
    bar_dia     = st.number_input("Rebar dia (in)", min_value=0.0, value=1.125, step=0.1)
    f_y         = st.number_input("Yield strength of rebars (psi)", min_value=0.0, value=60000.0, step=1.0)
    f_c         = st.number_input("Compressive strength of concrete (psi)", min_value=0.0, value=4000.0, step=1.0)
    cov_eff     = st.number_input("Effective cover (in)", min_value=0.0, value=2.5, step=0.1)

with col2:
    st.subheader("Beam Section")
    fig = draw_beam_with_rebars(width, depth, bar_nos, cov_eff, bar_dia)
    st.pyplot(fig)

#stress block factor beta_1 calculator
def beta_1_calc(f_c):
    if f_c >= 2500 and f_c <= 4000:
        beta_1 = 0.85
    if f_c > 4000 and f_c < 8000:
        beta_1 = 0.85 - .05/1000 * (f_c - 4000)
    if f_c >= 8000:
        beta_1 = 0.65
    return beta_1

# stress block factor α_{1}
def alpha_1_calc(f_c):
    if f_c < 10000:
        alpha_1 = 0.85
    else:
        alpha_1 = 0.85 - 0.02*(f_c-10000)/1000
    return alpha_1

# strength reduction factor calculator
def str_red_fact_calc(net_tens_e, f_y):
    x        = np.array([60, 75, 80, 100]) #ksi
    y        = np.array([0.002, 0.0028, 0.003, 0.004])
    z        = np.array([0.005, 0.005, 0.0056, 0.008])
# Create a linear interpolating function
    f_linear_y = interp1d(x, y, kind='linear', bounds_error=False, fill_value=(y.min(), y.max()))
    f_linear_z = interp1d(x, z, kind='linear', bounds_error=False, fill_value=(z.min(), z.max()))
# Evaluate at new points
    e_cl  = f_linear_y(f_y/1000)
    e_tl  = f_linear_z(f_y/1000)
    phi_1 = 0.75 + 0.15 * (net_tens_e - e_cl) / (e_tl - e_cl)

    phi_2 = min(max(0.75, phi_1),0.9)

    return phi_2, e_cl, e_tl
    
def str_fun_1(string_r, var_1, string_l, dim_unt):
    st.latex(rf"\text{{{string_r}}} {var_1} = {string_l}\;\text{{{dim_unt}}}")


def str_fun_2(string_r, var_1, string_l, numer_1, dim_unt):
    html_str = f"""
    $$
    \\begin{{align}}
    \\text{{{string_r}}} {var_1} &= {string_l} \ { dim_unt} \\\\
    \\ &= {numer_1} \ {dim_unt} 
    \\end{{align}}
    $$
    """
    return HTML(html_str)

def eq_3(lhs_1, var_1, rhs_1, rhs_2, rhs_3, dim_unt):
        st.latex(rf"\text{{{lhs_1}}} {var_1} = {rhs_1}\;\text{{{""}}}")
        st.latex(rf" = {rhs_2}")
        st.latex(rf" = {rhs_3}\;{dim_unt}")

def str_fun_3(string_r, var_1, string_l, numer_1, numer_2, dim_unt):
    st.latex(rf"""
    \begin{{align*}}
    \text{{{string_r}}} {var_1} &= {string_l} \\
    &= {numer_1} \\
    &= {numer_2}\;\text{{{dim_unt}}}
    \end{{align*}}
    """)


def frac(numer, denom):
    return f"\\frac{{{numer}}}{{{denom}}}"

def head_1(string_r, var_1):
    html_str = f"""
    $$
    \\begin{{align}}
    \\text{{{string_r}}} \\ {var_1}
    \\end{{align}}
    $$
    """
    return HTML(html_str)
    
def range_1(rhs_1, lhs_1, var_1):
    st.latex(rf"{rhs_1}  \leq {var_1} \leq {lhs_1}")

def range_2(lhs_1, var_1):
    st.latex(rf"{lhs_1}  \leq {var_1}")

def clause_1(str_1):
    st.latex(rf"\hspace{{2.5cm}}\text{{{str_1}}}")

def header_1(indx_1, str_1):
    st.markdown(f"**{indx_1}. {str_1}**")
    st.markdown("---")


def line_1():
    html_content = f"""
    <hr>
    """
    display(HTML(html_content))

def beam_dim_1(width, depth):
    header_1("1", "Beam Dimensions")
    str_fun_1("Beam width, ", "b", width, "in")
    str_fun_1("Beam depth, ", "d", depth, "in")

def rein_prop_1(bar_nos, bar_dia, bar_area):
    header_1("2", "Reinforcement Properties")
    str_fun_1("Number of rebars, ", "N_{bars}", bar_nos, "No's")
    str_fun_1("Diameter of rebar, ", "d_{bar}", bar_dia, "in")
    fract   = frac("\\pi", 4)
    rhs_1   = r"{N_{bars}} \cdot \frac{\pi}{4} \cdot {d_{bar}}^{2}"
    rhs_2   = f"{bar_nos} \\cdot {fract} \\cdot {bar_dia}^{{2}}"
    rhs_3   = bar_area
    lhs_1   = "Area of rebars, "
    var_1   = "A_{s}"
    dim_unt = r"{in^{2}}"
    eq_3(lhs_1, var_1, rhs_1, rhs_2, rhs_3, dim_unt)

def mat_prop_1(f_y, f_c, beta_1):
    header_1("3", "Material Properties")
    str_fun_1("Stress in tension reinforcement at nominal flexural resistance, ", "f_{s}", f_y/1000, "ksi")
    str_fun_1("Compressive strength of concrete at 28 days, ", "f'_{c}", f_c/1000, "ksi")

def stress_block_b1(f_c, beta_1):
    header_1("4", "Stress Block Factor, $\\beta_{1}$")
    if f_c >= 2500 and f_c <= 4000:
        string_r  = "stress block factor, "
        var_1     = "\\beta_{1}"
        string_l  = f"{beta_1}"
        dim_unt   = ""
        range_1(2.5, 4.0, "f'_{c}")
        str_fun_1(string_r, var_1, string_l, dim_unt)
    if f_c > 4000 and f_c < 8000:
        string_r = "stress block factor, "
        var_1    = "\\beta_{1}"
        str_eq   = "0.85 - 0.05 \\cdot ( \ f_{c} - 4 \ )"
        numer_1  = f"0.85 - 0.05 \\cdot ( \ {f_c/1000} - 4 \ )"
        string_l = beta_1
        range_1(4.0, 8.0, "f'_{c}")
        str_fun_3(string_r, var_1, str_eq, numer_1, round(string_l,2), "")
    if f_c >= 8000:
        range_2(8.0, "f'_{c}")
        string_r  = "stress block factor, "
        var_1     = "\\beta_{1}"
        string_l  = f"{beta_1}"
        dim_unt   = ""        
        str_fun_1(string_r, var_1, string_l, dim_unt)
    clause_1("[Clause 5.6.2.2 page : 5-38 to 5-39]")

def stress_block_a1(alpha_1, f_c):
    header_1("5", "Stress Block Factor, $\\alpha_{1}$")
    if f_c <= 10000:
        range_2("f'_{c}", 10)
        string_r  = "stress block factor, "
        var_1     = "\\alpha_{1}"
        string_l  = f"{alpha_1}"
        dim_unt   = ""
        str_fun_1(string_r, var_1, string_l, dim_unt)
    if f_c > 10000:
        range_2(10.0, "f'_{c}")
        string_r = "stress block factor, "
        var_1    = "\\alpha_{1}"
        str_eq   = "0.85 - 0.02 \\cdot ( \ f_{c} - 10 \ )"
        numer_1  = f"0.85 - 0.02 \\cdot ( \ {f_c/1000} - 10 \ )"
        string_l = alpha_1
        str_fun_3(string_r, var_1, str_eq, numer_1, round(string_l,2), "")
    clause_1("[Clause 5.6.2.2 page : 5-38 to 5-39]")

def eq_stress_block_depth(cov_eff, e_cu, depth, bar_area, f_y, alpha_1, f_c, beta_1, width, d_comp, d_na):
    header_1("6", "Depth of Equivalent Stress Block")
    str_fun_1("Effective cover, ", "d_{c}", cov_eff, "in")
    str_fun_1("Strain at the extreme concrete compression fiber, ", "\\varepsilon_{cu}", e_cu, "")
    clause_1("[Clause 5.6.2.1 page : 5-36 to 5-37]")
    str_fun_2("Effective depth, ", "d_{s}", str(depth) + "-" + str(cov_eff ), depth - cov_eff, "in")
    str_eq  = "\\frac{A_{s} \ f_{s}}{ \\alpha_{1} \ f'_{c} \ \\beta_{1} \ b}"
    numer_1 = f"\\frac{{{bar_area} \\cdot {f_y/1000}}}{{ {alpha_1} \\cdot {f_c/1000} \\cdot {beta_1} \\cdot {width}}}"
    str_fun_3("Distance from extreme compression fiber to the neutral axis, ", "c", str_eq, numer_1, round(d_comp/beta_1,2), "in")
    clause_1("[Clause 5.6.3.1.1-4 page : 5-39 to 5-40]")
    str_eq  = "c \\cdot \\beta_{1}"
    numer_1 = f"{d_na:.2f} \\cdot {beta_1}"
    str_fun_3("Depth of the equivalent stress block, ", "a", str_eq, numer_1, round(d_comp,2), "in")
    clause_1("[Clause 5.6.2.2 page : 5-38 to 5-39]")

def nom_flex_resist(bar_dia, f_y, eff_depth, d_comp, M_nom):
    header_1("7", "Nominal Flexural Resistance")
    str_eq  = "A_{s} \\cdot f_{s} \\cdot \\left( d_{s} - \\frac{a}{2} \\right)"
    numer_1 = f"{bar_dia} \\cdot {f_y/1000} \\cdot \\left( {eff_depth} - \\frac{{{round(d_comp,2)}}}{2} \\right)"
    str_fun_3("Nominal flexural resistance, ", "M_{n}", str_eq, numer_1, round(M_nom,2), "kips-in")
    clause_1("[Clause 5.6.3.2.2-1 page : 5-42 to 5-43]")


def resist_red_fact(eff_depth, d_na, e_cu, net_tens_e, f_y, e_cl, e_tl):
    header_1("8", "Resistance Reduction Factor")
    str_eq = "\\varepsilon_{cu} \\cdot \\frac{ \\left( d_{s} - c \\right)}{c}"
    numer  = f"{eff_depth} - {round(d_na,2)}"
    denom  = f"{round(d_na,2)}"
    fract  = f"{e_cu} \\cdot \\left( {frac(numer, denom)} \\right)"
    str_fun_3("Net tensile strain , ", "\\varepsilon_{t}", str_eq, fract, round(net_tens_e,5), "")
    clause_1("[Clause 5.6.2.1 page : 5-36 to 5-37]")
    x        = np.array([60, 75, 80, 100]) #ksi
    y        = np.array([0.002, 0.0028, 0.003, 0.004])
    z        = np.array([0.005, 0.005, 0.0056, 0.008])
# Create a linear interpolating function
    f_linear_y = interp1d(x, y, kind='linear', bounds_error=False, fill_value=(y.min(), y.max()))
    f_linear_z = interp1d(x, z, kind='linear', bounds_error=False, fill_value=(z.min(), z.max()))
# Evaluate at new points
    e_cl  = f_linear_y(f_y/1000)
    e_tl  = f_linear_z(f_y/1000)
    phi_1 = 0.75 + 0.15 * (net_tens_e - e_cl) / (e_tl - e_cl)

    phi_2 = min(max(0.75, phi_1),0.9)

    string_r = "compression-controlled strain limit, "
    var_1    = "\\varepsilon_{cl}"
    str_fun_1(string_r, var_1, e_cl, "")
    string_r = "tension-controlled strain limit, "
    var_1    = "\\varepsilon_{tl}"
    str_fun_1(string_r, var_1, e_tl, "")
    clause_1("[Table C5.6.2.1-1 page : 5-38]")

    string_r = "Resistance reduction factor, "
    var_1    = "\\phi"
    numer    = "\\varepsilon_{t} - \\varepsilon_{cl}"
    denom    = "\\varepsilon_{tl} - \\varepsilon_{cl}"
    fract_1  = frac(numer, denom)
    str_eq   = f"0.75 + 0.15 \\cdot {fract_1}"
    
    numer    = f"{round(net_tens_e,5)} - {np.round(e_cl,5)}"
    denom    = f"{np.round(e_tl,5)} - {np.round(e_cl,5)}"
    fract_1  = frac(numer, denom)
    numer_1  = f"0.75 + 0.15 \\cdot {fract_1}"

    string_l = phi_1

    str_fun_3(string_r, var_1, str_eq, numer_1, round(string_l,2), "")

    if phi_1 < 0.75:
        range_2(round(phi_1,2), 0.75)
    if phi_1 > 0.75 and phi_1 < 0.9:
        range_1(0.75, 0.9, round(phi_1,2))
    if phi_1 > 0.9:
        range_2(0.9, round(phi_1,2))

    clause_1("[Clause 5.5.4.2-2 page : 5-34]")

    string_r = "Resistance reduction factor, "
    var_1    = "\\phi"
    str_fun_1(string_r, var_1, round(phi_2,2), "")

def fact_flex_resist(str_red_fact, M_nom):
    header_1("9", "Factored Flexural Resistance")
    M_r     = str_red_fact * M_nom
    str_eq  = "\\phi \\cdot M_{n}"
    numer_1 = f"{round(str_red_fact,2)} \\cdot {round(M_nom,2)}"
    str_fun_3("Factored flexural resistance, ", "M_{r}", str_eq, numer_1, round(M_r,2), "kips-in")
    clause_1("[Clause 5.6.3.2.1-1 page : 5-42]")
    line_1()

# Do operations on stored data
e_cu         = 0.003                            # ultimate compressive strain in concrete
eff_depth    = depth - cov_eff                  # (in)
bar_area     = round((bar_nos * np.pi * bar_dia**2/4),2) # (in^2)
beta_1       = beta_1_calc(f_c)
alpha_1      = alpha_1_calc(f_c)
d_comp       = bar_area * f_y / (alpha_1 * f_c * width) # (in) depth of equivalent rectangular stress block
d_na         = d_comp/beta_1 # (in)
d_na_ratio   = d_na/eff_depth 
M_nom        = bar_area * f_y * (eff_depth - d_comp/2) * 0.001 # (kips-in)
net_tens_e   = e_cu * (eff_depth - d_na)/d_na
str_red_fact, e_cl, e_tl = str_red_fact_calc(net_tens_e, f_y)
M_cap        = str_red_fact * M_nom # (kips-in)
# display HTML
beam_dim_1(width, depth)
rein_prop_1(bar_nos, bar_dia, bar_area)
mat_prop_1(f_y, f_c, beta_1)
stress_block_b1(f_c, beta_1)
stress_block_a1(alpha_1, f_c)
eq_stress_block_depth(cov_eff, e_cu, depth, bar_area, f_y, alpha_1, f_c, beta_1, width, d_comp, d_na)
nom_flex_resist(bar_dia, f_y, eff_depth, d_comp, M_nom)
resist_red_fact(eff_depth, d_na, e_cu, net_tens_e, f_y, e_cl, e_tl)
fact_flex_resist(str_red_fact, M_nom)
