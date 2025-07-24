# B2G-22-001 signal interpolation

Signal interpolation based on the method laid out in Section 11.2 of `references/AN2020_159_v14.pdf`.

The general idea is to fit each signal mass point with a product of double-sided crystal ball (DSCB) functions. The parameter values recovered from the fit will be written to a CSV file. These parameter values will be linearly interpolated to obtain the values to generate signal mass points in between existing signal masses.

# Running interpolation

1. Run `python FitAllShapes.py` to generate the fit shapes for all signals for 16, 16APV, 17, and 18 with systematics.
    * If needed, fit individual shapes with `python FitShape.py -s <mT>-<mPhi> -y <year>` to determine per-signal initial parameter values.
2. Run `python GetYields.py` to save out the yields of all signals for all years. The yields are used for the interpolation in the next step. 
3. After generating the fit shapes for all signals and all years, run `python InterpolateShapes.py`
    * Either have the script automatically determine the existing signals between which to interpolate via `-m <interpolated mass> -mT <Tprime mass> -y <year>`
    * or provide them manually: `-m <interpolated mass> -m1 <existing m1> -m2 <existing m2> -mT <Tprime mass> -y <year>`
    * This can be run automatically for all signals and years with `./InterpolateShapes.sh`
    * this will freak out on the LPC, do it locally instead. Better: write condor job for it 

# Plotting the results

* Run `PlotGeneratedVsExisting.py` to plot the results after running the full interpolation process. The generated and existing signals for all phi masses associated with mT=3000 will be plotted, where the phi masses have been shifted by 50 GeV in order to avoid overcrowding.
* Run `CompareGeneratedVsExisting.py` to plot the comparison of the generated vs interpolated signals for the *already-existing* signals. This requires that you have generated the interpolated signals for the existing ones already. The existing phi masses are `[75, 100, 125, 175, 200, 250, 350, 450, 500]`

# Fitting

